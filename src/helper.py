# all the imports I will be using

from langchain_ollama import ChatOllama, OllamaEmbeddings  
from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from pypdf import PdfReader, PdfWriter

import os
import time


# Using nomic-embed-text model (8192 token context)

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"
)

# sometimes user inputted pdfs may not be structurally correct that is needed for chunking and storing content in vector db's

def repair_pdf(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path, strict=False)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        repaired_path = pdf_path.replace(".pdf", "_repaired.pdf")
        with open(repaired_path, "wb") as f:
            writer.write(f)
        return repaired_path
    except:
        return pdf_path


def create_vector_db(pdf_path: str, batch_size: int = 8) -> FAISS:
    
    repaired_path = repair_pdf(pdf_path)
    loader = PyPDFLoader(repaired_path)
    docs = loader.load()
    
    if not docs:
        raise ValueError("no content extracted from PDF")
    
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    
    # for large pdf files, it is observed that the system recieves a lot of crashes so one way to deal with it is by creating a robust pipeline for batching the chunks of the document details

    db = None
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]

        try:
            if db is None:
                db = FAISS.from_documents(batch, embedding=embeddings)
            else:
                db.merge_from(FAISS.from_documents(batch, embedding=embeddings))
        except Exception as e:
            try:
                if db is None:
                    db = FAISS.from_documents(batch, embedding=embeddings)
                else:
                    db.merge_from(FAISS.from_documents(batch, embedding=embeddings))
            except:
                continue
    
    if repaired_path != pdf_path and os.path.exists(repaired_path):
        try:
            os.remove(repaired_path)
        except:
            pass
    
    if db is None:
        raise Exception("failed to create embeddings")
    
    return db


def get_response_from_pdf(db, query, k=8):

    docs = db.similarity_search(query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])
    
    llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434")
    
    # prompt template

    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        You are a helpful assistant that can answer questions about PDF documents 
        based on their content.
        
        Answer the following question: {question}
        By analyzing the following document content: {docs}
        
        Only use the factual information from the document to answer the question.
        
        If you don't have enough information to answer the question, say "I don't know".
        
        Your answers should be verbose and detailed. Provide explanations, examples, 
        and context when relevant.
        """,
    )
    
    # chaining everything together

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": query, "docs": docs_page_content})
    
    return response