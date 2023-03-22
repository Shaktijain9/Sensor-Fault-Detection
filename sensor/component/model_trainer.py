import logging
import sys

import numpy as np
from xgboost import XGBClassifier
from sensor.entity import artifact_entity
from sensor.entity import config_entity
from sensor import utils
from sensor.exception import SensorException
from sklearn.metrics import f1_score


class ModelTrainer:
    def __init__(self, model_trainer_config: config_entity.ModelTrainerConfig,
                 data_transformation_artifact: artifact_entity.DataTransformationArtifact):
        try:
            logging.info("-------Model Trainer -------")
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
            pass
        except Exception as e:
            raise SensorException(e, sys)

    def initiate_model_trainer(self) -> artifact_entity.ModelTrainerArtifact:
        try:

            logging.info('Loading Train/Test arrays from Data Transformation Artifacts.')
            train_arr = utils.load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_train_path)
            test_arr = utils.load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_test_path)

            logging.info("Splitting the Train/Test Arrays")
            X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            logging.info("Training the XGBoost Model")
            model = ModelTrainer.train_model(X=X_train, y=y_train)
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)

            logging.info("Calculating the Train-Test F1-Score")

            f1_train_score = f1_score(y_train, y_pred_train)
            logging.info(f"Train F1-Score: {f1_train_score}")

            f1_test_score = f1_score(y_test, y_pred_test)
            logging.info(f"Test F1-Score: {f1_test_score}")

            # Check for overfiting or uderfiting or expected score
            logging.info('Checking for Threshold Accuracy')
            if f1_test_score < self.model_trainer_config.expected_score:
                raise f'Model is not good as its not giving expected accuracy.' \
                      f' Model Accuracy: {f1_test_score}, Expected Accuracy: {self.model_trainer_config.expected_score}'

            diff = f1_train_score - f1_test_score

            logging.info('Checking for Overfitting & Underfitting conditions.')
            if abs(diff) > self.model_trainer_config.overfitting_threshold:
                raise "Model is showing some overfiting/underfiting issue." \
                      f"Current Accuracy Difference for train & test model : {diff}." \
                      f"Train Score: {f1_train_score}, Test Score: {f1_test_score}"

            logging.info("Saving the model.")
            # Save the trained model
            utils.save_object(self.model_trainer_config.model_path, model)

            logging.info("Preparing the Model Trainer Artifact")
            # Prepare the artifact
            model_trainer_artifact = artifact_entity.ModelTrainerArtifact(model_path=self.model_trainer_config.
                                                                          model_path, f1_test_score=f1_test_score,
                                                                          f1_train_score=f1_train_score)

            logging.info(f"Model Trainer Artifact : {model_trainer_artifact}")
            return model_trainer_artifact

        except Exception as e:
            raise SensorException(e, sys)

    @staticmethod
    def train_model(X, y):
        xgb_cls = XGBClassifier()
        xgb_cls.fit(X, y)
        return xgb_cls

    def fine_tune_model(self):
        try:
            # Code for GridSearchCV
            pass
        except Exception as e:
            raise "Some issue occurred during fine-tuning!!!"
