import os
import time
import statistics

import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)

cursor = conn.cursor()

# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Get 10 sentences for testing
cursor.execute(
    "SELECT id, text FROM sentences ORDER BY id;"
)

sentences = cursor.fetchall()

insertion_times = []

for i, (sentence_id, text) in enumerate(sentences, start=1):
    # Generate the embedding outside the measured section
    embedding = model.encode(text).tolist()

    # Measure only the storage operation
    start = time.perf_counter()

    cursor.execute(
        "UPDATE sentences SET embedding = %s WHERE id = %s;",
        (embedding, sentence_id),
    )
    conn.commit()

    end = time.perf_counter()

    insertion_times.append(end - start)

    if i % 100 == 0:
        print(f"Processed {i}/{len(sentences)} sentences")

print(f"Stored embeddings: {len(insertion_times)}")
print(f"Minimum storage time: {min(insertion_times):.6f} s")
print(f"Maximum storage time: {max(insertion_times):.6f} s")
print(f"Average storage time: {statistics.mean(insertion_times):.6f} s")
print(
    f"Standard deviation: "
    f"{statistics.stdev(insertion_times):.6f} s"
)

cursor.close()
conn.close()