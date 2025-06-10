import os
from io import StringIO
import pandas as pd
import requests
from datetime import timedelta

MAP_KEY = os.getenv("FIRMS_MAP_KEY") or "c3a190311106b6395cdf0c6dcbe50820"
SOURCE  = "VIIRS_SNPP_NRT"

regions = {
    "estes_park":      "-105.6500,40.2000,-105.3500,40.5000",
    "romeo_region":    "-106.2349,36.9218,-105.7349,37.4218",
    "ute_reservations":"-108.2500,37.1250,-107.7500,37.6250",
    "trinidad_raton":  "-104.8000,37.0000,-103.2000,37.7500"
}

fires = pd.read_csv("core_fires.csv", parse_dates=["date_start", "date_end"])

for region, bbox in regions.items():
    # ensure folder exists
    os.makedirs(f"data/raw/{region}", exist_ok=True)

    for _, row in fires.iterrows():
        fid      = row["fire_id"]
        start_dt = row["date_start"]
        end_dt   = row["date_end"]
        days     = max(1, (end_dt - start_dt).days)
        date_str = start_dt.strftime("%Y-%m-%d")

        records = []
        times = pd.date_range(start_dt, end_dt, freq="12H")
        for t in times:
            t0 = t.isoformat() + "Z"
            t1 = (t + timedelta(hours=12)).isoformat() + "Z"
            url = (
                f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
                f"{MAP_KEY}/{SOURCE}/{bbox}/{days}/{date_str}"
            )
            resp = requests.get(url)
            resp.raise_for_status()
            df   = pd.read_csv(StringIO(resp.text))
            total_frp = df["frp"].sum()
            records.append({"time": t, "FRP_MW": total_frp})

        out = pd.DataFrame(records)
        safe_id = fid.replace(" ", "_").replace("/", "_")
        out_path = f"data/raw/{region}/fire_{safe_id}.csv"
        out.to_csv(out_path, index=False, date_format="%Y-%m-%dT%H:%M:%SZ")
        print(f"Wrote {out_path}")
