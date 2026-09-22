# Experimental results

Raw experimental results are stored separately for each development machine.

Structure:

- `bernat/`
- `marti/`

Each machine contains independent results for:

- PostgreSQL
- Chroma

Performance comparisons should be made within the same machine:

- PostgreSQL vs Chroma on Bernat's machine
- PostgreSQL vs Chroma on Martí's machine

Absolute execution times from different machines should not be directly
compared because hardware and runtime conditions may differ.

Using two machines allows us to check whether the same general behavioural
trends are reproduced in different environments.

Each result file should document the execution environment, measurement
methodology and raw results so that experiments can be reproduced consistently.
