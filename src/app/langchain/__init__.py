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
    __vectorstore = None
    __store = None
    COLLECTION_NAME = "yt_documents"
    def __init__(self) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=20)
        self.child_text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=20)        
        self.__store = InMemoryByteStore()

        self.__vectorstore = Chroma(
            collection_name= MyLangChain.COLLECTION_NAME,
            embedding_function=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
            persist_directory=chromadb_path
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
    def add_documents(self, id_key: str, text: str) -> List[str]:
        if id_key != "" and text != "":
            docs = self.text_splitter.split_text(text)
            self.save_to_vectorstore(id_key=id_key, docs=docs)
            chain = (
                {"doc": lambda x: x}
                | ChatPromptTemplate.from_template("Summarize the following document:\n\n{doc}")
                | ChatGoogleGenerativeAI(model="gemini-pro", safety_settings=safety_settings)
                | StrOutputParser()
            )
            summaries = chain.batch(docs, {"max_concurrency": 5})
            self.save_to_vectorstore(id_key=f'{id_key}/summaries', docs=summaries)
            return summaries
    def document_qa(self, id_key: str, question: str)-> None:
        template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" at the end of the answer.
            {context}
            Question: {question}
            Helpful Answer:"""
        retriever = MultiVectorRetriever(
            vectorstore=self.__vectorstore,
            docstore=self.__store,
            id_key=id_key,
        )
        QA_CHAIN_PROMPT = PromptTemplate.from_template(template)# Run chain
        qa_chain = RetrievalQA.from_chain_type(
            ChatGoogleGenerativeAI(model="gemini-pro", safety_settings=safety_settings),
            retriever=retriever.vectorstore.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )
        result = qa_chain.invoke({"query": question})
        print(result)
        return result["result"]
    # def query_documents(self,id_key: str) -> any:
    #     print(id_key)
    #     return self.__vectorstore.get()