# makeOurCity

import numpy as np
from fastapi import FastAPI
import pandas as pd
import json
import os

import requests
from dotenv import load_dotenv
from pycognito.utils import RequestsSrpAuth
from requests.auth import AuthBase

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


def get_auth() -> AuthBase:
    auth = RequestsSrpAuth(
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        user_pool_id=os.getenv("USER_POOL_ID"),
        client_id=os.getenv("APP_CLIENT_ID"),
        user_pool_region=os.getenv("USER_POOL_REGION"),
    )
    return auth


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
    df = pd.read_csv("./data/stops.txt", header=0)
    # print(df.loc[0])
    test = {}
    try:
        for gtfs_stop in df.loc:
            # print (gtfs_stop)
            ngsi_stop = {
                "id": "urn:ngsi-ld:GtfsStop:{}".format(gtfs_stop.stop_id),
                "type": "GtfsStop",
                "code": "",
                # "code": gtfs_stop.stop_code,
                "name": gtfs_stop.name,
                "location": {
                    "type": gtfs_stop.location_type,
                    "coordinates": [gtfs_stop.stop_lat, gtfs_stop.stop_lon],
                },
                "operateBy": [
                    "urn:ngsi-ld:GtfsStop:{}".format(gtfs_stop.stop_id)
                ],
            }
            ngsi_stop_json = json.dumps(ngsi_stop, cls=NpEncoder)

            # １つだけPOSTしてみる
            if ngsi_stop["name"] == 4369:
                test = ngsi_stop_json
                print("test=====", test)  # ここは出力されてる
                orion_endpoint = os.getenv("ORION_ENDPOINT")
                auth = get_auth()
                try:
                    req = requests.post(
                        orion_endpoint + "/v2/entities?options=keyValues",
                        auth=auth,
                        data=test,
                        headers={"content-type": "application/json"},
                    )
                    print("req===", req)
                    print("req.json=====", req.json())
                    print("OK-------------")
                except Exception as e:
                    print("post exception：", e)

            # print("==",ngsi_stop_json)

    except Exception as e:
        print("Error===", e)

    # orion_endpoint = os.getenv("ORION_ENDPOINT")
    # auth = get_auth()
    # response = requests.get(orion_endpoint + "/v2/entities", auth=auth)
    response = requests.get(
        orion_endpoint + "/v2/entities?type=GtfsStop", auth=auth
    )
    inOrion = json.dumps(response.json(), indent=2)

    return {"name": inOrion}
