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


bujjiAI_logger = logging.getLogger('BujjiAI')

embeddings = OpenAIEmbeddings(model=settings.EMBEDDINGS_MODEL)
VECTOR_DB = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")


class UploadCsvToVectorView(APIView):
    def dispatch(self, request, *args, **kwargs):
        self.status = 200
        self.message = "Success"
        self.api_data = None
        self.json_response = {'data': self.api_data, 'message': self.message}
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

        vectordb = Chroma.from_documents(self.docs, embedding=embeddings, persist_directory=settings.PERSIST_DIRECTORY)
        vectordb.persist()

    def validate_and_parse_input(self):
        self.csv_file = self.request.data.get('csv_file')

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

        if not self.pdf_file:
            self.message = 'Pdf file is required'
            self.status = 400

    def prepare_docs(self):
        reader = PdfReader(self.pdf_file)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        documents = [Document(page_content=text)]

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.docs = text_splitter.split_documents(documents)

        bujjiAI_logger.info('Pdf reading successful')


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

        prompt = ChatPromptTemplate.from_messages([
                    ("system", "Iam your boss. Call me Boss. You are a helpful assistant. If you don't know the answer, tell that you don't know"),
                    ("human", "Context:\n{context}\n\nQuestion: {input}")
                ])

        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        response = retrieval_chain.invoke({"input": self.query})

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