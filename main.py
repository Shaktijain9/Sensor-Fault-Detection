from sensor.pipeline import start_training_pipeline
from sensor.pipeline.batch_prediction import start_batch_prediction

if __name__ == "__main__":
    try:
        # start_training_pipeline()
        output_file_path = start_batch_prediction(
            input_file_path='/Users/shaktijain/PycharmProjects/Sensor-Fault-Detection/aps_failure_training_set1.csv')
        print(output_file_path)
    except Exception as e:
        raise e
