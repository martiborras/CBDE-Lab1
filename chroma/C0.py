import csv
import time
import statistics

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


CSV_FILE = "data/bookcorpus_10000.csv"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "bookcorpus"


def main():
    # Local persistent Chroma database
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Remove the previous collection so every execution starts clean
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    # Chroma's default embedding function uses all-MiniLM-L6-v2
    embedding_function = DefaultEmbeddingFunction()

    # Warm up the embedding model before taking measurements.
    # This avoids including model loading/download time in the first insertion.
    embedding_function(["warm-up sentence"])

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )

    insertion_times = []

    with open(CSV_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            sentence_id = str(row["id"])
            text = row["text"]

            start = time.perf_counter()

            collection.add(
                ids=[sentence_id],
                documents=[text],
            )

            end = time.perf_counter()
            insertion_times.append(end - start)

    print(f"Inserted sentences: {collection.count()}")
    print(f"Minimum insertion time: {min(insertion_times):.6f} s")
    print(f"Maximum insertion time: {max(insertion_times):.6f} s")
    print(f"Average insertion time: {statistics.mean(insertion_times):.6f} s")
    print(
        f"Standard deviation: "
        f"{statistics.stdev(insertion_times):.6f} s"
    )


if __name__ == "__main__":
    main()
