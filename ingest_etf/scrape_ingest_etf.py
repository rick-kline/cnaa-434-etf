import csv
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from google.cloud.storage.blob import Blob
from google.cloud import storage
import yfinance as yf
import datetime
from datetime import datetime, timedelta
import os
import shutil
import logging
import os.path
import datetime
import tempfile
import base64
import json
from google.cloud import pubsub_v1
from dateutil.relativedelta import relativedelta
from pytz import timezone


def pub_bq_load_msg(file_to_load, bucket, store_path, project, region):
    REGION = region
    PROJECT_ID = project
    RECEIVING_FUNCTION = 'publish'
        
    function_url = f'https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{RECEIVING_FUNCTION}'
   
    if file_to_load == 'micro_cap_etf_lst.csv':
        table_name = "top_micro_cap_etf"        
    else:
        table_name = "etf_ytd_daily_summary"

    param = {"project":project,"region":region,"topic":"load_etf_dataset","message":{"tgt_dataset":"etf_dataset", "tgt_tbl_name":table_name, "bucket":bucket, "store_path":store_path}}
    data=json.dumps(param)
    logging.info('topic-message passed:{}'.format(data))
    
    r = requests.post(function_url, json=param) 
    logging.info('request post header:{} request post status:{}'.format(r.headers, r.status_code))   

def load_file_to_storage(bucketname, file_path, store_path, project, region):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucketname)
    data=bucket.blob(store_path)
    data.upload_from_filename(file_path)
    file_name = os.path.basename(file_path)
    logging.info('load_file_to_storage:file to trans={}'.format(file_name))
    
    # pub_bq_tran_msg (file_name, project, region)
    pub_bq_load_msg(file_name, bucketname, store_path, project, region) 
    
def get_hist_etf_price(bucket, destdir, file_loc, project, region):

    etf_sym_nm=pd.read_csv(file_loc)
    etf_ytd_close_summary = pd.DataFrame([])
    summary_file_name = "etf_ytd_close_summary.csv"
    os.chdir(destdir)
    file_path = os.path.join(destdir,summary_file_name)
    store_path = 'ytd_2020/raw/{}'.format(os.path.basename(file_path))
    
    # Set dates for data
    now = datetime.datetime.now(timezone('US/Eastern'))
    roll_one_yr = relativedelta(days=-365)
    hist_end = relativedelta(days=-1)

    hist_start_date = now + roll_one_yr
    hist_start_notm = pd.to_datetime(hist_start_date).date()
    hist_end_date = now + hist_end
    hist_end_notm = pd.to_datetime(hist_end_date).date()

    hist_start_dt = hist_start_notm.strftime("%Y-%m-%d")
    hist_end_dt = hist_end_notm.strftime("%Y-%m-%d")
    
    ####################################################################

    for i in range(len(etf_sym_nm)):
        sym = etf_sym_nm.loc[i, "Symbol"] 
        
        etf_tick = yf.Ticker(sym)

        etf_price_data = etf_tick.history(start=hist_start_dt, end =hist_end_dt, interval="1d" )

        etf_price_data['ticker'] = sym

        etf_ytd_close_summary = etf_ytd_close_summary.append(etf_price_data)

    etf_ytd_close_summary =  etf_ytd_close_summary.round(decimals=2)
    etf_ytd_close_summary.to_csv(file_path, index = 'True')
    load_file_to_storage(bucket, file_path, store_path, project, region)
    return file_path


def scrape_data(url, bucket, destdir, project, region):

    html = urlopen(url)
    file_name = 'micro_cap_etf_lst.csv'
    os.chdir(destdir)
    file_path = os.path.join(destdir,file_name)
    store_path = 'ytd_2020/raw/{}'.format(os.path.basename(file_path))
    
    soup = BeautifulSoup(html, features="lxml")

    column_headers = [th.text.strip() for th in 
                  soup.findAll('tr', limit=2)[0].findAll('th')]

    data_rows = soup.findAll('tr')[1:26]  # skip the first header rows

    etf_data = [[td.getText() for td in data_rows[i].findAll('td')]
            for i in range(len(data_rows))]
    
    etf_df = pd.DataFrame(etf_data, columns=column_headers)

    etf_sym_nm = etf_df.iloc[:, 0:2]

    etf_sym_nm.to_csv(file_path, index = False)

    load_file_to_storage(bucket, file_path, store_path, project, region)

    return file_path

def ingest(bucket, project, region):
    tempdir = tempfile.mkdtemp(prefix='ingest_etf')
    url = "https://etfdb.com/etfs/size/micro-cap"
    file_loc_sym = scrape_data(url,bucket,tempdir, project, region)
    file_loc_prc = get_hist_etf_price(bucket,tempdir, file_loc_sym, project, region)

    return file_loc_sym, file_loc_prc
    
 
if __name__=="__main__":
   #import argparse
   #parser = argparse.ArgumentParser(description='ingest etf data from etfdb.com website to Google Cloud Storage')
   #parser.add_argument('--bucket', help='GCS bucket to upload data to', required=True)
   #args = parser.parse_args()
   #ingest(args.bucket)
   ingest("cnaa-434-etf-data", "cnaa-434", "us-central1")