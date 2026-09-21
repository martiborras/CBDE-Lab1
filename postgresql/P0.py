import os
from dotenv import load_dotenv
import csv
import time
import statistics

import psycopg2


CSV_FILE = "data/bookcorpus_10000.csv"

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def main():
    # Connect to PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Clean the table so that P0 can be executed multiple times
    cursor.execute("TRUNCATE TABLE sentences;")
    conn.commit()

    insertion_times = []

    # Read the fixed BookCorpus chunk
    with open(CSV_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            sentence_id = int(row["id"])
            text = row["text"]

            start = time.perf_counter()

            cursor.execute(
                "INSERT INTO sentences (id, text) VALUES (%s, %s);",
                (sentence_id, text),
            )

            conn.commit()

            end = time.perf_counter()
            insertion_times.append(end - start)

    # Calculate timing statistics
    print(f"Inserted sentences: {len(insertion_times)}")
    print(f"Minimum insertion time: {min(insertion_times):.6f} s")
    print(f"Maximum insertion time: {max(insertion_times):.6f} s")
    print(f"Average insertion time: {statistics.mean(insertion_times):.6f} s")
    print(f"Standard deviation: {statistics.stdev(insertion_times):.6f} s")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
