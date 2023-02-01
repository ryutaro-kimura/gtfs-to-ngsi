# makeOurCity
from typing import NamedTuple, TypedDict

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

app = FastAPI()


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


class GtfsStopTuple(NamedTuple):
    id: str
    type: str
    code: str
    name: str
    location: object
    operateBy: list


@app.get("/stops")
async def stop():
    df = pd.read_csv("./data/stops.txt", header=0)
    # print(df.iloc[0])
    try:
        for gtfs_stop in df.loc:
            ngsi_stop: GtfsStopTuple = {
                "id": "urn:ngsi-ld:GtfsStop:{}".format(gtfs_stop.stop_id),
                "type": "GtfsStop",
                "name": gtfs_stop.stop_name,
                "location": {
                    "type": gtfs_stop.location_type,
                    "coordinates": [gtfs_stop.stop_lat, gtfs_stop.stop_lon],
                },
                "operateBy": [
                    "urn:ngsi-ld:GtfsStop:{}".format(gtfs_stop.stop_id)
                ],
            }
            ngsi_stop_json = json.dumps(ngsi_stop, cls=NpEncoder)
            print(ngsi_stop_json)
            try:
                orion_endpoint = os.getenv("ORION_ENDPOINT")
                auth = get_auth()
                requests.post(
                    orion_endpoint + "/v2/entities?options=keyValues",
                    auth=auth,
                    data=ngsi_stop_json,
                    headers={"content-type": "application/json"},
                )
            except Exception as e:
                print("post exception：", e)

    except Exception as e:
        print("Error===", e)
    response = requests.get(
        orion_endpoint + "/v2/entities?type=GtfsStop&option=keyValue",
        auth=auth,
    )
    inOrion = json.dumps(response.json(), indent=2)

    return {"json": inOrion}
