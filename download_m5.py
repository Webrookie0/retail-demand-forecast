import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

RAW_DIR = PROJECT_DIR / "data" / "raw"
COMPETITION = "m5-forecasting-accuracy"

REQUIRED_FILES = {
    "calendar.csv",
    "sales_train_evaluation.csv",
    "sell_prices.csv",
}

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Resolve kaggle CLI path or use KaggleApi
    kaggle_bin = shutil.which("kaggle")
    if not kaggle_bin:
        venv_kaggle = Path(sys.executable).parent / "kaggle"
        if venv_kaggle.exists():
            kaggle_bin = str(venv_kaggle)

    print(f"Downloading {COMPETITION} datasets into {RAW_DIR}...")
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        api.competition_download_files(COMPETITION, path=str(RAW_DIR), quiet=False)
    except Exception as err:
        print(f"Python Kaggle API encountered: {err}. Trying CLI fallback...")
        if not kaggle_bin:
            raise RuntimeError("kaggle CLI not found and KaggleApi failed.") from err
        subprocess.run(
            [
                kaggle_bin, "competitions", "download",
                "-c", COMPETITION,
                "-p", str(RAW_DIR),
            ],
            check=True,
            env=os.environ,
        )

    archives = list(RAW_DIR.glob("*.zip"))
    if not archives:
        raise FileNotFoundError(f"No downloaded ZIP archive found in {RAW_DIR}")

    # Extract to a temporary directory, then copy just the required CSVs.
    print("Extracting downloaded archives...")
    found = set()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        for archive_path in archives:
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(temp_dir)

        # Handle any nested zip files
        for nested in list(temp_dir.rglob("*.zip")):
            with zipfile.ZipFile(nested) as nested_archive:
                nested_archive.extractall(temp_dir)

        for csv_path in temp_dir.rglob("*.csv"):
            if csv_path.name in REQUIRED_FILES:
                shutil.copy2(csv_path, RAW_DIR / csv_path.name)
                found.add(csv_path.name)

    missing = REQUIRED_FILES - found
    if missing:
        raise FileNotFoundError(
            "Download/extraction completed, but these expected files "
            f"were not found: {', '.join(sorted(missing))}. "
            f"Check the archive contents in {RAW_DIR}."
        )

    print("M5 dataset files are ready:")
    for filename in sorted(REQUIRED_FILES):
        print(f"  {RAW_DIR / filename}")

if __name__ == "__main__":
    main()