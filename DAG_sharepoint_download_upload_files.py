"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.models import Variable
import json


default_args = {
    'owner': 'rfaadmin',
    'depends_on_past': True,
    'start_date': datetime(2020, 12, 7, 15),
    'email': ['dev-alerts@rfa.com','airflow@rfa.opsgenie.net'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


dag = DAG(
    'sharepoint_download_upload', default_args=default_args, schedule_interval= '0 5 * * *',catchup=False)

client_id = Variable.get("client_id")
client_secret = Variable.get("client_secret")
config = {
      "tenant_name": "rfalab.com",
      "client_id": client_id,
      "client_secret": client_secret,
      "grant_type": "client_credentials",
      "scope": "https://graph.microsoft.com/.default",
      "site_name": "ExternalDev",
      "document_library": "TestdocsName"
    }
config = json.loads(str(config).replace("\'", "\""))


download_command = """
#!/bin/bash

~/.virtualenvs/sharepoint-document-library/bin/sharepoint-document-library --config "{}" --download_path ~/sharepoint_file_path/

""".format(config)


upload_command = """
#!/bin/bash

~/.virtualenvs/sharepoint-document-library/bin/sharepoint-document-library --config "{}" --upload_path ~/sharepoint_file_path/

""".format(config)


t_sharepoint_download = BashOperator(
    task_id='sharepoint_download',
    bash_command=download_command,
    retries=1,
    dag=dag)

t_sharepoint_upload = BashOperator(
    task_id='sharepoint_upload',
    bash_command=upload_command,
    retries=1,
    dag=dag)


t_sharepoint_download >> t_sharepoint_upload
