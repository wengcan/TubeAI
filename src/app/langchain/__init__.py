import os,uuid
from typing import List
import chromadb
import google.generativeai as genai
from langchain.storage import InMemoryByteStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.prompts import ChatPromptTemplate,PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA


from src.utils import chromadb_path, safety_settings

class MyLangChain:
    __persistent_client = None

    __store = None
    def __init__(self) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=20)
        self.child_text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=20)        
        self.__store = InMemoryByteStore()
        self.__persistent_client = chromadb.PersistentClient(path=chromadb_path)
    def get_collection(self, collection_name:  str) -> chromadb.Collection | None:
        try:
            return self.__persistent_client.get_collection(collection_name)
        except:
            return None
        
    def __get_retriever(self, collection_name:  str, id_key: str) -> MultiVectorRetriever:
        vectorstore = Chroma(
            client=self.__persistent_client,
            collection_name= collection_name,
            embedding_function=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
            # persist_directory=chromadb_path
        )
        return  MultiVectorRetriever(
            vectorstore=vectorstore,
            docstore=self.__store,
            id_key=id_key,
        )
    def __save_to_vectorstore(self, collection_name: str, document_type: str, docs:  List[str]) -> None:
        retriever =self.__get_retriever(collection_name, id_key= 'doc_id')
        doc_ids = [str(uuid.uuid4()) for _ in docs]
        sub_docs = self.child_text_splitter.create_documents(
            texts=docs, 
            metadatas=[
                {
                    'doc_id': doc_id,
                    'doc_type': document_type
                } for doc_id in doc_ids
            ]
        )
        retriever.vectorstore.add_documents(sub_docs)
        retriever.docstore.mset(list(zip(doc_ids, docs)))
    def save_text_to_vectorstore(self, collection_name: str, text: str) -> List[str]:
        if collection_name != "" and text != "":
            docs = self.text_splitter.split_text(text)
            self.__save_to_vectorstore(collection_name=collection_name, document_type = 'raw', docs=docs)
    def document_chat(self, collection_name:  str, template: str):
        collection = self.get_collection(collection_name=collection_name)
        result = collection.get(
            where={"doc_type": "summary"}
        )
        chain = (
            {"doc": lambda x: x}
            | ChatPromptTemplate.from_template(f"{template}" + " :\n\n{doc}")
            | ChatGoogleGenerativeAI(model="gemini-pro", safety_settings=safety_settings)
            | StrOutputParser()
        )
        return chain.batch(result.get("documents"), {"max_concurrency": 5})
    def document_qa(self, collection_name: str, question: str)-> None:
        id_key = 'doc_id'
        template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" at the end of the answer.
            {context}
            Question: {question}
            Helpful Answer:"""
        retriever =self.__get_retriever(collection_name, id_key= id_key)
        result = retriever.vectorstore.similarity_search(question)
        QA_CHAIN_PROMPT = PromptTemplate.from_template(template)# Run chain
        qa_chain = RetrievalQA.from_chain_type(
            ChatGoogleGenerativeAI(model="gemini-pro", safety_settings=safety_settings),
            retriever=retriever.vectorstore.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )
        result = qa_chain.invoke({"query": question})
        return result["result"]