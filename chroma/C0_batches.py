import argparse
import csv
import os
import statistics
import time

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


CSV_FILE = "data/bookcorpus_10000.csv"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "bookcorpus"

# Batch sizes used for the optimization experiment.
# Batch size 1 was already measured with the original C0 implementation.
# Batch size 100 was also already measured and will not be repeated.
EXPERIMENT_BATCH_SIZES = [250, 500, 750, 1000]


def run_experiment(batch_size):
    print()
    print("=" * 60)
    print(f"Running experiment with batch size: {batch_size}")
    print("=" * 60)

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Start each experiment with an empty collection.
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    embedding_function = DefaultEmbeddingFunction()

    # Warm up the embedding model before measuring.
    # Model loading/download time is therefore excluded from the experiment.
    embedding_function(["warm-up sentence"])

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )

    batch_times = []
    total_start = time.perf_counter()

    ids_batch = []
    texts_batch = []

    with open(CSV_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            ids_batch.append(str(row["id"]))
            texts_batch.append(row["text"])

            if len(ids_batch) == batch_size:
                start = time.perf_counter()

                collection.add(
                    ids=ids_batch,
                    documents=texts_batch,
                )

                end = time.perf_counter()
                batch_times.append(end - start)

                ids_batch = []
                texts_batch = []

        # Insert remaining documents if the dataset size is not
        # an exact multiple of the batch size.
        if ids_batch:
            start = time.perf_counter()

            collection.add(
                ids=ids_batch,
                documents=texts_batch,
            )

            end = time.perf_counter()
            batch_times.append(end - start)

    total_end = time.perf_counter()

    total_time = total_end - total_start
    inserted = collection.count()

    print(f"Inserted sentences: {inserted}")
    print(f"Batches: {len(batch_times)}")
    print(f"Batch size: {batch_size}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average time per sentence: {total_time / inserted:.6f} s")
    print(f"Minimum batch insertion time: {min(batch_times):.6f} s")
    print(f"Maximum batch insertion time: {max(batch_times):.6f} s")
    print(
        f"Average batch insertion time: "
        f"{statistics.mean(batch_times):.6f} s"
    )

    if len(batch_times) > 1:
        print(
            f"Standard deviation: "
            f"{statistics.stdev(batch_times):.6f} s"
        )
    else:
        print("Standard deviation: N/A")

    return {
        "batch_size": batch_size,
        "inserted": inserted,
        "batches": len(batch_times),
        "total_time": total_time,
        "time_per_sentence": total_time / inserted,
        "min_batch_time": min(batch_times),
        "max_batch_time": max(batch_times),
        "avg_batch_time": statistics.mean(batch_times),
        "std_batch_time": (
            statistics.stdev(batch_times)
            if len(batch_times) > 1
            else None
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run Chroma C0 batch insertion experiments."
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--batch-size",
        type=int,
        help="Run a single experiment with the specified batch size.",
    )

    group.add_argument(
        "--all",
        action="store_true",
        help="Run all currently selected batch-size experiments.",
    )

    args = parser.parse_args()

    if args.batch_size is not None:
        if args.batch_size <= 0:
            parser.error("batch size must be greater than 0")

        run_experiment(args.batch_size)

    elif args.all:
        results = []

        for batch_size in EXPERIMENT_BATCH_SIZES:
            results.append(run_experiment(batch_size))

        print()
        print("=" * 60)
        print("EXPERIMENT SUMMARY")
        print("=" * 60)

        for result in results:
            print(
                f"Batch {result['batch_size']:>4}: "
                f"{result['total_time']:.3f} s total | "
                f"{result['time_per_sentence']:.6f} s/sentence"
            )


if __name__ == "__main__":
    main()
