import requests
from bs4 import BeautifulSoup
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

index_name = "docs"
embeddings = OpenAIEmbeddings()

vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)

def upload_docs_to_pinecone(): 
    for package_name in open("requirements.txt").readlines():
        package_name = package_name.strip().split("==")[0]
        print(package_name)
        upload_to_pinecone(package_name)

def upload_to_pinecone(package_name):
    url = f"https://pypi.org/project/{package_name}/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    get_text_chunks_langchain(soup.text)

def get_text_chunks_langchain(text):
    text_splitter = CharacterTextSplitter(chunk_size=10000, chunk_overlap=0)
    docs = text_splitter.split_text(text)
    vectorstore.add_texts(docs)

upload_docs_to_pinecone()
