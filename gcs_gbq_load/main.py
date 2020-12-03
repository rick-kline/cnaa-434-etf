import base64
import json
import os
import time
import logging
import requests
from google.cloud import bigquery
from google.cloud import pubsub_v1

# Triggered from a message on a Cloud Pub/Sub topic.
def gcs_gbq_load(event, context):
    # consume and manipulate data from Pub/Sub message
    if 'data' in event:
        name = base64.b64decode(event['data']).decode('utf-8')
        name_dict = json.loads(name)

        project = name_dict.get('data').get('project')
        region = name_dict.get('data').get('region')
        dataset = name_dict.get('data').get('message').get("tgt_dataset")
        table_name = name_dict.get('data').get('message').get("tgt_tbl_name")
        src_bucket = name_dict.get('data').get('message').get("bucket")
        src_store_path = name_dict.get('data').get('message').get("store_path")
        
     # Construct a BigQuery client object.
    client = bigquery.Client()

    # Set table_id to the ID of the table to create.
    # table_id = "your-project.your_dataset.your_table_name"
    table_id = project +"."+ dataset +"."+table_name
    uri = "gs://"+src_bucket+"/"+src_store_path

    #uri = "gs://cnaa-434-etf-data/ytd_2020/raw/micro_cap_etf_lst.csv"
    logging.info('table_id:{}'.format(table_id))
    logging.info('uri:{}'.format(uri))        

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
    )

    load_job = client.load_table_from_uri(
        uri, table_id, job_config=job_config
    )  # Make an API request.

    load_job.result()  # Waits for the job to complete.

    destination_table = client.get_table(table_id)  # Make an API request.
    print("Loaded {} rows.".format(destination_table.num_rows))

    # Publish message to build model after tables are loaded/updated.

    REGION = region
    PROJECT_ID = project
    RECEIVING_FUNCTION = 'publish'
    function_url = f'https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{RECEIVING_FUNCTION}'

    # only build model after daily summary prices have been loaded/updated to etf_dataset
    if table_name == 'etf_ytd_daily_summary':
        param = {"topic":"build_etf_model","message":"data_updated","project":project, "region": region}
        data=json.dumps(param)
        logging.info('topic-message passed:{}'.format(data))
        
        r = requests.post(function_url, json=param) 
        logging.info('request post header:{} request post status:{}'.format(r.headers, r.status_code))   

   