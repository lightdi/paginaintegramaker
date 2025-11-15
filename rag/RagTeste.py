#from core.config import API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import RecursiveUrlLoader
#Bibliotecas para ler PDF
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.agents import create_agent
from langchain.tools import tool
import re
from html import unescape

API_KEY  = "AIzaSyDyI-EC9VxdPGCJDfs1Hls8kOFoCDHGpeU"
#Iniciando a concexão com o Geminai
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0, # o qual criativo ele pode ser
    api_key=API_KEY
)



embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

#Iniciando o ChormaDB
vector_store = Chroma(
    collection_name="ifchat_docs",
    embedding_function=embeddings,
    persist_directory="./chroma_data"
)


def criar_base_documentos():

    docs = []

    for n in Path("./documentos").glob("*.pdf"):
        try:
            loader = PyMuPDFLoader(str(n))
            docs.extend(loader.load())
            print(f"Carregado com sucesso arquivo {n.name}")
        except Exception as e:
            print(f"Erro ao carregar arquivo {n.name}: {e}")

    print(f"Total de documentos carregados: {len(docs)}")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # chunk size (characters)
        chunk_overlap=200,  # chunk overlap (characters)
        add_start_index=True,  # track index in original document
    )
    all_splits = text_splitter.split_documents(docs)

    print(f"Split blog post into {len(all_splits)} sub-documents.")

    document_ids = vector_store.add_documents(documents=all_splits)

    print(document_ids[:3])
    print("Finalização da base")


def criar_base_dados():
    loader = RecursiveUrlLoader(
        "https://sites.google.com/ifpb.edu.br/manualcoordenadorpatos/manual-do-coordenador",
    )

    docs = loader.load()

    print( len(docs))
    print(f"Total characters: {len(docs[0].page_content)}")

    print(docs[0].metadata)

    print(docs[1].metadata)


    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # chunk size (characters)
        chunk_overlap=200,  # chunk overlap (characters)
        add_start_index=True,  # track index in original document
    )
    all_splits = text_splitter.split_documents(docs)

    print(f"Split blog post into {len(all_splits)} sub-documents.")

    document_ids = vector_store.add_documents(documents=all_splits)

    print(document_ids[:3])
    print("Finalização da base")

#criar_base_dados()


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
    "Você é um assistente do coordenadro do IFPB,\n"
    "Responda à pergunta do usuário exclusivamente com base nas informações que \n"
    "Foram recuperadas na base de dados de chromaDB\n"
    "Instruções obrigatórias:\n"
    "- Use **apenas** o que está nas fontes acima.\n"
    "- Se não encontrar informação suficiente, diga:\n"
    "Não encontrei informações suficientes sobre isso nas fontes consultadas.\n"
    "Você pode reformular a pergunta ou consultar o [Manual do Coordenador do IFPB Patos](https://sites.google.com/ifpb.edu.br/manualcoordenadorpatos/manual-do-coordenador).\n"
    "- Sempre inclua ao final uma seção “📚 Leia mais” com os links citados nas fontes (se disponíveis).\n"
    "- Nunca invente ou suponha informações que não estejam nas fontes.\n"
    "Use the tool to help answer user queries."
)
agent = create_agent(llm, tools, system_prompt=prompt)

query = (
    "Como proceder com acompanhameto domiciliar?\n\n"
    ""
)

#for event in agent.stream(
#    {"messages": [{"role": "user", "content": query}]},
#    stream_mode="values",
#):
#    event["messages"][-1].pretty_print()

#result = agent.invoke({"messages": [{"role": "user", "content": query}]})
#print(result["messages"])



#result["messages"][3].content


#criar_base_documentos()