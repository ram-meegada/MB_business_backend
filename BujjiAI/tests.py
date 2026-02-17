from django.test import TestCase
import os
import pandas as pd
from pdf2image import convert_from_path
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores import Chroma
from pathlib import Path
import json
from django.conf import settings
from openai import OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# embeddings = OpenAIEmbeddings(model=settings.EMBEDDINGS_MODEL)
# VECTOR_DB = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")


def extract_csv():
    dataset_path = os.path.join(BASE_DIR, 'Backend_Related/Datasets/dairy_dataset.csv')
    df = pd.read_csv(dataset_path)
    docs = []

    for _, row in df.iterrows():
        content = json.dumps(dict(row.items()))
        docs.append(Document(page_content=content))

    vectordb = Chroma.from_documents(docs, embedding=embeddings, persist_directory="./chroma_db")
    vectordb.persist()


def query_vector_db():
    query = "Cows greater than 60"
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    VECTOR_DB = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")

    docs = VECTOR_DB.similarity_search(query, k=2)

    for doc in docs:
        print("🔎", doc.page_content)


def test_gpt_mini():
    retriever = VECTOR_DB.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0)

    prompt = ChatPromptTemplate.from_template(
        """
        You are an assistant answering only based on the given context.
        If the answer is not in the context, say you don't know.

        Context:
        {context}

        Question: {input}
        """
    )
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    query = "What is my dairy farm business model?"
    response = retrieval_chain.invoke({"input": query})

    print("Answer:", response["answer"])


if __name__ == '__main__':
    # extract_csv()
    query_vector_db()
    # test_gpt_mini()
    pass
