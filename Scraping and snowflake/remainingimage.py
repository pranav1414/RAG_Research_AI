# # remaining image insertion (s3 and snowflake)

# import os
# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# import boto3
# import snowflake.connector
# import time

# # AWS S3 setup
# s3 = boto3.client('s3',
#                   aws_access_key_id='',
#                   aws_secret_access_key='',
#                   region_name='us-east-1')

# BUCKET_NAME = 'testingbucketbig'

# # Snowflake connection details
# SNOWFLAKE_USER = 'Pranaav1392'
# SNOWFLAKE_PASSWORD = 'Pran@av1392'
# SNOWFLAKE_ACCOUNT = 'rghxtqa-yub04874'
# SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
# SNOWFLAKE_DATABASE = 'TEST_CFA_PUBLISH'
# SNOWFLAKE_SCHEMA = 'PUBLIC'
# SNOWFLAKE_TABLE = 'CFA_PUBLICATIONS_TABLE_TEST'

# # Initialize Snowflake connection
# def get_snowflake_connection():
#     return snowflake.connector.connect(
#         user=SNOWFLAKE_USER,
#         password=SNOWFLAKE_PASSWORD,
#         account=SNOWFLAKE_ACCOUNT,
#         warehouse=SNOWFLAKE_WAREHOUSE,
#         database=SNOWFLAKE_DATABASE,
#         schema=SNOWFLAKE_SCHEMA
#     )

# # Normalize folder names for flexible matching
# def normalize_name(name):
#     return name.replace(" ", "_").replace("-", "_").lower()

# # Check if the image already exists in S3 with flexible folder matching
# def image_exists_in_s3(folder_name, file_name):
#     normalized_folder_name = normalize_name(folder_name)
#     s3_key = f"{normalized_folder_name}/{file_name}"
#     try:
#         s3.head_object(Bucket=BUCKET_NAME, Key=s3_key)
#         print(f"[INFO] Image already exists in S3: {s3_key}")
#         return True
#     except s3.exceptions.ClientError:
#         return False

# # Function to upload image to S3 if it doesn't exist
# def upload_image_to_s3(image_url, folder_name):
#     file_name = os.path.basename(image_url)
#     print(f"[INFO] Attempting to upload {file_name} to S3 in folder {folder_name}")
#     if image_exists_in_s3(folder_name, file_name):
#         print(f"[INFO] Skipping upload for {file_name} as it already exists in S3.")
#         return f"https://{BUCKET_NAME}.s3.amazonaws.com/{normalize_name(folder_name)}/{file_name}"

#     try:
#         response = requests.get(image_url)
#         if response.status_code == 200:
#             s3_key = f"{normalize_name(folder_name)}/{file_name}"
#             s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=response.content)
#             print(f"[INFO] Uploaded {file_name} to S3: {s3_key}")
#             return f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
#         else:
#             print(f"[ERROR] Failed to download image from {image_url} (Status Code: {response.status_code})")
#     except Exception as e:
#         print(f"[ERROR] Exception while uploading image to S3: {e}")
#     return None

# # Update Snowflake with the image link if title exists
# def update_image_link_in_snowflake(title, image_link):
#     conn = get_snowflake_connection()
#     try:
#         with conn.cursor() as cursor:
#             normalized_title = title
#             update_query = f"""
#                 UPDATE {SNOWFLAKE_TABLE}
#                 SET image_link = %s
#                 WHERE title = %s AND image_link IS NULL
#             """
#             cursor.execute(update_query, (image_link, normalized_title))
#             conn.commit()
#             print(f"[INFO] Updated image link for title: {title}")
#     except Exception as e:
#         print(f"[ERROR] Exception while updating Snowflake: {e}")
#     finally:
#         conn.close()

# # Extract image URLs and titles from the listing URL, with handling for missing images and title normalization
# def extract_images_from_listing(url):
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#     driver.get(url)

#     # Incremental scroll to load all content
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     while True:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height

#     time.sleep(10)
#     # WebDriverWait(driver, 45).until(EC.presence_of_element_located((By.CLASS_NAME, "coveo-result-row")))

#     # Save page source for debugging
#     with open("debug_page_final.html", "w", encoding="utf-8") as f:
#         f.write(driver.page_source)
#     print("[DEBUG] Final page source saved for verification.")

#     soup = BeautifulSoup(driver.page_source, 'html.parser')

#     images_data = []
#     # books = soup.select("div.coveo-result-row")
#     books = soup.find_all("div", class_="coveo-list-layout CoveoResult")

#     for book in books:
#         title_tag = book.find("h4", class_="coveo-title")
#         image_tag = book.find("img", class_="coveo-result-image")

#         if title_tag:
#             title = title_tag.get_text(strip=True)
#             normalized_title = title.strip().lower()
#             print(f"[INFO] Found title: {title}")

#             if image_tag and image_tag['src']:
#                 image_url = image_tag['src']
#                 if image_url.startswith("/"):
#                     image_url = "https://rpc.cfainstitute.org" + image_url
#                 images_data.append((normalized_title, image_url))
#                 print(f"[INFO] Found image URL for title '{title}': {image_url}")
#             else:
#                 print(f"[WARNING] No image found for title: {title}")

#     driver.quit()
#     return images_data

# # Process the single provided URL
# def process_single_listing_url(url):
#     print(f"[INFO] Processing listing URL: {url}")
#     images_data = extract_images_from_listing(url)

#     for normalized_title, image_url in images_data:
#         folder_name = normalize_name(normalized_title)
#         image_link = upload_image_to_s3(image_url, folder_name)

#         if image_link:
#             update_image_link_in_snowflake(normalized_title, image_link)

# # Provided URL
# # listing_url = "https://rpc.cfainstitute.org/en/research-foundation/publications#first=80&sort=%40officialz32xdate%20descending"
# listing_url = "https://rpc.cfainstitute.org/en/research-foundation/publications#sort=%40officialz32xdate%20descending"

# # Run the process for the single URL
# process_single_listing_url(listing_url)













# # this is also working - 6th row entry
# # import os
# # import requests
# # from bs4 import BeautifulSoup
# # from selenium import webdriver
# # from selenium.webdriver.chrome.service import Service as ChromeService
# # from webdriver_manager.chrome import ChromeDriverManager
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from selenium.webdriver.common.by import By
# # import boto3
# # import snowflake.connector
# # import time

# # # AWS S3 setup
# # s3 = boto3.client('s3',
# #                   aws_access_key_id='AKIAQIJRSDTXXVW6DVT5',
# #                   aws_secret_access_key='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',
# #                   region_name='us-east-1')

# # BUCKET_NAME = 'testingbucketbig'

# # # Snowflake connection details
# # SNOWFLAKE_USER = 'Pranaav1392'
# # SNOWFLAKE_PASSWORD = 'Pran@av1392'
# # SNOWFLAKE_ACCOUNT = 'rghxtqa-yub04874'
# # SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
# # SNOWFLAKE_DATABASE = 'TEST_CFA_PUBLISH'
# # SNOWFLAKE_SCHEMA = 'PUBLIC'
# # SNOWFLAKE_TABLE = 'CFA_PUBLICATIONS_TABLE_TEST'

# # # Initialize Snowflake connection
# # def get_snowflake_connection():
# #     return snowflake.connector.connect(
# #         user=SNOWFLAKE_USER,
# #         password=SNOWFLAKE_PASSWORD,
# #         account=SNOWFLAKE_ACCOUNT,
# #         warehouse=SNOWFLAKE_WAREHOUSE,
# #         database=SNOWFLAKE_DATABASE,
# #         schema=SNOWFLAKE_SCHEMA
# #     )

# # # Normalize folder names for flexible matching
# # def normalize_name(name):
# #     return name.replace(" ", "_").replace("-", "_").lower()

# # # List all folders in S3 bucket
# # def list_s3_folders(bucket_name):
# #     response = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')
# #     folders = {normalize_name(prefix['Prefix'].strip('/')): prefix['Prefix'] for prefix in response.get('CommonPrefixes', [])}
# #     return folders

# # # Check if the image already exists in S3
# # def image_exists_in_s3(folder_path, file_name):
# #     s3_key = f"{folder_path}/{file_name}"
# #     try:
# #         s3.head_object(Bucket=BUCKET_NAME, Key=s3_key)
# #         print(f"[INFO] Image already exists in S3: {s3_key}")
# #         return True
# #     except s3.exceptions.ClientError:
# #         return False

# # # Function to upload image to S3 if it doesn't exist
# # def upload_image_to_s3(image_url, folder_path):
# #     file_name = os.path.basename(image_url)
# #     print(f"[INFO] Attempting to upload {file_name} to S3 in folder {folder_path}")
# #     if image_exists_in_s3(folder_path, file_name):
# #         print(f"[INFO] Skipping upload for {file_name} as it already exists in S3.")
# #         return f"https://{BUCKET_NAME}.s3.amazonaws.com/{folder_path}/{file_name}"

# #     try:
# #         response = requests.get(image_url)
# #         if response.status_code == 200:
# #             s3.put_object(Bucket=BUCKET_NAME, Key=f"{folder_path}/{file_name}", Body=response.content)
# #             print(f"[INFO] Uploaded {file_name} to S3: {folder_path}/{file_name}")
# #             return f"https://{BUCKET_NAME}.s3.amazonaws.com/{folder_path}/{file_name}"
# #         else:
# #             print(f"[ERROR] Failed to download image from {image_url} (Status Code: {response.status_code})")
# #     except Exception as e:
# #         print(f"[ERROR] Exception while uploading image to S3: {e}")
# #     return None

# # # Update Snowflake with the image link if title exists
# # def update_image_link_in_snowflake(title, image_link):
# #     conn = get_snowflake_connection()
# #     try:
# #         with conn.cursor() as cursor:
# #             update_query = f"""
# #                 UPDATE {SNOWFLAKE_TABLE}
# #                 SET image_link = %s
# #                 WHERE title = %s AND image_link IS NULL
# #             """
# #             cursor.execute(update_query, (image_link, title))
# #             conn.commit()
# #             print(f"[INFO] Updated image link for title: {title}")
# #     except Exception as e:
# #         print(f"[ERROR] Exception while updating Snowflake: {e}")
# #     finally:
# #         conn.close()

# # # Extract image URLs and titles from the listing URL
# # def extract_images_from_listing(url):
# #     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
# #     driver.get(url)

# #     # Incremental scroll to load all content
# #     last_height = driver.execute_script("return document.body.scrollHeight")
# #     while True:
# #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# #         time.sleep(2)
# #         new_height = driver.execute_script("return document.body.scrollHeight")
# #         if new_height == last_height:
# #             break
# #         last_height = new_height

# #     time.sleep(10)
# #     soup = BeautifulSoup(driver.page_source, 'html.parser')

# #     images_data = []
# #     books = soup.find_all("div", class_="coveo-list-layout CoveoResult")

# #     for book in books:
# #         title_tag = book.find("h4", class_="coveo-title")
# #         image_tag = book.find("img", class_="coveo-result-image")

# #         if title_tag:
# #             title = title_tag.get_text(strip=True)
# #             normalized_title = title.strip().lower()
# #             print(f"[INFO] Found title: {title}")

# #             if image_tag and image_tag['src']:
# #                 image_url = image_tag['src']
# #                 if image_url.startswith("/"):
# #                     image_url = "https://rpc.cfainstitute.org" + image_url
# #                 images_data.append((normalized_title, image_url))
# #                 print(f"[INFO] Found image URL for title '{title}': {image_url}")
# #             else:
# #                 print(f"[WARNING] No image found for title: {title}")

# #     driver.quit()
# #     return images_data

# # # Process the single provided URL
# # def process_single_listing_url(url):
# #     print(f"[INFO] Processing listing URL: {url}")
# #     images_data = extract_images_from_listing(url)

# #     # Get the list of available folders in S3 bucket
# #     available_folders = list_s3_folders(BUCKET_NAME)

# #     for normalized_title, image_url in images_data:
# #         # Check if folder exists in S3 for the title
# #         if normalized_title in available_folders:
# #             folder_path = available_folders[normalized_title]
# #             image_link = upload_image_to_s3(image_url, folder_path)

# #             if image_link:
# #                 update_image_link_in_snowflake(normalized_title, image_link)
# #         else:
# #             print(f"[WARNING] No matching folder found in S3 for title: {normalized_title}")

# # # Provided URL
# # listing_url = [
# # "https://rpc.cfainstitute.org/en/research-foundation/publications#first=10&sort=%40officialz32xdate%20descending",
# # "https://rpc.cfainstitute.org/en/research-foundation/publications#first=20&sort=%40officialz32xdate%20descending",
# # "https://rpc.cfainstitute.org/en/research-foundation/publications#first=30&sort=%40officialz32xdate%20descending",
# # "https://rpc.cfainstitute.org/en/research-foundation/publications#first=40&sort=%40officialz32xdate%20descending",
# # "https://rpc.cfainstitute.org/en/research-foundation/publications#first=50&sort=%40officialz32xdate%20descending",
# # "https://rpc.cfainstitute.org/en/research-foundation/publications#first=60&sort=%40officialz32xdate%20descending",
# # "https://rpc.cfainstitute.org/en/research-foundation/publications#first=70&sort=%40officialz32xdate%20descending",
# # "https://rpc.cfainstitute.org/en/research-foundation/publications#first=80&sort=%40officialz32xdate%20descending",
# # "https://rpc.cfainstitute.org/en/research-foundation/publications#first=90&sort=%40officialz32xdate%20descending",
# # ]
# # # Run the process for the single URL
# # process_single_listing_url(listing_url)




import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import boto3
import snowflake.connector
import time
from difflib import get_close_matches
from tenacity import retry, stop_after_attempt, wait_fixed

# AWS S3 setup
s3 = boto3.client('s3',
                  aws_access_key_id='AKIAQIJRSDTXXVW6DVT5',
                  aws_secret_access_key='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',
                  region_name='us-east-1')

BUCKET_NAME = 'testingbucketbig'

# Snowflake connection details
SNOWFLAKE_USER = 'Pranaav1392'
SNOWFLAKE_PASSWORD = 'Pran@av1392'
SNOWFLAKE_ACCOUNT = 'rghxtqa-yub04874'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
SNOWFLAKE_DATABASE = 'TEST_CFA_PUBLISH'
SNOWFLAKE_SCHEMA = 'PUBLIC'
SNOWFLAKE_TABLE = 'CFA_PUBLICATIONS_TABLE_TEST'

# Initialize Snowflake connection
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

# Normalize names
def normalize_name(name):
    return name.replace(" ", "_").replace("-", "_").lower()

# List all folders in S3 bucket
def list_s3_folders(bucket_name):
    response = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')
    folders = {normalize_name(prefix['Prefix'].strip('/')): prefix['Prefix'] for prefix in response.get('CommonPrefixes', [])}
    return folders

# Fuzzy match to find best S3 folder for a given title
def find_best_folder_match(normalized_title, available_folders):
    matches = get_close_matches(normalized_title, available_folders.keys(), n=1, cutoff=0.6)
    if matches:
        return available_folders[matches[0]]
    return None

# Check if the image already exists in S3
def image_exists_in_s3(folder_path, file_name):
    s3_key = f"{folder_path}/{file_name}"
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        print(f"[INFO] Image already exists in S3: {s3_key}")
        return True
    except s3.exceptions.ClientError:
        return False

# Retry mechanism for downloading images
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_image_data(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return response.content
    else:
        raise requests.exceptions.RequestException(f"Failed to download image: Status {response.status_code}")

# Function to upload image to S3 if it doesn't exist
def upload_image_to_s3(image_url, folder_path):
    file_name = os.path.basename(image_url)
    print(f"[INFO] Attempting to upload {file_name} to S3 in folder {folder_path}")
    s3_key = f"{folder_path}/{file_name}"

    if image_exists_in_s3(folder_path, file_name):
        print(f"[INFO] Skipping upload for {file_name} as it already exists in S3.")
        return f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

    try:
        image_data = fetch_image_data(image_url)
        s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=image_data)
        print(f"[INFO] Uploaded {file_name} to S3: {s3_key}")
        return f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    except Exception as e:
        print(f"[ERROR] Exception while uploading image to S3: {e}")
    return None

# Update Snowflake with the image link if title exists
def update_image_link_in_snowflake(title, image_link):
    conn = get_snowflake_connection()
    try:
        with conn.cursor() as cursor:
            update_query = f"""
                UPDATE {SNOWFLAKE_TABLE}
                SET image_link = %s
                WHERE title = %s AND image_link IS NULL
            """
            cursor.execute(update_query, (image_link, title))
            print(f"[DEBUG] Rows affected: {cursor.rowcount}")
        conn.commit()
        print(f"[INFO] Committed updates to Snowflake for title: {title}")
    except Exception as e:
        print(f"[ERROR] Exception while updating Snowflake: {e}")
    finally:
        conn.close()

# Extract image URLs and titles from the listing URL
def extract_images_from_listing(url):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)

    # Incremental scroll to load all content
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    images_data = []
    books = soup.find_all("div", class_="coveo-list-layout CoveoResult")

    for book in books:
        title_tag = book.find("h4", class_="coveo-title")
        image_tag = book.find("img", class_="coveo-result-image")

        if title_tag:
            title = title_tag.get_text(strip=True)
            normalized_title = title.strip().lower()
            print(f"[INFO] Found title: {title}")

            if image_tag and image_tag['src']:
                image_url = image_tag['src']
                if image_url.startswith("/"):
                    image_url = "https://rpc.cfainstitute.org" + image_url
                images_data.append((normalized_title, image_url))
                print(f"[INFO] Found image URL for title '{title}': {image_url}")
            else:
                print(f"[WARNING] No image found for title: {title}")

    return images_data

# Process the single provided URL
def process_single_listing_url(url):
    print(f"[INFO] Processing listing URL: {url}")
    images_data = extract_images_from_listing(url)

    # Get the list of available folders in S3 bucket
    available_folders = list_s3_folders(BUCKET_NAME)

    for normalized_title, image_url in images_data:
        # Find best folder match in S3 for the title
        folder_path = find_best_folder_match(normalized_title, available_folders)

        if folder_path:
            image_link = upload_image_to_s3(image_url, folder_path)
            if image_link:
                update_image_link_in_snowflake(normalized_title, image_link)
        else:
            print(f"[WARNING] No matching folder found in S3 for title: {normalized_title}")

# Provided URLs
listing_urls = [
    "https://rpc.cfainstitute.org/en/research-foundation/publications#first=10&sort=%40officialz32xdate%20descending",
    "https://rpc.cfainstitute.org/en/research-foundation/publications#first=20&sort=%40officialz32xdate%20descending",
    "https://rpc.cfainstitute.org/en/research-foundation/publications#first=30&sort=%40officialz32xdate%20descending",
    "https://rpc.cfainstitute.org/en/research-foundation/publications#first=40&sort=%40officialz32xdate%20descending",
    "https://rpc.cfainstitute.org/en/research-foundation/publications#first=50&sort=%40officialz32xdate%20descending",
    "https://rpc.cfainstitute.org/en/research-foundation/publications#first=60&sort=%40officialz32xdate%20descending",
    "https://rpc.cfainstitute.org/en/research-foundation/publications#first=70&sort=%40officialz32xdate%20descending",
    "https://rpc.cfainstitute.org/en/research-foundation/publications#first=80&sort=%40officialz32xdate%20descending",
    "https://rpc.cfainstitute.org/en/research-foundation/publications#first=90&sort=%40officialz32xdate%20descending",
]

# Loop through each URL and process it individually
for url in listing_urls:
    process_single_listing_url(url)
