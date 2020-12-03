#!/bin/bash

URL=publish
REGION=us-central1
echo $URL
echo $REGION

gcloud functions deploy $URL --region $REGION --runtime python37 --trigger-http --timeout 480s