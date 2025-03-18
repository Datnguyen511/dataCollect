import hashlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

global_unique_hashes = set()

def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

def chunk_text(text, title, chunk_size=2000, overlap=50):
    global global_unique_hashes
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len
    )
    chunks = splitter.create_documents([text])
    unique_chunks = []
    for chunk in chunks:
        chunk_hash = hash_text(chunk.page_content)
        if chunk_hash not in global_unique_hashes:
            unique_chunks.append(chunk)
            global_unique_hashes.add(chunk_hash)
    for chunk in unique_chunks:
        chunk.page_content = f"{title} {chunk.page_content}"
    return unique_chunks

def process_text_files(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
                text = f.read()
            title = filename.replace(".txt", "")
            chunks = chunk_text(text, title)
            with open(os.path.join(output_dir, f"{title}_chunks.txt"), 'w', encoding='utf-8') as f:
                for i, chunk in enumerate(chunks):
                    f.write(f"Chunk {i+1}: {chunk.page_content}\n\n")
            print(f"Chunked {filename}")

if __name__ == "__main__":
    process_text_files("content_files", "chunks")