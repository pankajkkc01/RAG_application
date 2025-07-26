from chromadb import PersistentClient
import numpy as np

client     = PersistentClient(path="chroma_db")
collection = client.get_collection("langchain")   # ensure this matches your Chroma() default

total = collection.count()
print(f"Total chunks stored: {total}\n")

if total > 0:
    results = collection.get(include=["documents","embeddings","metadatas"], limit=442)
    for i, (doc, embed) in enumerate(zip(results["documents"], results["embeddings"])):
        print(f"--- Chunk {i+1} ---")
        print("Text:", doc[:200].replace("\n"," "), "...")
        print("Embedding Len:", len(embed))
        print("First 10 dims:", np.round(embed[:10],3), "\n")
else:
    print("⚠️ No chunks found. Did you upload and index a PDF with the API?")
