# retail-demand-forecast

Retail demand forecasting project using the M5 Forecasting Accuracy dataset.

## Setup

1. Create and activate the virtual environment, then install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Add your `KAGGLE_API_TOKEN` to `.env`, then download the raw M5 dataset:
   ```bash
   python download_m5.py
   ```

3. Generate daily train/validation splits:
   ```bash
   python generate_daily_splits.py
   ```
