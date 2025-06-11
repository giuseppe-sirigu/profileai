import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os
from dotenv import load_dotenv

load_dotenv(override=True)

embedding_fn = OpenAIEmbeddingFunction(api_key=os.getenv("OPENAI_API_KEY"))

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="publications", embedding_function=embedding_fn)

def retrieve_docs(query, top_k=5, section_filter=None):
    """
    Retrieve docs from Chroma based on query and optional section filter.
    """
    filters = {}
    if section_filter:
        filters["section"] = section_filter

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=filters if filters else None
    )
    print(results)
    return results["documents"][0]  # list of retrieved text chunks

def rag_agent(question):
    # Step 1: Retrieve relevant chunks, optionally filtering by section
    retrieved_chunks = retrieve_docs(question, top_k=5, section_filter=None)

    if not retrieved_chunks:
        return {"context": "Sorry, I could not find relevant information."}
    
    return {"context": " ".join(retrieved_chunks)}

rag_agent_json = {
    "name": "rag_agent",
    "description": "Always use this tool to retrieve information related to the publications.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that refers to one or more publications"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}
