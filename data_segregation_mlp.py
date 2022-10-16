# -*- coding: utf-8 -*-
"""data_segregation_mlp.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eQ5LwMbIdIxWMRJ3NCNOsPF6pfvYZtuh
"""

!pip install wandb -qU

import wandb
wandb.login()

# import the necessary packages
from imutils import paths
import logging
import os
import cv2
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# configure logging
# reference for a logging obj
logger = logging.getLogger()

# set level of logging
logger.setLevel(logging.INFO)

# create handlers
c_handler = logging.StreamHandler()
c_format = logging.Formatter(fmt="%(asctime)s %(message)s",datefmt='%d-%m-%Y %H:%M:%S')
c_handler.setFormatter(c_format)

# add handler to the logger
logger.handlers[0] = c_handler

"""Segregação dos dados"""

# since we are using Jupyter Notebooks we can replace our argument
# parsing code with *hard coded* arguments and values
args = {
  "project_name": "second_image_classifier",
  "artifact_name_feature": "clean_data:latest",
  "artifact_name_target": "label:latest",
  "train_feature_artifact": "train_x",
  "train_target_artifact": "train_y",
  "test_feature_artifact": "test_x",
  "test_target_artifact": "test_y"
}

# open the W&B project created in the Fetch step
run = wandb.init(entity="gildson",project=args["project_name"], job_type="data_segregation")

logger.info("Downloading and reading clean data artifact")
clean_data = run.use_artifact(args["artifact_name_feature"])
clean_data_path = clean_data.file()

logger.info("Downloading and reading label data artifact")
label_data = run.use_artifact(args["artifact_name_target"])
label_data_path = label_data.file()

# unpacking the artifacts
data = joblib.load(clean_data_path)
label = joblib.load(label_data_path)

# partition the data into training and testing splits using 75% of
# the data for training and the remaining 25% for testing
(train_x, test_x, train_y, test_y) = train_test_split(data, label,test_size=0.25, random_state=42, stratify=label)

logger.info("Train x: {}".format(train_x.shape))
logger.info("Train y: {}".format(train_y.shape))
logger.info("Test x: {}".format(test_x.shape))
logger.info("Test y: {}".format(test_y.shape))

logger.info("Dumping the train and test data artifacts to the disk")

# Save the artifacts using joblib
joblib.dump(train_x, args["train_feature_artifact"])
joblib.dump(train_y, args["train_target_artifact"])
joblib.dump(test_x, args["test_feature_artifact"])
joblib.dump(test_y, args["test_target_artifact"])

# train_x artifact
artifact = wandb.Artifact(args["train_feature_artifact"],
                          type="TRAIN_DATA",
                          description="A json file representing the train_x"
                          )

logger.info("Logging train_x artifact")
artifact.add_file(args["train_feature_artifact"])
run.log_artifact(artifact)

# train_y artifact
artifact = wandb.Artifact(args["train_target_artifact"],
                          type="TRAIN_DATA",
                          description="A json file representing the train_y"
                          )

logger.info("Logging train_y artifact")
artifact.add_file(args["train_target_artifact"])
run.log_artifact(artifact)

# test_x artifact
artifact = wandb.Artifact(args["test_feature_artifact"],
                          type="TEST_DATA",
                          description="A json file representing the test_x"
                          )

logger.info("Logging test_x artifact")
artifact.add_file(args["test_feature_artifact"])
run.log_artifact(artifact)

# test_y artifact
artifact = wandb.Artifact(args["test_target_artifact"],
                          type="TEST_DATA",
                          description="A json file representing the test_y"
                          )

logger.info("Logging test_y artifact")
artifact.add_file(args["test_target_artifact"])
run.log_artifact(artifact)

run.finish()