# LEARN Corporation Data Engineer Assignment

This repository contains a local PySpark medallion pipeline for the LEARN Corporation Data Engineer technical assignment.

The pipeline reads three raw Bronze source files, standardizes them into trusted Silver datasets, and produces a Gold `student_360` table for downstream business use.

## Project Goal

Build a student-level analytics table from three source systems:

- `leads`: CRM and acquisition data
- `learning_activity`: learner engagement data
- `sales`: observed monetization data

Final Gold output:

- `student_360`
- grain = one row per `student_code`

## Repository Structure

```text
.
├── data/
│   ├── edtech_raw_datasets_3_files/   # Bronze source files (CSV)
│   ├── silver/                        # Silver outputs (Parquet)
│   └── gold/                          # Gold outputs (Parquet)
├── docs/
│   └── Learn Corporation - Assignment for Data Engineer position.pptx
├── jobs/
│   ├── silver.py                      # Bronze -> Silver job
│   └── gold.py                        # Silver -> Gold job
├── notebooks/
│   ├── bronze_inspection.ipynb        # notebook-first Bronze/Silver exploration
│   └── gold_student_360.ipynb         # notebook-first Gold logic exploration
├── transform/
│   ├── leads.py
│   ├── learning.py
│   ├── sales.py
│   └── gold.py
├── utils/
│   ├── paths.py
│   ├── readers.py
│   └── spark.py
└── pipeline.py                        # end-to-end pipeline entrypoint
```

## Data Layers

### Bronze

Bronze is the raw source directory:

- `data/edtech_raw_datasets_3_files/leads_raw.csv`
- `data/edtech_raw_datasets_3_files/learning_activity_raw.csv`
- `data/edtech_raw_datasets_3_files/sales_raw.csv`

These files are read as raw CSV source data.

### Silver

Silver creates trusted, joinable datasets:

- `data/silver/leads`
- `data/silver/learning_activity`
- `data/silver/sales`

Key Silver logic:

- `leads`
  - trim `student_code`
  - normalize phone numbers
  - normalize `source_channel`
  - standardize `lead_created_at`
  - keep latest lead record per `student_code`
- `learning_activity`
  - trim `student_code`
  - standardize `event_time`
  - normalize `event_name`
  - cast `duration_minutes`
  - drop invalid rows
- `sales`
  - trim keys
  - standardize `order_date`
  - keep qualifying successful transactions
  - preserve trusted monetization records for downstream analysis

### Gold

Gold produces:

- `data/gold/student_360`

`student_360` uses `leads_silver` as the base table, aggregates `learning_silver` and `sales_silver` to student level, then left joins both back to the lead population.

Main Gold sections:

- Identity
- Acquisition
- Learning
- Monetization
- Action

Main derived business fields:

- `engagement_segment`
- `risk_flag`
- `lead_priority_score`
- `lead_priority_band`

## Environment

This project is intended to run in WSL with `uv`.

Python dependencies are managed with:

```bash
uv sync
```

If your WSL environment injects cluster Spark settings such as `SPARK_HOME`, `HADOOP_CONF_DIR`, or `SPARK_CONF_DIR`, unset them before running local jobs:

```bash
env -u SPARK_HOME -u HADOOP_CONF_DIR -u SPARK_CONF_DIR uv run python pipeline.py --stage all
```

## How To Run

### Run the full pipeline

```bash
uv run python pipeline.py --stage all
```

This runs:

1. Bronze CSV -> Silver Parquet
2. Silver Parquet -> Gold Parquet

### Run only Silver

```bash
uv run python pipeline.py --stage silver
```

### Run only Gold

```bash
uv run python pipeline.py --stage gold
```

### Run job modules directly

Silver:

```bash
uv run python -m jobs.silver --dataset all --output-format parquet
```

Gold:

```bash
uv run python -m jobs.gold
```

## Notebook Workflow

The project was developed notebook-first and then moved into Python modules.

Useful notebooks:

- `notebooks/bronze_inspection.ipynb`
  - raw Bronze inspection
  - Silver transformation exploration
- `notebooks/gold_student_360.ipynb`
  - Gold aggregation logic
  - business field design

## Assumptions and Interpretation Notes

These assumptions matter for the business logic:

- `student_code` is the conformed key across all sources.
- Gold uses `leads_silver` as the base population.
- Missing sales records are not interpreted as proof that a student never purchased historically.
- The provided `sales` source is treated as observed monetization from the available dataset, not guaranteed full lifetime purchase history.
- `trial_course` is not counted in paid monetization metrics.
- `risk_flag` is interpreted as disengagement risk, based primarily on engagement behavior and lead age.
- `lead_priority_score` is treated as an action-priority score, not a pure engagement score.

## Outputs

After a successful run, expected output locations are:

- Silver
  - `data/silver/leads`
  - `data/silver/learning_activity`
  - `data/silver/sales`
- Gold
  - `data/gold/student_360`

All pipeline outputs are written as Parquet.

## Main Entry Point

The main runnable entry point for the project is:

- `pipeline.py`

Supporting code is organized into:

- `jobs/`
- `transform/`
- `utils/`

This keeps the pipeline easier to read, test, and explain than putting all logic into one file.
