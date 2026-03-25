from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_BRONZE_SOURCE_DIR = DATA_DIR / "edtech_raw_datasets_3_files"
EXTERNAL_BRONZE_SOURCE_DIR = Path("/data/edtech_raw_datasets_3_files")
BRONZE_SOURCE_DIR = (
    EXTERNAL_BRONZE_SOURCE_DIR if EXTERNAL_BRONZE_SOURCE_DIR.exists() else DEFAULT_BRONZE_SOURCE_DIR
)
SILVER_DIR = DATA_DIR / "silver"
SILVER_CSV_DIR = DATA_DIR / "silver_csv"

_BRONZE_DATASETS = {
    "leads": BRONZE_SOURCE_DIR / "leads_raw.csv",
    "learning": BRONZE_SOURCE_DIR / "learning_activity_raw.csv",
    "sales": BRONZE_SOURCE_DIR / "sales_raw.csv",
}

_SILVER_DATASETS = {
    "leads": SILVER_DIR / "leads",
    "learning": SILVER_DIR / "learning_activity",
    "sales": SILVER_DIR / "sales",
}


def bronze_dataset_path(dataset: str) -> Path:
    return _BRONZE_DATASETS[dataset]


def silver_dataset_path(dataset: str) -> Path:
    return _SILVER_DATASETS[dataset]
