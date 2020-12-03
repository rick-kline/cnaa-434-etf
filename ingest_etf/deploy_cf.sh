#!/bin/bash

URL=ingest_etf_UR5VVLvlU1V75vqy4XJFBPFTK8YFJl84
echo $URL

gcloud functions deploy $URL --entry-point ingest_etf --runtime python37 --trigger-http --timeout 480s
