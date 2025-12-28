from typing import List
from langchain_openai import ChatOpenAI
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
except ImportError:
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema.runnable import RunnablePassthrough
    from langchain.schema.output_parser import StrOutputParser

from . import vector_store

# PRD Section 10 & 11: RAG Pipeline & Answer Format
LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0)

STRICT_SYSTEM_PROMPT = """You are DocuMind Pro, a helpful assistant.
Answer the user's question using the provided context.

Question:
{question}

Context:
{context}

STRICT FORMATTING RULES:
1. Answer: <concise, grounded response>
2. Sources:
   - File: <filename> | Page/Row: <reference>

If the answer is not entirely in the context, summarize what IS in the context related to the question.
If the context is completely irrelevant, then explicitly refuse.
"""

def format_docs(docs):
    """
    CRITICAL: Format context to include metadata so LLM can cite sources.
    Format: Content: [text] | Source: [filename], Page/Row: [ref]
    """
    formatted_chunks = []
    for doc in docs:
        source = doc.metadata.get("document_name", "Unknown File")
        
        # Handle Page or Row Range
        if "page_number" in doc.metadata:
            ref = f"Page {doc.metadata['page_number']}"
        elif "row_range" in doc.metadata:
            ref = doc.metadata['row_range']
        else:
            ref = "Unknown Location"
            
        formatted_chunk = f"Content: {doc.page_content}\nSource: {source}, Ref: {ref}"
        formatted_chunks.append(formatted_chunk)
        
    return "\n\n".join(formatted_chunks)
        
def get_answer(user_id: int, question: str) -> str:
    """
    Retrieves documents and generates an answer using RAG.
    """
    vectorstore = vector_store.get_vectorstore(user_id)
    # Reverting to simple retrieval significantly robust
    # We kept k=10 from optimization
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 10, 
            "filter": {"user_id": user_id} 
        }
    )
    
    # Standard RAG Chain
    prompt = ChatPromptTemplate.from_template(STRICT_SYSTEM_PROMPT)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | LLM
        | StrOutputParser()
    )
    
    try:
        response = rag_chain.invoke(question)
        return response
    except Exception as e:
        # print(f"RAG Error: {e}")
        return "Sorry, I encountered an error processing your request."
