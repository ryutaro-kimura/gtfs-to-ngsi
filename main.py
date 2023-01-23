import pandas as pd
from fastapi import FastAPI
import json
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

app = FastAPI()
@app.get("/stops")
async def stop():
  df = pd.read_csv('./stops.txt', header=0)
  print(df.loc[0])
  ngsi_stops = []
  try:
    for gtfs_stop in df.loc:
      # print (gtfs_stop)
      ngsi_stop = {
        'id': "urn:ngsi-ld:GtfsStop:{}".format(gtfs_stop.stop_id),
        "type": "GtfsStop",
        "code": gtfs_stop.stop_code,
        "name": gtfs_stop.name,
        "location": {
          "type": gtfs_stop.location_type,
          "coordinates": [gtfs_stop.stop_lat, gtfs_stop.stop_lon]
        },
        "operateBy": ["urn:ngsi-ld:GtfsStop:{}".format(gtfs_stop.stop_id)]
      }
      ngsi_stop_json = json.dumps(ngsi_stop, cls=NpEncoder)
      print("====",ngsi_stop_json)
      ngsi_stops.append(ngsi_stop)

  except Exception as e:
    
    print(e)

  print(type(ngsi_stops))
  data = json.dumps(ngsi_stops, cls=NpEncoder)
  return {"name":data}
