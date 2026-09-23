import csv
import time
import statistics

import chromadb
from sentence_transformers import SentenceTransformer


CSV_FILE = "data/bookcorpus_10000.csv"
CHROMA_PATH = "chroma_db/c1"
COLLECTION_NAME = "bookcorpus_c1"
MODEL_NAME = "all-MiniLM-L6-v2"


def main():
    # Local persistent Chroma database
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Remove the previous collection so every execution starts clean
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    # Load the same embedding model used in PostgreSQL P1
    model = SentenceTransformer(MODEL_NAME)

    print(f"Embedding model loaded: {MODEL_NAME}")
    print(f"Embedding dimensions: {model.get_embedding_dimension()}")

    # Warm up the model before taking measurements
    model.encode("warm-up sentence")

    # Embeddings will be generated explicitly and passed to Chroma
    collection = client.create_collection(
        name=COLLECTION_NAME
    )

    generation_times = []
    storage_times = []

    with open(CSV_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader, start=1):
            sentence_id = str(row["id"])
            text = row["text"]

            # Generate the embedding explicitly
            generation_start = time.perf_counter()

            embedding = model.encode(text).tolist()

            generation_end = time.perf_counter()
            generation_times.append(
                generation_end - generation_start
            )

            # Store the document and its precomputed embedding in Chroma
            storage_start = time.perf_counter()

            collection.add(
                ids=[sentence_id],
                documents=[text],
                embeddings=[embedding],
            )

            storage_end = time.perf_counter()
            storage_times.append(
                storage_end - storage_start
            )

            if i % 100 == 0:
                print(f"Processed {i} sentences...")

    print("\n" + "=" * 80)
    print("C1 RESULTS")

    print(f"\nStored sentences: {collection.count()}")

    print("\nEmbedding generation time:")
    print(f"Minimum: {min(generation_times):.6f} s")
    print(f"Maximum: {max(generation_times):.6f} s")
    print(f"Average: {statistics.mean(generation_times):.6f} s")
    print(
        f"Standard deviation: "
        f"{statistics.stdev(generation_times):.6f} s"
    )

    print("\nEmbedding storage time:")
    print(f"Minimum: {min(storage_times):.6f} s")
    print(f"Maximum: {max(storage_times):.6f} s")
    print(f"Average: {statistics.mean(storage_times):.6f} s")
    print(
        f"Standard deviation: "
        f"{statistics.stdev(storage_times):.6f} s"
    )


if __name__ == "__main__":
    main()