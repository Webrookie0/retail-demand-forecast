from pathlib import Path
import pandas as pd

base_dir = Path.cwd()
raw_dir = base_dir / "data" / "raw"
processed_dir = base_dir / "data" / "processed"
processed_dir.mkdir(parents=True, exist_ok=True)

sales = pd.read_csv(raw_dir / "sales_train_evaluation.csv")
calendar = pd.read_csv(raw_dir / "calendar.csv")

day_columns = [column for column in sales.columns if column.startswith("d_")]

# Sum unit sales across all products and stores for each day.
daily = (
    sales[day_columns]
    .sum()
    .rename_axis("d")
    .reset_index(name="units_sold")
    .merge(calendar[["d", "date"]], on="d", validate="one_to_one")
)

daily["date"] = pd.to_datetime(daily["date"])
daily = daily[["date", "units_sold"]].sort_values("date").reset_index(drop=True)

# The notebook's split is 1,913 training days and the final 28 validation days.
train = daily.iloc[:-28].copy()
validation = daily.iloc[-28:].copy()

train.to_csv(processed_dir / "train_daily_demand.csv", index=False)
validation.to_csv(processed_dir / "validation_daily_demand.csv", index=False)

print("Train:", train.shape, train["date"].min(), "to", train["date"].max())
print(
    "Validation:",
    validation.shape,
    validation["date"].min(),
    "to",
    validation["date"].max(),
)
