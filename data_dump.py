import pymongo
import pandas as pd
import json
from dotenv import load_dotenv
from sensor.config import mongo_client


print('Loading Environment variable from .env file.')
load_dotenv()
client = pymongo.MongoClient(
    mongo_client)


DATA_FILE_PATH = "aps_failure_training_set1.csv"
DATABASE_NAME = "APS"
COLLECTION_NAME = "Sensor"


def export_to_mongo():
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        print(f"Rows and columns: {df.shape}")

        # Convert dataframe to json so that we can dump these record in mongo db
        df.reset_index(drop=True, inplace=True)

        json_record = list(json.loads(df.T.to_json()).values())

        print("Records insertion started.")
        # insert converted json record to mongo db
        db = client[DATABASE_NAME]
        db[COLLECTION_NAME].insert_many(json_record)

        print("Records are inserted successfully.")

    except:
        raise "Something went wrong!!"


if __name__ == "__main__":
    export_to_mongo()
