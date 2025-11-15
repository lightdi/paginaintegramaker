from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings

from langchain_chroma import Chroma


    # ---------------------------------------------
    # CONFIGURAÇÃO DO OLLAMA (IMPORTANTE)
    # ---------------------------------------------
    # Dentro do Docker, você *não pode* usar localhost.
    # Então apontamos para o host do Docker (normalmente 172.17.0.1).
    # Ajuste se necessário.
OLLAMA_URL = "http://localhost:11434"


    # ---------------------------------------------
    # MODELO OLLAMA
    # ---------------------------------------------
llm = ChatOllama(
    model="qwen2.5:0.5b",
    temperature=0,
    base_url="http://200.129.71.149:11434",
)


# ---------------------------------------------
# EMBEDDINGS
# ---------------------------------------------
#embeddings = HuggingFaceEmbeddings(
#    model_name="sentence-transformers/all-mpnet-base-v2"
#)
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://200.129.71.149:11434",
)



# ---------------------------------------------
# CHROMA VECTOR DB
# ---------------------------------------------
vector_store = Chroma(
    collection_name="ifchat_docs",
    embedding_function=embeddings,
    persist_directory="./chroma_data"
)


# ---------------------------------------------
# RETRIEVER (SEM TOOLS)
# ---------------------------------------------
def retrieve_context(query: str):
    """Retorna os documentos relevantes do Chroma."""
    retrieved_docs = vector_store.similarity_search(query, k=1)
    serialized = "\n\n".join(
        f"Fonte: {doc.metadata}\nConteúdo: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized


# ---------------------------------------------
# ASK_RAG (fluxo principal do RAG)
# ---------------------------------------------
def ask_rag(question: str):

    context = retrieve_context(question)

    prompt = f"""
    Você é o Assistente Virtual Oficial do IFPB, treinado para auxiliar
    alunos, servidores, coordenadores e professores.

    Sua missão é responder SOMENTE com informações presentes no contexto
    fornecido. Não utilize conhecimento externo, inferências não justificadas
    ou suposições.

    ================== CONTEXTO ==================
    {context}
    ================================================

    Pergunta do usuário:
    {question}

    ==================== REGRAS ====================
    1. Responda de forma objetiva, clara e educada.
    2. Use APENAS as informações do contexto acima.
    3. Se houver múltiplas fontes no contexto, consolide sem inventar.
    4. NÃO responda nada que não esteja no contexto.
    5. Se as informações forem insuficientes, responda:
    "Não encontrei informações suficientes sobre isso nas fontes consultadas."
    6. Caso o contexto inclua links ou documentos, finalize com:
    "📚 Leia mais"
    7. Não adicione opiniões pessoais, previsões ou informações externas.
    8. Mantenha linguagem apropriada ao ambiente institucional do IFPB.
    ================================================

    Agora produza a melhor resposta possível seguindo todas as regras.
    """

    response = llm.invoke(prompt)
    return response.content


#print(llm.invoke("oie"))

print(ask_rag("Como é o processo para receber o doploma?"))