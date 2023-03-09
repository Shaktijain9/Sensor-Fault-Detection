import pandas as pd
import numpy as np
import pymongo
import json
import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class EnvironmentVariables:
    load_dotenv()
    mongo_db_url: str = os.getenv("MONGO_DB_CONNECTION")


env_var = EnvironmentVariables()

mongo_client = pymongo.MongoClient(env_var.mongo_db_url)
