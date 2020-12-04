
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
from google.cloud import bigquery
import pandas as pd
import google.auth
import json
import base64
import logging
from google.cloud import pubsub_v1

# Triggered from a message on a Cloud Pub/Sub topic.
def build_etf_model(event, context):
    # consume and manipulate data from Pub/Sub message
    if 'data' in event:
        name = base64.b64decode(event['data']).decode('utf-8')
        name_dict = json.loads(name)

        project = name_dict.get('data').get('project')
        region = name_dict.get('data').get('region')

    # Set dates for data
    now = datetime.now(timezone('US/Eastern'))
    roll_one_yr = relativedelta(days=-365)
    train_end = relativedelta(days=-1)

    train_start_date = now + roll_one_yr
    train_start_notm = pd.to_datetime(train_start_date).date()
    train_end_date = now + train_end
    train_end_notm = pd.to_datetime(train_end_date).date()

    train_strt_str = train_start_notm.strftime("%Y-%m-%d")
    train_end_str = train_end_notm.strftime("%Y-%m-%d")

    credentials, project = google.auth.default(
        scopes=['https://www.googleapis.com/auth/bigquery']
        )

    client = bigquery.Client(
        project = project,
        credentials=credentials
    )
    
    # Build model
    train_query = """
    CREATE OR REPLACE MODEL """ + "`"+ project + "`"+ """.etf_models.etf_price_forecast
    OPTIONS(model_type='ARIMA',
            time_series_data_col='close_trade_price',
            time_series_timestamp_col='close_date',
            time_series_id_col='etf_symbol') AS
    SELECT etf_symbol
            , CAST(close_date AS TIMESTAMP) AS close_date
        , close_trade_price
    FROM  """ + "`"+ project + "`"+ """.etf_dataset.etf_ytd_daily_summary
    WHERE close_date BETWEEN """ + "'" + train_strt_str + "'" + """ AND """ + "'" + train_end_str +"'" +"""
    ORDER BY close_date """

    client.query(train_query)







