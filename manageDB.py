from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.agents import create_agent
from langchain.tools import tool


TELEGRAM_TOKEN="8396320863:AAE2gcTlMhb-Xj5WEApaF8SrdBL0ls-_TmY"
WEBHOOK_URL= "https://fearless-ellsworth-obsessional.ngrok-free.dev/telegram/webhook"
API_KEY="AIzaSyDyI-EC9VxdPGCJDfs1Hls8kOFoCDHGpeU"


#Iniciando a concexão com o Geminai
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0, # o qual criativo ele pode ser
    api_key=API_KEY
)

#Iniciando os embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

#Iniciando o ChormaDB
vector_store = Chroma(
    collection_name="ifchat_docs",
    embedding_function=embeddings,
    persist_directory="./chroma_data"
)


#Procurar respresentividade
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
    "- Sempre inclua ao final uma seção “📚 Leia mais” com os links citados nas fontes (se disponíveis).\n"
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
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    print(result["messages"])
    msgs = result["messages"]
  
   # pega a última mensagem útil (normalmente index 3 ou 1)
    raw = msgs[3].content if len(msgs) > 2 else msgs[1].content

    # limpa e extrai só o texto
    return extrair_texto(raw)


