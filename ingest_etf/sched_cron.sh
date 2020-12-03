#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: ./sched_cron.sh  destination-bucket-name compute-region ingest-url"
    echo "   eg: ./sched_cron.sh  cnaa-434-etf-data us-central1 ingest_etf_nt1JVXuQH1kFTj6knUPUqNYB4Q6aq7JU"
    exit
fi

PROJECT=$(gcloud config get-value project)
BUCKET=$1
REGION=$2
UPATH=$3

URL="https://${REGION}-${PROJECT}.cloudfunctions.net/${UPATH}"

echo {\"bucket\":\"${BUCKET}\"} > /tmp/message

gcloud pubsub topics create cron-topic
gcloud pubsub subscriptions create cron-sub --topic cron-topic

gcloud beta scheduler jobs create http etfMinute \
       --schedule="* * * * *" \
       --uri=$URL \
       --message-body-from-file=/tmp/message
