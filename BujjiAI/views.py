from rest_framework.views import APIView
import os
import pandas as pd
import json
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from django.conf import settings
from rest_framework.response import Response
import logging
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from django.utils import timezone


bujjiAI_logger = logging.getLogger('BujjiAI')

embeddings = OpenAIEmbeddings(model=settings.EMBEDDINGS_MODEL)
VECTOR_DB = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")
MEMORY = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )


class UploadCsvToVectorView(APIView):
    def dispatch(self, request, *args, **kwargs):
        self.status = 200
        self.message = "Success"
        self.api_data = None
        self.json_response = {'data': self.api_data, 'message': self.message}
        self.now = timezone.localtime(timezone.now())
        return super().dispatch(request, *args, **kwargs)
    
    def prepare_docs(self):
        df = pd.read_csv(self.csv_file)
        self.docs = []

        for _, row in df.iterrows():
            content = json.dumps(dict(row.items()))
            self.docs.append(Document(page_content=content))

        bujjiAI_logger.info('Dataframe reading successful')

    def build_api_response(self):
        self.prepare_docs()

        vectordb = Chroma(persist_directory=settings.PERSIST_DIRECTORY, embedding_function=embeddings)
        vectordb.add_documents(self.docs)

    def validate_and_parse_input(self):
        self.csv_file = self.request.data.get('csv_file')
        self.source = self.request.data.get('source', 'unknown')
        self.title = self.request.data.get('title', 'Dairy')
        self.category = self.request.data.get('category', 'General')
        self.date = self.request.data.get('date', self.now.date())
        self.type = 'csv'

        if not self.csv_file:
            self.message = 'Csv file is required'
            self.status = 400

    def post(self, *args, **kwargs):
        try:
            self.validate_and_parse_input()
    
            if self.status == 200:
                self.build_api_response()
                self.json_response["data"] = self.api_data
    
        except Exception as err:
            bujjiAI_logger.error(err.args[0] if err.args else 'Something gone wrong')
            self.message = 'Internal server error'
            self.status = 500

        self.json_response['message'] = self.message
        return Response(self.json_response, status=self.status)


class UploadPdfToVectorView(UploadCsvToVectorView):
    def validate_and_parse_input(self):
        self.pdf_file = self.request.FILES.get('pdf_file')
        self.source = self.request.data.get('source', 'unknown')
        self.title = self.request.data.get('title', 'Dairy')
        self.category = self.request.data.get('category', 'General')
        self.date = self.now.date().strftime('%Y-%m-%d')
        self.type = 'pdf'

        if not self.pdf_file:
            self.message = 'Pdf file is required'
            self.status = 400

    def prepare_docs(self):
        text = ""
        reader = PdfReader(self.pdf_file)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if text:
            documents = [
                Document(
                    page_content=text,
                    metadata={
                        "source": self.source,
                        "title": self.title,
                        "category": self.category,
                        "date": self.date,
                        "type": self.type
                    })
            ]

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            self.docs = text_splitter.split_documents(documents)
            bujjiAI_logger.info('Pdf reading successful')
        else:
            self.message = 'There is no text in this file'
            self.status = 400


class AskBujjiView(APIView):
    def dispatch(self, request, *args, **kwargs):
        self.status = 200
        self.message = "Success"
        self.api_data = None
        self.json_response = {'data': self.api_data, 'message': self.message}
        return super().dispatch(request, *args, **kwargs)
        
    def build_api_response(self):
        retriever = VECTOR_DB.as_retriever(search_kwargs={"k": 3})
        llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0)

        # prompt = ChatPromptTemplate.from_messages([
        #             ("system", "Call me Boss. You are a helpful assistant. If you don't know the answer, tell that you don't know"),
        #             ("human", "Context:\n{context}\n\nQuestion: {input}")
        #         ])

        # document_chain = create_stuff_documents_chain(llm, prompt)
        # retrieval_chain = create_retrieval_chain(retriever, document_chain)
        qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=MEMORY,
        combine_docs_chain_kwargs={
            "prompt": ChatPromptTemplate.from_messages([
                ("system", "I am your Boss. You are my helpful assistant."),
                ("human", "Chat history:\n{chat_history}\n\nContext:\n{context}\n\nQuestion: {question}")
            ])
        }
    )
        response = qa_chain.invoke({"question": self.query})

        self.api_data = response["answer"]

    def validate_and_parse_input(self):
        self.query = self.request.data.get('query')

        if not self.query:
            self.message = "Query is needed"
            self.status = 400

    def post(self, *args, **kwargs):
        try:
            self.validate_and_parse_input()

            if self.status == 200:
                self.build_api_response()
                self.json_response["data"] = self.api_data

        except Exception as err:
            bujjiAI_logger.error(err.args[0] if err.args else 'Something gone wrong')
            self.message = 'Internal server error'
            self.status = 500

        self.json_response['message'] = self.message
        return Response(self.json_response, status=self.status)