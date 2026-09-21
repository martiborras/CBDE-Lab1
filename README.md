# CBDE Lab 1 — Vector Databases vs Relational Databases

Laboratory project for the CBDE course.

The objective of the project is to study the impedance mismatch between
relational databases and vector databases by comparing PostgreSQL and Chroma
using the same textual dataset and embeddings.

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
│   ├── C0.py
│   ├── C1.py
│   └── C2.py
├── results/
├── prepare_dataset.py
├── requirements.txt
├── LAB_NOTES.md
├── .env.example
└── README.md
```

## Environment

The project has been developed using:

- Ubuntu 24.04 LTS (WSL2)
- Python 3.12
- PostgreSQL 16

## Setup

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd CBDE-Lab1
```

Create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Create the local environment configuration:

```bash
cp .env.example .env
```

Edit `.env` and configure the PostgreSQL credentials for your local machine.

Example:

```text
DB_HOST=localhost
DB_NAME=cbde_lab1
DB_USER=your_postgresql_user
DB_PASSWORD=your_postgresql_password
```

## Dataset

The experiment uses a fixed subset of 10,000 entries from BookCorpus.

The dataset used by the experiments is stored in:

```text
data/bookcorpus_10000.csv
```

The same dataset will be used for PostgreSQL and Chroma to ensure a fair
comparison between both database systems.

`prepare_dataset.py` contains the code used to generate this dataset from
BookCorpus through Hugging Face.

## PostgreSQL

The PostgreSQL database used by the project is:

```text
cbde_lab1
```

The current relational schema is:

```sql
CREATE TABLE sentences (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL
);
```

### P0 — Text insertion

`postgresql/P0.py` loads the 10,000 sentences into PostgreSQL and measures
the insertion times.

Current status:

- P0: implemented
- P1: pending
- P2: pending

## Chroma

Current status:

- C0: pending
- C1: pending
- C2: pending

## Laboratory notes

`LAB_NOTES.md` contains the development log, design decisions, experimental
results and relevant problems encountered during the laboratory.

It should be updated throughout the project so that the final report can be
written from the complete experimental record.
