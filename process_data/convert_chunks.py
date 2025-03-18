import os
import json
import re

input_folder = 'chunks'
output_file = 'dataset.jsonl'

data = []

for filename in os.listdir(input_folder):
    if filename.endswith('.txt'):
        with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                continue
            
            # Split into chunks using "Chunk X:" as delimiter if not already chunked
            chunks = re.split(r'Chunk \d+:', content)[1:]  
            if not chunks:
                continue
            
            # Extract base topic from filename (remove .txt)
            base_topic = filename.replace('.txt', '').replace('_', ' ')
            
            for chunk in chunks:
                chunk = chunk.strip()
                if not chunk:
                    continue
                
                # Split chunk into header and body
                lines = chunk.splitlines()
                if len(lines) < 2:
                    continue
                
                header = lines[0].strip()
                body_start = 1 if len(lines) == 1 else 2 if lines[1].startswith('=') or lines[1].startswith('-') else 1
                body = '\n'.join(lines[body_start:]).strip()
                
                if not body:
                    continue
                
                # Create instruction/response pair
                text = f"{body}"
                data.append({"text": text})


# Write to JSONL
with open(output_file, 'w', encoding='utf-8') as f:
    for entry in data:
        f.write(json.dumps(entry) + '\n')

print(f"Created {output_file} with {len(data)} entries.")