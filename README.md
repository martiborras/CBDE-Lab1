# CBDE Lab 1 — Vector Databases vs Relational Databases

Laboratory project for the CBDE course.

The objective of the project is to study the differences between a relational database and a vector database by implementing equivalent experiments using PostgreSQL and Chroma.

The experiments use the same fixed textual dataset and the same general embedding model so that the behaviour of both database systems can be studied under comparable conditions.

---

## Project structure

```text
CBDE-Lab1/
├── data/
│   └── bookcorpus_10000.csv
├── postgresql/
│   ├── P0.py
│   ├── P1.py
│   └── P2.py
├── chroma/
│   ├── C0_batches.py
│   ├── C1.py
│   └── C2.py
├── results/
│   ├── postgresql/
│   ├── chroma/
│   ├── previous/
│   └── README.md
├── prepare_dataset.py
├── requirements.txt
├── LAB_NOTES.md
├── .env.example
└── README.md
```

The `results/` directory contains the experimental results obtained during the laboratory. Its internal organization and conventions are described in `results/README.md`.

---

## Environment

The experiments are executed in the following environment:

- Ubuntu 24.04 LTS through WSL2
- Python 3.12
- PostgreSQL 16
- ChromaDB 1.5.9

Python dependencies are specified in `requirements.txt`.

The project uses a Python virtual environment (`.venv`) for its dependencies.

---

## Setup

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd CBDE-Lab1
```

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Create the local environment configuration:

```bash
cp .env.example .env
```

Edit `.env` and configure the PostgreSQL connection parameters:

```text
DB_HOST=localhost
DB_NAME=cbde_lab1
DB_USER=your_postgresql_user
DB_PASSWORD=your_postgresql_password
```

The `.env` file is local and must not be committed to the repository.

---

## Dataset

The experiments use a fixed subset of 10,000 sentences from BookCorpus.

The dataset is stored in:

```text
data/bookcorpus_10000.csv
```

The same dataset is used throughout the PostgreSQL and Chroma experiments.

This is important because the experiments are intended to operate on the same input data.

The dataset contains:

- 10,000 sentences
- an `id` field
- a `text` field

`prepare_dataset.py` contains the code used to generate the fixed dataset from BookCorpus through Hugging Face.

---

# PostgreSQL experiments

The relational database used by the project is:

```text
cbde_lab1
```

The main table used by the experiments is:

```sql
CREATE TABLE sentences (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL
);
```

The PostgreSQL experiments are divided into three parts.

### P0 — Text insertion

`postgresql/P0.py` inserts the 10,000 sentences into PostgreSQL.

Each sentence is inserted individually and the insertion time is measured.

The table is cleared before each execution so that the experiment can be repeated with the same initial state.

The measured operation includes the `INSERT` and its corresponding transaction commit.

### P1 — Embedding storage

`postgresql/P1.py` extends the PostgreSQL experiment by working with sentence embeddings.

The experiment evaluates storing embeddings in the relational database using the selected PostgreSQL representation.

### P2 — Similarity search

`postgresql/P2.py` evaluates similarity search using the stored embeddings.

The experiment measures the execution of similarity queries against the stored sentence representations.

Detailed results and measurements are stored in:

```text
results/postgresql/
```

---

# Chroma experiments

Chroma is used as the vector database for the second part of the laboratory.

The Chroma experiments use Chroma's persistent local storage and its default embedding function:

```text
all-MiniLM-L6-v2
```

The embedding model is warmed up before timing measurements so that model loading and initialization are not included in the measured insertion times.

The Chroma experiments are divided into three parts.

## C0 — Batch insertion

The C0 experiment studies the effect of the batch size when inserting the 10,000 sentences into Chroma.

The final implementation is:

```text
chroma/C0_batches.py
```

The program can run a specific batch size:

```bash
python chroma/C0_batches.py --batch-size 500
```

The batch-size experiment was designed progressively.

The following configurations were evaluated:

```text
1
100
250
500
750
1000
1250
2000
5000
```

Batch size 1 represents individual insertion and is used as the baseline.

The larger batch sizes were tested to study whether increasing the number of documents inserted in each `collection.add()` operation reduces the overall execution time.

The main performance metric is the total time required to insert all 10,000 sentences.

Additional batch-level statistics are also recorded:

- minimum batch insertion time
- maximum batch insertion time
- average batch insertion time
- standard deviation

Some batch sizes were executed more than once in order to observe the variability between executions.

The C0 results are stored in:

```text
results/chroma/
```

The experiments showed a large reduction in execution time when moving from individual insertion to batch insertion. For larger batch sizes, the additional improvements became much smaller and the measured execution times varied between runs.

The results should therefore be interpreted as experimental measurements from the same machine and environment rather than as an absolute optimal batch size.

## C1 — Embedding storage

`chroma/C1.py` evaluates storing the sentence embeddings in Chroma.

The experiment uses the same dataset and embedding approach as the other Chroma experiments.

## C2 — Similarity search

`chroma/C2.py` evaluates similarity search using the embeddings stored in Chroma.

The experiment allows the vector-database approach to be compared with the corresponding PostgreSQL similarity-search experiment.

---

# Experimental methodology

The PostgreSQL and Chroma experiments use the same fixed dataset:

```text
data/bookcorpus_10000.csv
```

The experiments are performed on the same development machine to avoid mixing hardware and runtime differences with database-system differences.

This means that comparisons between PostgreSQL and Chroma are made within the same experimental environment.

The project does not use execution times obtained from different machines as if the difference were caused by the database technology.

For experiments involving repeated executions, the individual runs are also recorded so that variability can be considered when interpreting the results.

---

# Results

Experimental results are stored separately from the implementation code:

```text
results/
```

PostgreSQL results are stored in:

```text
results/postgresql/
```

Chroma results are stored in:

```text
results/chroma/
```

The `results/README.md` file describes the organization of the result files and the conventions used to record experimental measurements.

Previous intermediate results that were obtained before the final experimental methodology was established are kept separately under:

```text
results/previous/
```

These previous results are not used as the main basis for the final cross-database comparison when a corresponding experiment is regenerated under the final methodology.

---

# Laboratory notes

`LAB_NOTES.md` contains the development log of the laboratory.

It records:

- design decisions
- methodological decisions
- changes to the experimental approach
- relevant problems encountered during development
- observations about the experiments
- decisions taken by the team
- information that can be useful when writing the final report

The README provides the general structure and methodology of the project, while `LAB_NOTES.md` provides the chronological and detailed development record.

---

# Dependencies

The main Python dependencies are listed in:

```text
requirements.txt
```

The current project uses:

```text
datasets
psycopg2-binary
python-dotenv
numpy
sentence-transformers
chromadb
```

All versions are pinned in `requirements.txt` to make the experimental environment reproducible.

---

# Reproducibility

To reproduce an experiment:

1. Activate the Python virtual environment.
2. Make sure PostgreSQL is running when executing PostgreSQL experiments.
3. Make sure the `.env` file contains the correct database configuration.
4. Use the fixed dataset in `data/bookcorpus_10000.csv`.
5. Execute the corresponding experiment script.
6. Record the resulting measurements in the appropriate file under `results/`.

For example, a Chroma C0 experiment with batch size 500 can be executed with:

```bash
python chroma/C0_batches.py --batch-size 500
```

The experiment should be run from the project root:

```text
CBDE-Lab1/
```

so that the relative paths to the dataset and other project files are resolved correctly.
