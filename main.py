# Configurações de Telemetria (para limpar o log)
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import os
import shutil
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# --- IMPORTAÇÕES CORRIGIDAS ---
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_mistralai import ChatMistralAI
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
# ------------------------------

# Carregar variáveis
load_dotenv()
TARGET_URL = os.getenv("TARGET_URL")
API_KEY = os.getenv("AI_KEY")

if API_KEY:
    print(f"DEBUG: Chave carregada: {API_KEY[:5]}... (Tamanho: {len(API_KEY)})")
else:
    print("DEBUG: ERRO CRÍTICO - Nenhuma chave encontrada na variável AI_KEY")
# ---------------------------------

# Configurações do Crawler
MAX_DEPTH = 2 

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.decompose()
    text = soup.get_text(separator="\n")
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def main():
    if not TARGET_URL or not API_KEY:
        print("ERRO: Verifique se o .env tem TARGET_URL e AI_KEY")
        return

    persist_directory = "./chroma_db"

    # Verifica se o banco já existe
    db_exists = os.path.exists(persist_directory) and len(os.listdir(persist_directory)) > 0

    print(f"--- Iniciando sistema HÍBRIDO para URL: {TARGET_URL} ---")
    print("(Embeddings: Local/HuggingFace | Chat: Mistral API)")

    # 1. Configurar Embeddings LOCAIS (Roda na CPU do Docker)
    # O modelo 'all-MiniLM-L6-v2' é leve, rápido e excelente para inglês/código.
    print("-> Carregando modelo de embeddings local (pode demorar um pouco na 1ª vez)...")
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if not db_exists:
        print(f"-> Iniciando CRAWLER RECURSIVO (Profundidade: {MAX_DEPTH})...")

        loader = RecursiveUrlLoader(
            url=TARGET_URL,
            max_depth=MAX_DEPTH,
            extractor=clean_html, 
            prevent_outside=True 
        )

        raw_docs = loader.load()
        print(f"-> Páginas baixadas: {len(raw_docs)}")

        if len(raw_docs) == 0:
            print("ERRO: Nenhuma página baixada. Verifique a URL.")
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(raw_docs)
        print(f"-> Documentos divididos em {len(splits)} pedaços.")

        print("-> Criando Banco Vetorial Local (ChromaDB)...")
        # Como é local, podemos mandar tudo de uma vez (sem limite de taxa)
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embedding_function,
            persist_directory=persist_directory
        )
        print("-> Banco de dados criado com sucesso!")
    else:
        print("-> Banco de dados encontrado! Carregando...")
        vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)

    # 2. Configurar o Chat (MISTRAL)
    retriever = vectorstore.as_retriever()
    llm = ChatMistralAI(model="mistral-tiny", temperature=0, api_key=API_KEY)

    system_prompt = (
        "Você é um assistente especialista baseado na documentação extraída."
        "Use o contexto abaixo para responder. Se não souber, diga que não sabe."
        "\n\nContexto:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    print("\n\n=== CHATBOT PRONTO (Digite 'sair' para encerrar) ===")
    while True:
        try:
            query = input("\nVocê: ")
            if query.lower() in ["sair", "exit"]:
                break
            
            print("Mistral pensando...")
            response = rag_chain.invoke({"input": query})
            print(f"IA: {response['answer']}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()