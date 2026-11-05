import json
import pandas as pd

def trend_frame(rows, parameter):
    out=[]
    for r in rows:
        for p in json.loads(r["parameters_json"]):
            if p.get("Parameter")==parameter:
                out.append({"Date":r["report_date"],"Value":p.get("Value"),"Status":p.get("Status")})
    return pd.DataFrame(out)
