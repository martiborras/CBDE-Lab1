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

## 13. Multi-machine experimental methodology

The experiments will be reproduced independently on two development machines,
one used by Bernat and one used by Martí.

The objective of using two machines is not to compare their absolute execution
times directly, since differences in hardware, operating-system scheduling,
I/O activity and other runtime conditions may affect performance.

Instead, each machine will execute the complete PostgreSQL and Chroma
experiments using the same dataset, scripts and general methodology.

Performance comparisons will therefore be made within each machine:

- PostgreSQL vs Chroma on Bernat's machine.
- PostgreSQL vs Chroma on Martí's machine.

Results obtained on different machines will not be directly compared as if the
difference were caused by the database technology.

Using two independent environments will allow us to check whether the same
general trends are reproduced across different machines.

Raw experimental results will be stored separately under:

- `results/bernat/`
- `results/marti/`

The `LAB_NOTES.md` file will contain the methodological decisions,
interpretation of the results, relevant problems encountered and conclusions.

### Bernat — P0 repeated experiment

P0 was reproduced on Bernat's machine using the same fixed dataset of
10,000 sentences.

Five complete executions were performed.

Average insertion times:

- Run 1: 1.262 ms
- Run 2: 1.263 ms
- Run 3: 1.332 ms
- Run 4: 1.234 ms
- Run 5: 1.305 ms

The mean of the five run averages was approximately 1.279 ms per sentence.

The average times were relatively stable across executions, although isolated
higher-latency insertions were observed. The largest individual insertion time
was 40.271 ms.

These results are stored in:

`results/bernat/postgresql/P0.txt`

No direct performance comparison will be made with P0 results obtained on
Martí's machine because the experiments were executed on different hardware
and runtime environments.

---

## 14. PostgreSQL P1 - Embedding generation and storage

### Embedding model

The selected embedding model is `all-MiniLM-L6-v2`, following the lightweight transformer recommendation in the lab statement.

The model was loaded using `sentence-transformers`.

A preliminary test confirmed that each sentence is transformed into an embedding with 384 dimensions.

### PostgreSQL representation

Pgvector cannot be used in the mandatory PostgreSQL part of the lab.

Therefore, the `sentences` table was extended with:

`embedding DOUBLE PRECISION[]`

This allows PostgreSQL to store the 384 floating-point values of each embedding using a native PostgreSQL array.

This representation is convenient for storage but does not provide native vector-distance operators or specialized vector indexing. This decision will be especially relevant when implementing P2 and discussing the vector-data impedance mismatch.

### P1 methodology

For every sentence already stored in PostgreSQL:

1. Read its `id` and textual content.
2. Generate its embedding using `all-MiniLM-L6-v2`.
3. Convert the resulting NumPy array to a Python list.
4. Update the corresponding PostgreSQL row.
5. Commit the operation.

Embedding generation is performed outside the measured section.

The timer measures the SQL `UPDATE` that stores one embedding and the corresponding `COMMIT`.

This maintains a per-element baseline similar to P0.

### P1 results - Martí machine

10,000 embeddings were stored.

- Minimum storage time: 0.003174 s
- Maximum storage time: 0.049861 s
- Average storage time: 0.004681 s
- Standard deviation: 0.001827 s

### Validation

A SQL validation query confirmed:

- Total sentences: 10,000
- Sentences with an embedding: 10,000
- Minimum embedding dimensionality: 384
- Maximum embedding dimensionality: 384

Therefore, every sentence has a complete 384-dimensional embedding stored in PostgreSQL.

### Points to revisit

- Repeat P1 several times if repeated-run measurements are required for the final experimental methodology.
- Compare individual commits with optimized insertion/update strategies.
- Evaluate the difficulty and performance of computing vector distances over `DOUBLE PRECISION[]` in P2.
- Compare this representation with Chroma's native vector handling.

## 15. PostgreSQL P2 - Top-2 similarity search

### Objective

For 10 fixed and clearly identified sentences, find the top-2 most similar
sentences among the other 9,999 sentences using two different distance metrics.

The same query sentence IDs will later be reused in Chroma C2 to make the
comparison reproducible and fair.

### Query sentence selection

One sentence was selected from approximately each 1,000-sentence region of
the dataset in order to obtain a deterministic and distributed sample.

Query IDs:

- 0
- 1010
- 2001
- 3014
- 4004
- 5003
- 6003
- 7001
- 8003
- 9003

### Distance metrics

Two metrics were implemented:

1. Euclidean distance
2. Cosine distance

For both metrics, a smaller distance means that two embeddings are considered
more similar.

The query sentence itself is excluded from the candidate sentences.

### Implementation

PostgreSQL stores the embeddings as `DOUBLE PRECISION[]`.

Since Pgvector cannot be used in this part of the laboratory, similarity
computation is implemented explicitly in Python using NumPy.

The script:

1. Retrieves the embeddings stored in PostgreSQL.
2. Takes each of the 10 selected query sentences.
3. Compares its embedding exhaustively against the other 9,999 embeddings.
4. Computes the distance using Euclidean or Cosine distance.
5. Sorts the candidates by ascending distance.
6. Selects the first two results.

This implementation also illustrates the impedance mismatch: PostgreSQL can
store the vector representation using a generic array, but it does not provide
the specialized vector operators and vector indexes that a vector database
provides.

### Timing methodology

The two metrics are timed separately.

For each query, the measured operation includes:

- computation of the 9,999 distances;
- sorting the candidates;
- selection of the top-2 results.

The initial retrieval of all embeddings from PostgreSQL is outside the timed
region.

Therefore, the reported times represent the similarity-search computation
implemented in Python and should not be interpreted as PostgreSQL-native vector
query execution times.

### Euclidean distance results

- Minimum: 0.292067 s
- Maximum: 0.453680 s
- Average: 0.365925 s
- Standard deviation: 0.066833 s

### Cosine distance results

- Minimum: 0.338566 s
- Maximum: 0.411857 s
- Average: 0.363042 s
- Standard deviation: 0.022566 s

Both metrics have a very similar average execution time in this experiment.
Cosine distance showed lower timing variability in this run.

### Comparison between Euclidean and Cosine results

For all 10 query sentences, Euclidean and Cosine returned exactly the same
top-2 sentences in exactly the same order.

The numerical distance values are different, but the ranking is identical.

To investigate this result, the norms of several stored embeddings were
measured:

- ID 0: 0.9999999453
- ID 1010: 0.9999999716
- ID 2001: 1.0000000262
- ID 5003: 0.9999999962
- ID 9003: 1.0000000527

Therefore, the embeddings are effectively unit-normalized.

For unit vectors:

    Euclidean_distance^2 = 2 * Cosine_distance

Consequently, Euclidean and Cosine distance are monotonic transformations of
each other for these embeddings and therefore produce the same ranking.

This does not mean that Euclidean and Cosine distance are equivalent in
general. The result follows from the normalization of the embeddings used in
this experiment.

### Points for PQ1 / final discussion

- Query times are reasonably close across the 10 queries, although Euclidean
  showed more variability than Cosine in this run.
- Both metrics produced identical rankings because the embeddings are
  effectively unit-normalized.
- PostgreSQL without Pgvector has no native vector datatype/operator/index
  specialized for this similarity-search workload.
- The current solution retrieves generic arrays and explicitly computes
  similarities in Python.
- This is an example of the impedance mismatch studied in the laboratory.
- Chroma C2 must reuse exactly the same 10 query IDs and, where possible, the
  same distance metrics for a fair comparison.