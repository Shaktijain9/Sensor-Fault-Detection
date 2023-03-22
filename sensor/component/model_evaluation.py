from sensor.predictor import ModelResolver
from sensor.entity import config_entity, artifact_entity
import os, sys
from sensor.exception import SensorException
from sensor.logger import logging
from sensor.utils import load_object
from sklearn.metrics import f1_score
import pandas as pd
import numpy as np
from sensor.config import TARGET_COLUMN


class ModelEvaluation:
    def __init__(self,
                 model_eval_config: config_entity.ModelEvaluationConfig,
                 data_ingestion_artifact: artifact_entity.DataIngestionArtifact,
                 data_transformation_artifact: artifact_entity.DataTransformationArtifact,
                 model_trainer_artifact: artifact_entity.ModelTrainerArtifact):
        try:
            logging.info("-------Model Evaluation -------")
            self.model_eval_config = model_eval_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_transformation_artifact = data_transformation_artifact
            self.model_trainer_artifact = model_trainer_artifact
            self.model_resolver = ModelResolver()
        except Exception as e:
            raise SensorException(e, sys)

    def initiate_model_evaluation(self) -> artifact_entity.ModelEvaluationArtifact:
        try:
            logging.info("Comparison of saved model & currently trained model.")
            # if saved model folder has any model saved then we'll compare
            # We'll compare whether the trained model is working better than the saved model or not
            latest_dir_path = self.model_resolver.get_latest_dir_path()
            if latest_dir_path is None:
                model_eval_artifact = artifact_entity.ModelEvaluationArtifact(is_model_accepted=True,
                                                                              improved_accuracy=None)
                logging.info(f"Returning Model Evaluation Artifact: {model_eval_artifact}")
                return model_eval_artifact

            # Finding location of transformer model & target encoder
            transformer_path = self.model_resolver.get_latest_transformer_path()
            model_path = self.model_resolver.get_latest_save_model_path()
            target_encoder_path = self.model_resolver.get_latest_encoder_path()

            # Loading Previously trained model objects
            logging.info("Loading previously trained models objects")
            transformer = load_object(file_path=transformer_path)
            model = load_object(file_path=model_path)
            target_encoder = load_object(file_path=target_encoder_path)

            # Currently trained model objects
            logging.info("Loading current models objects")
            current_transformers = load_object(file_path=self.data_transformation_artifact.transformed_object_path)
            current_model = load_object(file_path=self.model_trainer_artifact.model_path)
            current_target_encoder = load_object(file_path=self.data_transformation_artifact.target_encoder_path)

            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            target_df = test_df[TARGET_COLUMN]
            y_true = target_encoder.transform(target_df)

            # Accuracy using previously trained model
            input_arr = transformer.transform(test_df)
            y_pred = model.predict(input_arr)
            print(f"Prediction using previous model: {target_encoder.inverse_transform(y_pred[:5])}")

            previous_model_score = f1_score(y_true, y_pred)
            logging.info(f"Previous Model Score:{previous_model_score}")

            # Accuracy using current model
            input_arr_curr = current_transformers.transform(test_df)
            y_pred_curr = current_model.predict(input_arr_curr)
            print(f"Prediction using current model: {current_target_encoder.inverse_transform(y_pred_curr[:5])}")

            current_model_score = f1_score(y_true, y_pred_curr)
            logging.info(f"Current Model Score:{current_model_score}")

            if current_model_score < previous_model_score:
                raise Exception("Current trained model is not better than previous model.")
            accuracy_diff = current_model_score - previous_model_score
            model_eval_artifact = artifact_entity.ModelEvaluationArtifact(is_model_accepted=True,
                                                                          improved_accuracy=accuracy_diff)
            logging.info(f"Improved Accuracy : {accuracy_diff}")
            logging.info(f"Model Eval Artifact : {model_eval_artifact}")
            return model_eval_artifact






        except Exception as e:
            raise SensorException(e, sys)
