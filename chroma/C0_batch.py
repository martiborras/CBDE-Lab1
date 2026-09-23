import csv
import time
import statistics

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


CSV_FILE = "data/bookcorpus_10000.csv"
CHROMA_PATH = "chroma_db_batch_test"
COLLECTION_NAME = "bookcorpus_batch"
BATCH_SIZE = 100


def main():
    # Local persistent Chroma database
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Remove previous collection if it exists
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    # Chroma default embedding function
    embedding_function = DefaultEmbeddingFunction()

    # Warm up the model before measuring
    embedding_function(["warm-up sentence"])

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )

    insertion_times = []

    ids_batch = []
    texts_batch = []

    with open(CSV_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            ids_batch.append(str(row["id"]))
            texts_batch.append(row["text"])

            if len(ids_batch) == BATCH_SIZE:
                start = time.perf_counter()

                collection.add(
                    ids=ids_batch,
                    documents=texts_batch,
                )

                end = time.perf_counter()

                insertion_times.append(end - start)

                ids_batch = []
                texts_batch = []

        # Insert remaining sentences if needed
        if ids_batch:
            start = time.perf_counter()

            collection.add(
                ids=ids_batch,
                documents=texts_batch,
            )

            end = time.perf_counter()

            insertion_times.append(end - start)

    print(f"Inserted sentences: {collection.count()}")
    print(f"Batches: {len(insertion_times)}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Minimum batch insertion time: {min(insertion_times):.6f} s")
    print(f"Maximum batch insertion time: {max(insertion_times):.6f} s")
    print(f"Average batch insertion time: {statistics.mean(insertion_times):.6f} s")
    print(
        f"Standard deviation: "
        f"{statistics.stdev(insertion_times):.6f} s"
    )


if __name__ == "__main__":
    main()
