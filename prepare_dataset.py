from datasets import load_dataset
import csv

NUM_SENTENCES = 10_000
OUTPUT_FILE = "data/bookcorpus_10000.csv"

dataset = load_dataset(
    "bookcorpus",
    split="train",
    streaming=True,
    trust_remote_code=True
)

count = 0

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "text"])

    for example in dataset:
        text = example["text"].strip()

        # Ignore empty entries
        if not text:
            continue

        writer.writerow([count, text])
        count += 1

        if count >= NUM_SENTENCES:
            break

print(f"Saved {count} sentences to {OUTPUT_FILE}")
