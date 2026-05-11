# Ontology-Guided World-Model Maintenance

Companion repository for the paper "Ontology-guided validation of causal explanations for world-model maintenance in service robots".

## Repository Structure

- `Semantic_memory_pipeline/`: ontology construction, pruning, and validation utilities.
- `Explanations/`: causal-validation and Cohere-based candidate-generation experiments.

## Setup

Create the Conda environment:

```bash
conda env create -f environment.yml
conda activate ogwmm
```

Candidate generation uses Cohere. Create a local `.env` file and set the API key:

```bash
cp .env.example .env
```

```text
COHERE_API_KEY=your_key_here
```

## Reproduction

Run the Python test suite:

```bash
python -m pytest Explanations
```

Build the pruning module:

```bash
cd Semantic_memory_pipeline/Pruning
mvn -q package
```

Run the causal-validation benchmark:

```bash
python Explanations/src/scenarios/run_causal_validation_benchmark.py
```

Run the candidate-generation suite:

```bash
python Explanations/scripts/run_generation_suite.py --runs 3
python Explanations/scripts/aggregate_generation_suite.py
python Explanations/scripts/summarize_generation_run1.py
```

The main result files are stored in `Explanations/results/`:

- `causal_validation_benchmark.csv`
- `causal_validation_benchmark.md`
- `generation_suite/suite_summary.jsonl`
- `generation_suite/aggregates/`
- `generation_suite/run1_candidate_summary.md`

Raw generation outputs are written to `Explanations/outputs/` and are ignored by Git.
