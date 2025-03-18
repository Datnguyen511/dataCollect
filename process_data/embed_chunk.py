import json
import numpy as np
from FlagEmbedding import BGEM3FlagModel
import os

embed_model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def embed(chunks):
    embedded_chunks = []
    for chunk in chunks:
        emb = embed_model.encode(chunk, batch_size=12, max_length=600)['dense_vecs']
        embedding = np.array(emb)
        embedded_chunks.append({
            "data": chunk,
            "vector_data": json.loads(json.dumps(embedding, cls=NumpyEncoder))
        })
    return embedded_chunks

def process_chunk_files(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.endswith("_chunks.txt"):
            chunks = []
            with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
                current_chunk = ""
                for line in f:
                    if line.startswith("Chunk "):
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = line.split(":", 1)[1].strip()
                    else:
                        current_chunk += " " + line.strip()
                if current_chunk:
                    chunks.append(current_chunk.strip())
            embedded_chunks = embed(chunks)
            output_file = os.path.join(output_dir, f"{filename.replace('.txt', '')}_embedded.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(embedded_chunks, f, indent=4)
            print(f"Embedded {filename}")

if __name__ == "__main__":
    process_chunk_files("chunks", "embedded")