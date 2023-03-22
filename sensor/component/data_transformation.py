import logging
import sys

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

from sensor.entity import artifact_entity
from sensor.entity import config_entity
from sensor import utils
from sensor.exception import SensorException
from sensor.config import TARGET_COLUMN
from sklearn.preprocessing import LabelEncoder
from imblearn.combine import SMOTETomek


class DataTransformation:
    def __init__(self, data_transformation_config: config_entity.DataTransformationConfig,
                 data_ingestion_artifact: artifact_entity.DataIngestionArtifact):
        logging.info("-------Data Transformation -------")
        try:
            self.data_transformation_config = data_transformation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise SensorException(e, sys)

    @classmethod
    def get_data_transformer_object(cls) -> Pipeline:
        try:
            simple_imputer = SimpleImputer(strategy='constant', fill_value=0)
            robust_scaler = RobustScaler()
            pipeline = Pipeline(steps=[
                ('Imputer', simple_imputer),
                ('RobustScaler', robust_scaler)
            ])
            return pipeline

        except Exception as e:
            raise SensorException(e, sys)

    def initiate_data_transformation(self, ) -> artifact_entity.DataTransformationArtifact:
        try:
            # Reading training & testing files
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)

            # Selecting input features
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN])
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN])

            # Selecting target features
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_test_df = test_df[TARGET_COLUMN]

            label_encoder = LabelEncoder()
            label_encoder.fit(target_feature_train_df)

            # Transformation on target column
            target_feature_train_arr = label_encoder.transform(target_feature_train_df)
            target_feature_test_arr = label_encoder.transform(target_feature_test_df)

            transformation_pipeline = DataTransformation.get_data_transformer_object()
            transformation_pipeline.fit(input_feature_train_df)

            # Transformation on input features
            input_feature_train_arr = transformation_pipeline.transform(input_feature_train_df)
            input_feature_test_arr = transformation_pipeline.transform(input_feature_test_df)

            smt = SMOTETomek(sampling_strategy='minority')
            logging.info(f'Before resampling input train size:{input_feature_train_arr.shape},'
                         f' target size:{target_feature_train_arr.shape}')

            logging.info(f'Before resampling input test size:{input_feature_test_arr.shape},'
                         f' target size:{target_feature_test_arr.shape}')

            input_feature_train_arr, target_feature_train_arr = smt.fit_resample(input_feature_train_arr,
                                                                                 target_feature_train_arr)

            logging.info(f'After resampling input size:{input_feature_train_arr.shape},'
                         f' target size:{target_feature_train_arr.shape}')

            input_feature_test_arr, target_feature_test_arr = smt.fit_resample(input_feature_test_arr,
                                                                               target_feature_test_arr)

            logging.info(f'After resampling input test size:{input_feature_test_arr.shape},'
                         f' target size:{target_feature_test_arr.shape}')

            # Target Encoder
            train_arr = np.c_[input_feature_train_arr, target_feature_train_arr]
            test_arr = np.c_[input_feature_test_arr, target_feature_test_arr]

            # Save numpy array
            utils.save_numpy_array_data(file_path=self.data_transformation_config.transformed_train_path,
                                        array=train_arr)
            utils.save_numpy_array_data(file_path=self.data_transformation_config.transformed_test_path,
                                        array=test_arr)

            # Save transformation objects
            utils.save_object(file_path=self.data_transformation_config.transformed_object_path,
                              obj=transformation_pipeline)
            utils.save_object(file_path=self.data_transformation_config.target_encoder_path,
                              obj=label_encoder)

            data_transformation_artifact = artifact_entity.DataTransformationArtifact(
                transformed_object_path=self.data_transformation_config.transformed_object_path,
                transformed_train_path=self.data_transformation_config.transformed_train_path,
                transformed_test_path=self.data_transformation_config.transformed_test_path,
                target_encoder_path=self.data_transformation_config.target_encoder_path
            )

            logging.info('Data Transformation Object Created.')
            return data_transformation_artifact

        except Exception as e:
            raise SensorException(e, sys)
