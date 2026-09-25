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

BATCH_SIZE = 5000


def add_in_batches(collection, ids, documents, embeddings):
    """
    Add vectors to Chroma in batches because Chroma has a maximum
    batch size limit for a single add() operation.
    """

    for start in range(0, len(ids), BATCH_SIZE):
        end = start + BATCH_SIZE

        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            embeddings=embeddings[start:end],
        )


def get_top_2(collection, query_id, query_embedding):
    """
    Query Chroma for the closest vectors and remove the query itself.
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

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    source_collection = client.get_collection(
        name=SOURCE_COLLECTION
    )

    print(
        f"Source collection contains "
        f"{source_collection.count()} sentences."
    )

    # Retrieve embeddings generated during C1
    data = source_collection.get(
        include=[
            "documents",
            "embeddings",
        ]
    )

    ids = data["ids"]
    documents = data["documents"]
    embeddings = data["embeddings"]


    # Remove previous C2 collections
    for collection_name in [
        L2_COLLECTION,
        COSINE_COLLECTION,
    ]:
        try:
            client.delete_collection(
                name=collection_name
            )
        except Exception:
            pass


    # Create HNSW index using L2 distance
    l2_collection = client.create_collection(
        name=L2_COLLECTION,
        configuration={
            "hnsw": {
                "space": "l2"
            }
        },
    )


    # Create HNSW index using cosine distance
    cosine_collection = client.create_collection(
        name=COSINE_COLLECTION,
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        },
    )


    print("Building L2 HNSW index...")

    add_in_batches(
        l2_collection,
        ids,
        documents,
        embeddings,
    )


    print("Building cosine HNSW index...")

    add_in_batches(
        cosine_collection,
        ids,
        documents,
        embeddings,
    )


    print("C2 collections created successfully.")


    # Retrieve fixed query embeddings

    query_data = source_collection.get(
        ids=[
            str(query_id)
            for query_id in QUERY_IDS
        ],
        include=[
            "documents",
            "embeddings",
        ],
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

        start = time.perf_counter()

        l2_results = get_top_2(
            l2_collection,
            query_id,
            query_embedding,
        )

        end = time.perf_counter()

        l2_query_times.append(
            end - start
        )


        # Cosine query

        start = time.perf_counter()

        cosine_results = get_top_2(
            cosine_collection,
            query_id,
            query_embedding,
        )

        end = time.perf_counter()

        cosine_query_times.append(
            end - start
        )


        print("\n" + "=" * 80)
        print(f"Query ID: {query_id}")
        print(f"Query text: {query_text}")


        print("\nTop-2 using Euclidean (L2) distance:")

        for rank, result in enumerate(
            l2_results,
            start=1
        ):
            result_id, document, distance = result

            print(f"\nRank {rank}")
            print(f"ID: {result_id}")
            print(f"Distance: {distance:.6f}")
            print(f"Text: {document}")


        print("\nTop-2 using Cosine distance:")

        for rank, result in enumerate(
            cosine_results,
            start=1
        ):
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
