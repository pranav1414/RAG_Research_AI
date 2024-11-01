from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
import random
import csv
import pandas as pd
#
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Ensure the project3 directory is in the Python path
sys.path.insert(0, '/home/ec2-user/project3')  # Replace with the path to the project3 folder

# Import functions from scraping.py
from scraping import scrape_data, upload_to_s3, load_to_snowflake

# Define default_args for the DAG
default_args = {
    'owner': 'team9',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'cfa_scraping_dag',
    default_args=default_args,
    description='DAG to scrape CFA publications, upload to S3, and load to Snowflake',
    schedule_interval=timedelta(days=1),  # Set to the desired schedule
    start_date=datetime(2023, 10, 1),
    catchup=False,
) as dag:

    # Task 1: Scrape Data
    scrape_data_task = PythonOperator(
        task_id='scrape_data',
        python_callable=scrape_data
    )

    # Task 2: Upload to S3
    upload_to_s3_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3
    )

    # Task 3: Load to Snowflake
    load_to_snowflake_task = PythonOperator(
        task_id='load_to_snowflake',
        python_callable=load_to_snowflake
    )

    # Set task dependencies
    scrape_data_task >> upload_to_s3_task >> load_to_snowflake_task
