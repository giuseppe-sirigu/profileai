from dotenv import load_dotenv
import os
import uuid
import re

import fitz
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

load_dotenv(override=True)

embedding_fn = OpenAIEmbeddingFunction(api_key=os.getenv("OPENAI_API_KEY"))

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="publications", embedding_function=embedding_fn)

def extract_chunks_with_layout(filepath, max_chars=1000):
    doc = fitz.open(filepath)
    title = os.path.splitext(os.path.basename(filepath))[0]

    chunks = []
    current_section = "Introduction"  # fallback default
    chunk = ""
    section_font_threshold = 1.5  # ratio over average font size to consider as header

    for page_number, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        spans_info = []

        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    spans_info.append({
                        "text": span["text"].strip(),
                        "size": span["size"],
                        "font": span["font"],
                        "bold": "Bold" in span["font"],
                        "origin": span["origin"],
                        "bbox": span["bbox"]
                    })

        # Calculate average font size for the page
        font_sizes = [s["size"] for s in spans_info if len(s["text"]) > 5]
        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 10

        for span in spans_info:
            text = span["text"]
            if not text or len(text) < 2:
                continue

            is_potential_header = (
                span["size"] > avg_font_size * section_font_threshold
                or span["bold"]
                or text.isupper()
            )
            if is_potential_header and len(text) < 80:
                current_section = text
                continue

            # Accumulate normal content under current section
            if len(chunk) + len(text) < max_chars:
                chunk += " " + text
            else:
                chunks.append({
                    "text": chunk.strip(),
                    "page": page_number,
                    "section": current_section,
                    "title": title
                })
                chunk = text

    if chunk:
        chunks.append({
            "text": chunk.strip(),
            "page": page_number,
            "section": current_section,
            "title": title
        })

    return chunks

def add_structured_pdfs_to_chroma(folder_path):
    for filename in os.listdir(folder_path):
        if not filename.endswith(".pdf"):
            continue
        filepath = os.path.join(folder_path, filename)
        print(f"📄 Processing {filename}")
        chunks = extract_chunks_with_layout(filepath)

        ids = [str(uuid.uuid4()) for _ in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [
            {
                "title": c["title"],
                "page": c["page"],
                "section": c["section"],
                "source": filepath
            }
            for c in chunks
        ]
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"✅ {len(chunks)} chunks added from {filename}")

if __name__ == "__main__":
    add_structured_pdfs_to_chroma("./data/publications")
