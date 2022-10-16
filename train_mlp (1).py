# -*- coding: utf-8 -*-
"""train_mlp.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Q8ydAp6lhMnzqx4cXG7rh_Xu_UYNUKqI
"""

!pip install wandb --upgrade

import wandb
wandb.login()

# import the necessary packages
from imutils import paths
import logging
import os
import cv2
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier

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

# since we are using Jupyter Notebooks we can replace our argument
# parsing code with *hard coded* arguments and values
args = {
  "project_name": "second_image_classifier",
  "train_feature_artifact": "train_x:latest",
  "train_target_artifact": "train_y:latest",
  "encoder": "target_encoder",
  "inference_model": "model"
}

# open the W&B project created in the Fetch step
run = wandb.init(entity="gildson",project=args["project_name"], job_type="Train")

logger.info("Downloading the training data")
train_x_artifact = run.use_artifact(args["train_feature_artifact"])
train_x_path = train_x_artifact.file()
train_y_artifact = run.use_artifact(args["train_target_artifact"])
train_y_path = train_y_artifact.file()

global train_x
global train_y
# unpacking the artifacts
train_x = joblib.load(train_x_path)
train_y = joblib.load(train_y_path)

sweep_config = {
    'method': 'random',
    'metric': {
      'name': 'val_accuracy',
      'goal': 'maximize'   
    },
    'parameters': {
    'solver': {
        'values': ['adam', 'sgd']
        },
    'max_iter': {
        'values': [100, 200]
        },
    'activation': {
        'values': ['relu', 'tanh']
        },
     'hidden_layer_sizes': {
          'values': [(10,5), (20,10)]
        },
      'learn_rate': {
          'values': [0.01,0.001,0.005],  
        },
    }
}

sweep_id = wandb.sweep(sweep=sweep_config, entity='gildson', project=args["project_name"])

def train():
  with wandb.init() as run:
    # encode the labels as integers
    le = LabelEncoder()
    train_y = le.fit_transform(train_y)

    logger.info("[INFO] training MLP classifier...")
    model = MLPClassifier(hidden_layer_sizes=run.config.hidden_layer_sizes,
                          max_iter=run.config.max_iter,
                          solver=run.config.solver,
                          activation=run.config.activation,
                          random_state=1,
                          verbose=True)
    model.fit(train_x, train_y)

wandb.agent(sweep_id=sweep_id, function=train, count=3)

logger.info("Dumping the model and encoder artifacts to the disk")

# Save the artifacts using joblib
joblib.dump(le, args["encoder"])
joblib.dump(model, args["inference_model"])

# encoder artifact
artifact = wandb.Artifact(args["encoder"],
                          type="INFERENCE_MODEL",
                          description="A json file representing the target encoder"
                          )

logger.info("Logging the target encoder artifact")
artifact.add_file(args["encoder"])
run.log_artifact(artifact)

# inference model artifact
artifact = wandb.Artifact(args["inference_model"],
                          type="INFERENCE_MODEL",
                          description="A json file representing the inference model"
                          )

logger.info("Logging the inference model artifact")
artifact.add_file(args["inference_model"])
run.log_artifact(artifact)

run.finish()