"""
Alternativa usando HuggingFace Pipeline para modelos offline.
Use este arquivo se preferir não usar Ollama.

Para usar, renomeie este arquivo para managedb.py e atualize o main.py
"""

import json
import os
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
from langchain_chroma import Chroma
from transformers import pipeline
from langchain.agents import create_agent
from langchain.tools import tool

# Configuração do modelo HuggingFace
# Modelos recomendados (em português):
# - "pierreguillou/gpt2-small-portuguese"
# - "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# - "neuralmind/bert-base-portuguese-cased"
HF_MODEL = os.getenv("HF_MODEL", "microsoft/DialoGPT-medium")  # Ajuste conforme necessário

print(f"Carregando modelo HuggingFace: {HF_MODEL}...")
print("⚠️ Isso pode demorar alguns minutos na primeira vez (download do modelo)")

# Criar pipeline do HuggingFace
pipe = pipeline(
    "text-generation",
    model=HF_MODEL,
    max_new_tokens=512,
    temperature=0.0,
    device_map="auto",  # Usa GPU se disponível
)

# Criar LLM wrapper do LangChain
llm = HuggingFacePipeline(pipeline=pipe)

#Iniciando os embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

#Iniciando o ChromaDB
vector_store = Chroma(
    collection_name="ifchat_docs",
    embedding_function=embeddings,
    persist_directory="./chroma_data"
)


#Procurar representatividade
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=4)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

tools = [retrieve_context]

prompt = (
    "Você é um assistente do virtual do IFPB,\n"
    "Responda à pergunta do usuário exclusivamente com base nas informações que \n"
    "Foram recuperadas na base de dados de chromaDB\n"
    "Instruções obrigatórias:\n"
    "- Use **apenas** o que está nas fontes acima.\n"
    "- Se não encontrar informação suficiente, diga:\n"
    "Não encontrei informações suficientes sobre isso nas fontes consultadas.\n"
    "Você pode reformular a pergunta ou consultar o site https://www.ifpb.edu.br ou [Manual do Coordenador do IFPB Patos](https://sites.google.com/ifpb.edu.br/manualcoordenadorpatos/manual-do-coordenador).\n"
    "- Sempre inclua ao final uma seção "📚 Leia mais" com os links citados nas fontes (se disponíveis).\n"
    "- Nunca invente ou suponha informações que não estejam nas fontes.\n"
    "Use the tool to help answer user queries."
)
agent = create_agent(llm, tools, system_prompt=prompt)


def extrair_texto(chunk):
    """
    Extrai apenas o texto útil de um chunk vindo do RAG.
    """
    if chunk is None:
        return ""

    # Se for string pura
    if isinstance(chunk, str):
        # tenta converter string JSON
        try:
            data = json.loads(chunk)
            chunk = data
        except:
            return chunk  # string normal

    # Se for lista de objetos [{"type":..., "text":...}]
    if isinstance(chunk, list):
        textos = []
        for item in chunk:
            if isinstance(item, dict):
                if "text" in item:
                    textos.append(item["text"])
                elif "content" in item:
                    textos.append(item["content"])
        return "\n".join(textos).strip()

    # Se for dict único
    if isinstance(chunk, dict):
        if "text" in chunk:
            return chunk["text"].strip()
        if "content" in chunk:
            return chunk["content"].strip()

    return str(chunk)


def ask_rag(question: str):
    """
    Processa uma pergunta usando o RAG e retorna a resposta.
    
    Args:
        question: A pergunta do usuário
        
    Returns:
        str: A resposta gerada pelo RAG
    """
    try:
        result = agent.invoke({"messages": [{"role": "user", "content": question}]})
        print(result["messages"])
        msgs = result["messages"]
      
        # Encontra a última mensagem do assistente (não do sistema)
        raw = None
        for msg in reversed(msgs):
            # Procura por mensagens do assistente ou que tenham conteúdo útil
            if hasattr(msg, 'content') and msg.content:
                # Ignora mensagens vazias ou de sistema
                if isinstance(msg.content, str) and msg.content.strip():
                    raw = msg.content
                    break
                elif isinstance(msg.content, (list, dict)):
                    raw = msg.content
                    break
        
        # Fallback: pega a última mensagem se não encontrou nada
        if raw is None and len(msgs) > 0:
            raw = msgs[-1].content if hasattr(msgs[-1], 'content') else str(msgs[-1])

        # limpa e extrai só o texto
        resposta = extrair_texto(raw)
        
        if not resposta or not resposta.strip():
            return "Desculpe, não consegui gerar uma resposta adequada. Tente reformular sua pergunta."
        
        return resposta
        
    except Exception as e:
        print(f"Erro ao processar pergunta: {e}")
        return f"Erro ao processar sua pergunta. Por favor, tente novamente. Detalhes: {str(e)}"

