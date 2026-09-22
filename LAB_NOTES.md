# CBDE Lab 1 — Laboratory Notes
## Impedance Mismatch: Vector Databases vs Relational Databases

## 1. Objective

The purpose of the laboratory is to study the impedance mismatch that appears
when data whose natural representation is a vector is stored and processed
using different database models.

The experiment compares PostgreSQL, a relational DBMS, with Chroma, a vector
database. The same textual dataset and embeddings will be used in both systems
so that differences in storage, querying, implementation complexity and
performance can be compared.

Pgvector is optional and has not been used in the basic PostgreSQL experiment.

---

## 2. Development environment

Main development environment:

- Windows host
- WSL2
- Ubuntu 24.04 LTS
- Python 3.12.3
- Python virtual environment: `.venv`
- Git
- PostgreSQL 16.15

The project is stored inside the Linux filesystem:

`/home/marti_borras/CBDE-Lab1`

rather than `/mnt/c/...`.

This was chosen to avoid unnecessary filesystem overhead and possible
permission/synchronization issues when working with Python, PostgreSQL and
large amounts of data under WSL.

---

## 3. Project structure

Current structure:

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
├── README.md
├── .gitignore
└── .env (not tracked by Git)

The Python virtual environment `.venv/` is also excluded from Git.

Database credentials are stored in `.env` rather than directly in the Python
scripts so that credentials are not published in the repository.

---

## 4. Dataset preparation

Dataset: BookCorpus.

Hugging Face `datasets` is used to access BookCorpus.

An initial compatibility problem was encountered.

With:

- datasets 5.0.1

BookCorpus could not be loaded because this version no longer supported the
dataset loading script (`bookcorpus.py`).

The environment was changed to:

- datasets 3.6.0
- huggingface_hub 0.33.2

This combination successfully loaded BookCorpus using streaming.

Example first sentence obtained:

"usually , he would be tearing around the living room , playing with his toys ."

Streaming was used because downloading the complete BookCorpus is unnecessary
for this experiment.

A deterministic chunk containing the first 10,000 non-empty entries was
created and stored as:

`data/bookcorpus_10000.csv`

Format:

id,text

The file contains:

- 10,000 sentences
- 1 header row
- 10,001 total CSV lines

The IDs range from 0 to 9999.

The same fixed dataset will be used for PostgreSQL and Chroma. This is important
for experimental fairness: differences between both systems should come from
their data models and implementations, not from using different input data.

---

## 5. PostgreSQL setup

PostgreSQL version:

16.15

Database:

`cbde_lab1`

Application user:

`cbde_user`

Python communicates with PostgreSQL using `psycopg2`.

The connection from Python to PostgreSQL was tested successfully before
implementing P0.

---

## 6. PostgreSQL textual representation

A relational table was created:

CREATE TABLE sentences (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL
);

Design rationale:

### id — INTEGER PRIMARY KEY

Only 10,000 sentences are used, therefore INTEGER is more than sufficient.

The identifier uniquely identifies each sentence.

Using PRIMARY KEY also causes PostgreSQL to create a B-tree index on the ID.

### text — TEXT NOT NULL

The sentences have variable lengths.

PostgreSQL TEXT avoids imposing an arbitrary maximum length such as
VARCHAR(500) or VARCHAR(1000).

NOT NULL guarantees that stored rows contain textual data.

Empty entries had already been filtered during dataset preparation.

---

## 7. P0 — Text insertion into PostgreSQL

`postgresql/P0.py`:

1. Connects to PostgreSQL using psycopg2.
2. Reads `data/bookcorpus_10000.csv`.
3. Clears the previous contents of the `sentences` table using TRUNCATE.
4. Inserts the 10,000 sentences.
5. Measures individual insertion times using `time.perf_counter()`.
6. Calculates:
   - minimum
   - maximum
   - average
   - standard deviation

For the initial implementation, each INSERT is followed by an individual
COMMIT.

This is intentionally a simple baseline implementation rather than an
optimized bulk-loading strategy.

It allows the latency of individual insert operations/transactions to be
observed.

Potential optimization alternatives to discuss later include:

- batching multiple inserts in one transaction
- executemany
- execute_values
- PostgreSQL COPY

These alternatives have not yet been experimentally evaluated.

---

## 8. P0 — First experimental result

Number of inserted sentences:

10,000

First execution:

Minimum insertion time:
0.001796 s

Maximum insertion time:
0.127722 s

Average insertion time:
0.004627 s

Standard deviation:
0.003786 s

Approximate average latency:

4.63 ms per sentence.

The maximum value (~127.7 ms) is much larger than the average and appears to
be an outlier.

No definitive conclusion about stability has been made yet because additional
runs/analysis may be necessary.

The relatively large difference between the minimum, average and maximum
values should be considered when answering PQ1.

---

## 9. Validation

After P0 finished, the database contents were independently checked with:

SELECT COUNT(*) FROM sentences;

Result:

10000

Therefore all expected sentences were successfully stored in PostgreSQL.

The first rows were also inspected using:

SELECT * FROM sentences ORDER BY id LIMIT 5;

---

## 10. Current state

Completed:

- Development environment
- Git initialization
- Project structure
- BookCorpus access
- Fixed 10,000-sentence dataset
- PostgreSQL installation/configuration
- Python → PostgreSQL connection
- Relational schema
- Functional P0 implementation
- First P0 timing experiment
- Validation of 10,000 stored sentences

Next task:

P1 — generate embeddings for the 10,000 sentences and store them in
PostgreSQL without using Pgvector.

Planned embedding model:

`all-MiniLM-L6-v2`

This model produces fixed-size embeddings.

The representation of these vectors inside standard PostgreSQL must be
decided before implementing P1. This decision is especially relevant to the
impedance mismatch being studied.

---

## 11. Points to revisit before final report

Do not treat the current measurements as final yet.

Before writing the report:

- Repeat timing experiments if necessary.
- Save final measurements systematically.
- Decide whether transaction time should be included in the definition of
  insertion time and explain the decision.
- Compare individual insertion with possible optimized PostgreSQL insertion
  methods.
- Analyze stability using min/max/average/std.
- Record embedding generation/storage measurements.
- Record similarity-query measurements.
- Compare the two distance metrics.
- Record equivalent Chroma measurements.
- Compare implementation complexity and number of relevant code lines/API
  calls between PostgreSQL and Chroma.
- Discuss impedance mismatch rather than only raw execution time.
- Record every important design decision and unexpected problem.

---

## 12. AI usage record

AI assistance has been used during development.

Current uses include:

- interpreting the laboratory statement
- planning the project structure
- configuring the Python/PostgreSQL environment
- debugging dependency compatibility problems
- discussing database design decisions
- implementing and explaining the initial P0 solution
- planning experimental measurements

For the mandatory AI appendix, the final report should synthesize:

1. how AI was instructed,
2. how proposed solutions were refined,
3. how generated suggestions were independently validated,
4. which design decisions were ultimately taken by the team.

Full prompts do not need to be reproduced.

---

## C0 implementation comparison

The first C0 implementation inserted documents individually into Chroma.
Although this approach was conceptually similar to PostgreSQL P0, the execution
time was very high.

A second implementation was tested using batch insertion (100 documents per
operation). This reduced the execution time by approximately four times.

The final implementation strategy will be decided after discussing whether
the objective is to maximize comparability with PostgreSQL or represent a more
realistic Chroma loading workflow.
