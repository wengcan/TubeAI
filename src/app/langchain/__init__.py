import os,uuid
from typing import List
import chromadb
from langchain.storage import InMemoryByteStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils import data_path

class MyLangChain:
    __vectorstore = None
    __store = None
    __client = None
    COLLECTION_NAME = "yt_documents"
    def __init__(self) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=20)
        self.child_text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=20)        
        self.__store = InMemoryByteStore()
        # self.__client = chromadb.PersistentClient(path=os.path.join(data_path, 'chromadb'))

        self.__vectorstore = Chroma(
            collection_name= MyLangChain.COLLECTION_NAME,
            embedding_function=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
            persist_directory=os.path.join(data_path, 'chromadb')
        )

    def id_exist(self, id: str) -> bool:
        ## TODO check id exist or not
        return False
    def save_to_vectorstore(self,id_key: str, docs:  List[str]) -> None:
        retriever = MultiVectorRetriever(
            vectorstore=self.__vectorstore,
            docstore=self.__store,
            id_key=id_key,
        )
        doc_ids = [str(uuid.uuid4()) for _ in docs]
        sub_docs = self.child_text_splitter.create_documents(texts=docs, metadatas=[{id_key: doc_id} for doc_id in doc_ids])
        retriever.vectorstore.add_documents(sub_docs)
        retriever.docstore.mset(list(zip(doc_ids, docs)))
    def add_documents(self, id_key: str, text: str) -> None:
        if id_key != "" and text != "":
            docs = self.text_splitter.split_text(text)
            self.save_to_vectorstore(id_key=id_key, docs=docs)
            chain = (
                {"doc": lambda x: x}
                | ChatPromptTemplate.from_template("Summarize the following document:\n\n{doc}")
                | ChatGoogleGenerativeAI(model="gemini-pro")
                | StrOutputParser()
            )
            ### TODO add safety_settings
            summaries = chain.batch(docs, {"max_concurrency": 5})
            print(summaries)
            self.save_to_vectorstore(id_key=f'{id_key}/summaries', docs=summaries)
    def query_documents(self,id_key: str) -> any:
        print(id_key)
        return self.__vectorstore.get()