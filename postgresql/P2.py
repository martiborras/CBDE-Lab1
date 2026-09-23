# Fixed query sentences used for both PostgreSQL P2 and Chroma C2.
# One sentence is selected from each 1,000-sentence region of the dataset
# to obtain a reproducible and distributed sample.

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

import os
import time
import statistics

import numpy as np

import psycopg2
from dotenv import load_dotenv

def cosine_distance(vector_a, vector_b):
    dot_product = np.dot(vector_a, vector_b)

    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    cosine_similarity = dot_product / (norm_a * norm_b)

    return 1 - cosine_similarity

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)

cursor = conn.cursor()

cursor.execute(
    """
    SELECT id, text, embedding
    FROM sentences
    WHERE id = ANY(%s)
    ORDER BY id;
    """,
    (QUERY_IDS,),
)

query_sentences = cursor.fetchall()

cursor.execute(
    """
    SELECT id, text, embedding
    FROM sentences
    ORDER BY id;
    """
)

all_sentences = cursor.fetchall()

# Compute the top-2 closest sentences using Euclidean distance
# for each of the 10 fixed query sentences.

euclidean_query_times = []
cosine_query_times = []

for query_id, query_text, query_embedding in query_sentences:
    query_embedding = np.array(query_embedding)

    distances = []
    cosine_distances = []

    euclidean_start = time.perf_counter()

    for sentence_id, text, embedding in all_sentences:
        # Do not compare the query sentence with itself
        if sentence_id == query_id:
            continue

        candidate_embedding = np.array(embedding)

        # Euclidean distance
        distance = np.linalg.norm(
            query_embedding - candidate_embedding
        )

        distances.append(
            (distance, sentence_id, text)
        )

    # Sort both distance lists and keep the two closest sentences
    distances.sort(key=lambda x: x[0])
    top_2 = distances[:2]

    euclidean_end = time.perf_counter()
    euclidean_query_times.append(euclidean_end - euclidean_start)

    cosine_start = time.perf_counter()

    for sentence_id, text, embedding in all_sentences:
        if sentence_id == query_id:
            continue

        candidate_embedding = np.array(embedding)

        cos_distance = cosine_distance(
            query_embedding,
            candidate_embedding
        )

        cosine_distances.append(
            (cos_distance, sentence_id, text)
        )

    cosine_distances.sort(key=lambda x: x[0])
    cosine_top_2 = cosine_distances[:2]

    cosine_end = time.perf_counter()
    cosine_query_times.append(cosine_end - cosine_start)

    print("\n" + "=" * 80)
    print(f"Query ID: {query_id}")
    print(f"Query text: {query_text}")

    print("\nTop-2 using Euclidean distance:")

    for rank, result in enumerate(top_2, start=1):
        distance, sentence_id, text = result

        print(f"\nRank {rank}")
        print(f"ID: {sentence_id}")
        print(f"Distance: {distance:.6f}")
        print(f"Text: {text}")

    print("\nTop-2 using Cosine distance:")

    for rank, result in enumerate(cosine_top_2, start=1):
        distance, sentence_id, text = result

        print(f"\nRank {rank}")
        print(f"ID: {sentence_id}")
        print(f"Distance: {distance:.6f}")
        print(f"Text: {text}")

print("\n" + "=" * 80)
print("QUERY TIME STATISTICS")

print("\nEuclidean distance:")
print(f"Minimum query time: {min(euclidean_query_times):.6f} s")
print(f"Maximum query time: {max(euclidean_query_times):.6f} s")
print(f"Average query time: {statistics.mean(euclidean_query_times):.6f} s")
print(
    f"Standard deviation: "
    f"{statistics.stdev(euclidean_query_times):.6f} s"
)

print("\nCosine distance:")
print(f"Minimum query time: {min(cosine_query_times):.6f} s")
print(f"Maximum query time: {max(cosine_query_times):.6f} s")
print(f"Average query time: {statistics.mean(cosine_query_times):.6f} s")
print(
    f"Standard deviation: "
    f"{statistics.stdev(cosine_query_times):.6f} s"
)

cursor.close()
conn.close()
