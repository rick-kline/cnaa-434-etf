import logging
from flask import escape
from scrape_ingest_etf import *
 
def ingest_etf(request):
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
        json = request.get_json(force=True)

        bucket = escape(json['bucket'])
        project = escape(json['project'])
        region =  escape(json['region'])
        
        logging.info('ingest bucket={} project={} region={}'.format(bucket, project, region))
        file_loc_sym, file_loc_prc = ingest(bucket, project, region)
        
        logging.info('Success ... sym file ingested={} price file ingested={}'.format(file_loc_sym, file_loc_prc))