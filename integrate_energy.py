import glob
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import trapezoid, simpson
from pandas.errors import EmptyDataError

def load_series(path):
    # 1) Read without parse_dates
    try:
        df = pd.read_csv(path)
    except EmptyDataError:
        print(f"  → Skipping empty file: {path}")
        return None

    if df.shape[0] == 0:
        print(f"  → Skipping zero-row file: {path}")
        return None

    # 2) Find which column is the datetime
    if "time" in df.columns:
        dt_col = "time"
    else:
        # assume first column is time
        dt_col = df.columns[0]
        df = df.rename(columns={dt_col: "time", df.columns[1]: "FRP_MW"})

    # 3) Convert to datetime & sort
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time")

    # 4) Compute elapsed hours from ignition
    df["hrs"] = (df["time"] - df["time"].iloc[0]) / pd.Timedelta("1h")
    return df

def energy_trap(df):
    return trapezoid(y=df["FRP_MW"], x=df["hrs"])

def energy_mid(df):
    hrs = df["hrs"].values; frp = df["FRP_MW"].values
    frp = df["FRP_MW"].values
    mids = (frp[1:] + frp[:-1]) / 2
    return np.sum(frp[:-1] * np.diff(hrs))

def energy_simp(df):
    return simpson(y=df["FRP_MW"], x=df["hrs"])

# Find all CSVs
paths = glob.glob("data/raw/*/fire_*.csv")
print(f"Found {len(paths)} FRP CSVs to integrate.")

results = []
for p in paths:
    df = load_series(p)
    if df is None:
        continue
    fire_name = os.path.basename(p).replace(".csv", "")
    results.append({
        "fire": fire_name,
        "trapezoid": energy_trap(df),
        "midpoint":  energy_mid(df),
        "simpson":   energy_simp(df)
    })

res = pd.DataFrame(results).set_index("fire")

# save summary
res.to_csv("energy_summary.csv")
print("Wrote energy_summary.csv")

# quick bar chart
res.plot(kind="bar", figsize=(10,6))
plt.ylabel("Total Energy (MJ)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("energy_comparison.png", dpi=200)
plt.show()
