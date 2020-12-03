#!/bin/bash

URL=build_etf_model
REGION=us-central1
echo $URL
echo $REGION

gcloud functions deploy $URL --region $REGION --runtime python37 --trigger-topic build_etf_model --timeout 480s