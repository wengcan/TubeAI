from enum import Enum
import os,uuid
from typing import List,Tuple
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
from langchain.chains import LLMChain
from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain
     

from src.utils import chromadb_path, safety_settings
from .Doctype import Doctype

class MyLangChain:
    __llm = None
    __persistent_client = None

    __store = None

    __splitters = []

    def __init__(self) -> None:
        self.__llm = ChatGoogleGenerativeAI(model="gemini-pro", safety_settings=safety_settings)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=5000, 
            chunk_overlap=0
        )
        self.child_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=0
        )      
        self.__splitters = [self.text_splitter, self.child_text_splitter] 
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
    
    def __create_documents(self,  document_type: Doctype,  docs:  List[str]) -> Tuple[List[str], List[Document]]:
        doc_ids = [str(uuid.uuid4()) for _ in docs]
        documents = self.__splitters[document_type.value].create_documents(
            texts= docs,
            metadatas= [
                {
                    'doc_id': doc_id,
                    'index': id,
                    'doc_type': document_type.value
                } for id, doc_id in enumerate(doc_ids)
            ]
        )
        return (doc_ids, documents)
    def __save(self, collection_name: str,  doc_ids: List[str] , full_documents:List[Document]) -> None:
        retriever =self.__get_retriever(collection_name, id_key= 'doc_id')
        retriever.vectorstore.add_documents(full_documents)
        retriever.docstore.mset(list(zip(doc_ids, full_documents)))
    def save_text_to_vectorstore(self, collection_name: str, text: str) -> List[str]:
        if collection_name != "" and text != "":
            docs = self.text_splitter.split_text(text)
            documents = []
            self.__merge_documents(docs, documents)
        
            # doc_ids = [str(uuid.uuid4()) for _ in docs]
            # id_key= 'doc_id'
            # full_documents = [
            #     Document(
            #         page_content=page_content,
            #         metadata={
            #             id_key: doc_ids[index], 
            #             'doc_type':  Doctype.full
            #         }
            #     ) for index, page_content in enumerate(documents)
            # ]

            doc_ids, full_documents = self.__create_documents(document_type=Doctype.full, docs= docs)
            self.__save(collection_name, doc_ids=doc_ids, full_documents= full_documents)
            
    def __merge_documents(self, documents: List[str], new_documents: List[str] = [] ) -> None:
        max_tokens = 30000
        temp = "".join(documents)        
        if  int(self.__llm.client.count_tokens(temp).total_tokens) < max_tokens:
            if temp != "":
                new_documents.append(temp)
            return
        else:
            n = len(documents) 
            half_n = n // 2
            self.__merge_documents(documents[0:half_n], new_documents)
            self.__merge_documents(documents[half_n:n], new_documents)                

    def chat(self, collection_name:  str, prompt: str, refine_prompt, lang: str):
        collection = self.get_collection(collection_name=collection_name)
        result = collection.get(
            where={"doc_type": Doctype.full.value}
        )
        documents = result.get("documents")

        print(documents)

        chain = (
            {"doc": lambda x : x}
            | PromptTemplate.from_template(prompt)
            | self.__llm
            | StrOutputParser()
        )
        temp = chain.batch(documents, {"max_concurrency": 5})

        llm_chain = LLMChain(llm=self.__llm, prompt=PromptTemplate(
            input_variables=["existing_answer", "text", "lang"],
            template=refine_prompt
        ))

        res = llm_chain.invoke({
            "existing_answer": temp,
            "text": "",
            "lang": lang
        })

        return res.get("text")

   
    # def qa(self, collection_name: str, question: str)-> None:
    #     id_key = 'doc_id'
    #     template = (
    #         "Use the following pieces of context to answer the question at the end. \n"
    #         "If you don't know the answer, just say that you don't know, don't try to make up an answer.\n" 
    #         "Use three sentences maximum. Keep the answer as concise as possible. \n" 
    #         "Always say \"thanks for asking!\" at the end of the answer."
    #         "------------\n"
    #         "{context}\n"
    #         "------------\n"            
    #         "Question: {question}"
    #         "Helpful Answer:"
    #     )
    #     retriever =self.__get_retriever(collection_name, id_key= id_key)
    #     result = retriever.vectorstore.similarity_search(question)
    #     QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    #     qa_chain = RetrievalQA.from_chain_type(
    #         ChatGoogleGenerativeAI(model="gemini-pro", safety_settings=safety_settings),
    #         retriever=retriever.vectorstore.as_retriever(),
    #         return_source_documents=True,
    #         chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    #     )
    #     result = qa_chain.invoke({"query": question})
    #     return result["result"]