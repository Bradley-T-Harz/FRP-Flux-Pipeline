import pandas as pd
ics_file = (
    "../ICS-209-Plus_Datasets/"
    "ics209plus-wildfire/ics209plus-wildfire/"
    "ics209-plus-wf_incidents_1999to2020.csv"
)
df = pd.read_csv(
    ics_file,
    usecols=["INCIDENT_ID", "DISCOVERY_DATE", "FIRED_SIMPLE_FSR"],
    parse_dates=["DISCOVERY_DATE"]
)

top10 = (
    df.sort_values("FIRED_SIMPLE_FSR", ascending=False)
      .head(10)
      .rename(columns={
          "INCIDENT_ID": "fire_id",
          "DISCOVERY_DATE": "date_start"
      })
)
top10[["fire_id", "date_start"]].to_csv(
    "core_fires.csv",
    index=False,
    date_format="%Y-%m-%d"
)
print(f"Wrote core_fires.csv with {len(top10)} records")
