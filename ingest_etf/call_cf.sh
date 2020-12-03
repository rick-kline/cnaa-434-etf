#!/bin/bash
if [ "$#" -ne 3 ]; then
    echo "Usage: ./call_cf.sh  destination-bucket-name compute-region ingest-url"
    echo "   eg: ./call_cf.sh  cnaa-434-etf-data us-central1 ingest_etf_opaOKsEXL8WaftrTeGJFFe9wYgnYMvfQ"
    exit
fi

PROJECT=$(gcloud config get-value project)
BUCKET=$1
REGION=$2
UPATH=$3

URL="https://${REGION}-${PROJECT}.cloudfunctions.net/${UPATH}"
echo $URL
echo {\"bucket\":\"${BUCKET}\"\,\"project\":\"${PROJECT}\"\,\"region\":\"${REGION}\"} > /tmp/message
cat /tmp/message
curl -X POST $URL -H "Content-Type:application/json" --data-binary @/tmp/message


