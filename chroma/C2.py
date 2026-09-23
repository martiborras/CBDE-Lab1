import time
import statistics

import chromadb


QUERY_IDS = [
    0,
    1010,
    2001,
    3014,
    4004,
    5003,
    6003,
    7001,
    8003,
    9003,
]

CHROMA_PATH = "chroma_db/c1"
SOURCE_COLLECTION = "bookcorpus_c1"

L2_COLLECTION = "bookcorpus_c2_l2"
COSINE_COLLECTION = "bookcorpus_c2_cosine"


def get_top_2(collection, query_id, query_embedding):
    """
    Query Chroma for the closest vectors.

    We request 3 results because the query sentence itself is expected
    to be the closest result. It is explicitly removed afterwards.
    """
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "distances"],
    )

    top_2 = []

    for result_id, document, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["distances"][0],
    ):
        if result_id == query_id:
            continue

        top_2.append(
            (result_id, document, distance)
        )

        if len(top_2) == 2:
            break

    return top_2


def main():
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # C1 contains the same 10,000 sentences and their explicitly
    # generated all-MiniLM-L6-v2 embeddings.
    source_collection = client.get_collection(
        name=SOURCE_COLLECTION
    )

    print(
        f"Source collection contains "
        f"{source_collection.count()} sentences."
    )

    # Retrieve documents and embeddings generated during C1.
    data = source_collection.get(
        include=["documents", "embeddings"]
    )

    ids = data["ids"]
    documents = data["documents"]
    embeddings = data["embeddings"]

    # Remove previous C2 collections so every execution starts clean.
    for collection_name in [L2_COLLECTION, COSINE_COLLECTION]:
        try:
            client.delete_collection(name=collection_name)
        except Exception:
            pass

    # One collection uses Euclidean (L2) distance.
    l2_collection = client.create_collection(
        name=L2_COLLECTION,
        configuration={
            "hnsw": {
                "space": "l2"
            }
        },
    )

    # The other collection uses cosine distance.
    cosine_collection = client.create_collection(
        name=COSINE_COLLECTION,
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        },
    )

    print("Creating L2 collection...")
    l2_collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
    )

    print("Creating cosine collection...")
    cosine_collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
    )

    print("C2 collections created successfully.")

    # Obtain the 10 fixed query sentences and embeddings.
    query_data = source_collection.get(
        ids=[str(query_id) for query_id in QUERY_IDS],
        include=["documents", "embeddings"],
    )

    query_lookup = {}

    for query_id, document, embedding in zip(
        query_data["ids"],
        query_data["documents"],
        query_data["embeddings"],
    ):
        query_lookup[query_id] = (
            document,
            embedding,
        )

    l2_query_times = []
    cosine_query_times = []

    for query_id_int in QUERY_IDS:
        query_id = str(query_id_int)

        query_text, query_embedding = query_lookup[query_id]

        # L2 query
        l2_start = time.perf_counter()

        l2_top_2 = get_top_2(
            l2_collection,
            query_id,
            query_embedding,
        )

        l2_end = time.perf_counter()
        l2_query_times.append(l2_end - l2_start)

        # Cosine query
        cosine_start = time.perf_counter()

        cosine_top_2 = get_top_2(
            cosine_collection,
            query_id,
            query_embedding,
        )

        cosine_end = time.perf_counter()
        cosine_query_times.append(
            cosine_end - cosine_start
        )

        print("\n" + "=" * 80)
        print(f"Query ID: {query_id}")
        print(f"Query text: {query_text}")

        print("\nTop-2 using Euclidean (L2) distance:")

        for rank, result in enumerate(l2_top_2, start=1):
            result_id, document, distance = result

            print(f"\nRank {rank}")
            print(f"ID: {result_id}")
            print(f"Distance: {distance:.6f}")
            print(f"Text: {document}")

        print("\nTop-2 using Cosine distance:")

        for rank, result in enumerate(cosine_top_2, start=1):
            result_id, document, distance = result

            print(f"\nRank {rank}")
            print(f"ID: {result_id}")
            print(f"Distance: {distance:.6f}")
            print(f"Text: {document}")

    print("\n" + "=" * 80)
    print("QUERY TIME STATISTICS")

    print("\nEuclidean (L2) distance:")
    print(
        f"Minimum query time: "
        f"{min(l2_query_times):.6f} s"
    )
    print(
        f"Maximum query time: "
        f"{max(l2_query_times):.6f} s"
    )
    print(
        f"Average query time: "
        f"{statistics.mean(l2_query_times):.6f} s"
    )
    print(
        f"Standard deviation: "
        f"{statistics.stdev(l2_query_times):.6f} s"
    )

    print("\nCosine distance:")
    print(
        f"Minimum query time: "
        f"{min(cosine_query_times):.6f} s"
    )
    print(
        f"Maximum query time: "
        f"{max(cosine_query_times):.6f} s"
    )
    print(
        f"Average query time: "
        f"{statistics.mean(cosine_query_times):.6f} s"
    )
    print(
        f"Standard deviation: "
        f"{statistics.stdev(cosine_query_times):.6f} s"
    )


if __name__ == "__main__":
    main()