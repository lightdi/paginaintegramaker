import chromadb
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ----------------------------
# Inicialização do Chroma
# ----------------------------

client = chromadb.PersistentClient(path="./chroma_data")

# Correção: adicionar parênteses!
embedding_function = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="ifchat_docs",
    embedding_function=embedding_function
)


# ----------------------------
# Função: adicionar PDF chunk a chunk
# ----------------------------
def add_document(path: str):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30
    )

    try:
        # Carregar arquivo PDF
        loader = PyMuPDFLoader(path)
        docs = loader.load()

        # Gerar chunks
        chunks = splitter.split_documents(docs)

        for i, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk.page_content],
                metadatas=[{
                    "source": path,
                    "page": chunk.metadata.get("page"),
                    "chunk": i
                }],
                ids=[f"{path}_chunk_{i}"]
            )

        print(f"Documento {path} adicionado ({len(chunks)} chunks).")

    except Exception as e:
        print(f"Erro ao carregar arquivo {path}: {e}")


# ----------------------------
# Busca por similaridade
# ----------------------------
def search_similar(query: str):
    return collection.query(
        query_texts=[query],
        n_results=3
    )
