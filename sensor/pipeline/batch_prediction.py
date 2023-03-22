import os

import numpy as np

from sensor.logger import logging
from sensor.predictor import ModelResolver
import pandas as pd
from datetime import datetime
from sensor.utils import load_object

PREDICTION_DIR = 'prediction'


def start_batch_prediction(input_file_path):
    try:
        os.makedirs(PREDICTION_DIR, exist_ok=True)
        logging.info("Creating Model Resolver.")
        model_resolver = ModelResolver(model_registry='saved_models')
        logging.info(f"Reading file: {input_file_path}")
        prediction_file_name = os.path.basename(input_file_path).replace(
            ".csv", f"{datetime.now().strftime('%m%d%Y__%H%M__%S')}.csv")
        df = pd.read_csv(input_file_path)
        df.replace({"na": np.NAN}, inplace=True)


        # Validation code here...

        prediction_file_path = os.path.join(PREDICTION_DIR, prediction_file_name)

        logging.info(f"Loading Transformer to transform dataset.")
        transformer = load_object(file_path=model_resolver.get_latest_transformer_path())
        input_features_name = list(transformer.feature_names_in_)
        input_arr = df[input_features_name]

        logging.info("Loading model to make predictions")
        model = load_object(file_path=model_resolver.get_latest_model_path())
        prediction = model.predict(input_arr)

        logging.info("Loading Target Encoder to make target values")
        target_encoder = load_object(file_path=model_resolver.get_latest_encoder_path())
        categorical_predictions = target_encoder.inverse_transform(prediction)

        df['predictions'] = prediction
        df['true_predictions'] = categorical_predictions

        df.to_csv(prediction_file_path, index=False, header=True)
        return prediction_file_path






    except Exception as e:
        raise e
