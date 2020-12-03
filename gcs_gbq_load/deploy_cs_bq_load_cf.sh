#!/bin/bash

URL=gcs_gbq_load
REGION=us-central1
echo $URL
echo $REGION

gcloud functions deploy $URL --region $REGION --runtime python37 --trigger-topic load_etf_dataset --timeout 480s