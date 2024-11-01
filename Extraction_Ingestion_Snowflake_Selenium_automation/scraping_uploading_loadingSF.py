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
import os
import requests
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError



#Scraping

def scrape_data():
    #Step-1, getting hrefs.
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Fullscreen mode
    options.add_argument("--headless")  # Uncomment to run in headless mode

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Open the webpage and wait for it to load
    url = "https://rpc.cfainstitute.org/en/research-foundation/publications#sort=%40officialz32xdate%20descending&f:SeriesContent=[Research%20Foundation]"
    driver.get(url)

    # Handle the cookie banner
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/a'))
        ).click()
        print("Cookie banner closed.")
    except TimeoutException:
        print("No cookie banner found.")

    # Wait for the pager element to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="CoveoPager"]'))
    )

    # Get the total number of pages
    pager = driver.find_element(By.XPATH, '/html/body/main/div/div[1]/div[2]/div/div[3]/div[5]')
    total_pages = int(pager.get_attribute('data-number-of-pages'))
    print(f"Total pages: {total_pages}")

    # Prepare to store data in a DataFrame
    data_list = []

    # Function to handle stale elements
    def safe_get_elements(xpath):
        try:
            return driver.find_elements(By.XPATH, xpath)
        except StaleElementReferenceException:
            print("Stale element encountered. Retrying...")
            time.sleep(2)
            return driver.find_elements(By.XPATH, xpath)



    # scraping oage 1
    elements = safe_get_elements('//h4/a')
    for element in elements:
        title = element.text
        link = element.get_attribute("href")
        print(f"Found: {title} - {link}")
        data_list.append({"Publication Title": title, "Publication Link": link})



    # Iterate through each page
    for page_number in range(1, total_pages + 2):
        print(f"Scraping page {page_number}...")
        time.sleep(3)  # Delay to simulate human behavior

        # Get titles and hrefs
        elements = safe_get_elements('//h4/a')
        for element in elements:
            title = element.text
            link = element.get_attribute("href")
            print(f"Found: {title} - {link}")
            data_list.append({"Publication Title": title, "Publication Link": link})
        
        
        # Navigate to the next page if not on the last one
        if page_number < total_pages+1:
            print(page_number)
            
            try:
                next_button = driver.find_element(
                    By.XPATH, f'/html/body/main/div/div[1]/div[2]/div/div[3]/div[5]/ul/li[{page_number+1}]/a'
                )
                print(page_number)
                next_button.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//h4/a'))
                )
                
            except TimeoutException:
                print("Next page took too long to load.")
                break
            

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(data_list)
    # Remove duplicate rows (if any)
    df = df.drop_duplicates()
    df.to_csv("CFA_Publications.csv", index=False, encoding="utf-8")
    print("Scraping completed.")

    # Close the browser
    driver.quit()








    # Step-2, detailed scraping from hrefs, title, summary, overview, images, pdfs

    # Set up Chrome driver (optional headless mode)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Uncomment for headless mode

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Load the CSV from Step 1
    df = pd.read_csv('CFA_Publications.csv')

    # Create folders for PDFs and Images if not already present
    os.makedirs("pdfs", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    # Prepare DataFrame to store scraped info
    scraped_data = []

    # Iterate over each publication link
    for index, row in df.iterrows():
        title = row['Publication Title']
        url = row['Publication Link']
        print(f"Scraping: {title} - {url}")

        try:
            driver.get(url)
            time.sleep(3)  # Allow page to load
            # Handle the cookie banner
            try:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/a'))
                ).click()
                print("Cookie banner closed.")
            except TimeoutException:
                print("No cookie banner found.")

            # # Scrape title
            # # //*[@id="contentarea"]/section[2]/div/div/div/h1
            # scraped_title = driver.find_element(By.XPATH, '//*[@id="contentarea"]/section[2]/div/div/div/h1').text
            # Scrape title
            # //*[@id="contentarea"]/section[2]/div/div/div/h1
            try:
                scraped_title = driver.find_element(By.XPATH, "//*[@id='contentarea']/section[2]/div/div/div/h1").text
                print(scraped_title)
            except NoSuchElementException:
                scraped_title = ""  # Leave blank if title is not found


            # Scrape brief summary
            # //*[@id="contentarea"]/section[3]/section/div/article/section[3]/span/p[1]
            # //*[@id="contentarea"]/section[3]/section/div/article/section[3]/span
            # Some pages don't have this information, write a try, expect loop
            # Scrape brief summary
            # Example for summary scraping with multiple XPath options
            summary = ''
            try:
                if driver.find_elements(By.XPATH, "//*[@id='contentarea']/section[3]/section/div/article/section[3]/span/p[1]"):
                    summary = driver.find_element(By.XPATH, "//*[@id='contentarea']/section[3]/section/div/article/section[3]/span/p[1]").text
                elif driver.find_elements(By.XPATH, "//*[@id='contentarea']/section[3]/section/div/article/section[3]/span"):
                    summary = driver.find_element(By.XPATH, "//*[@id='contentarea']/section[3]/section/div/article/section[3]/span").text
                print(summary)
                # Continue checking other paths as needed
            except Exception as e:
                print(f"Error scraping summary: {e}")



            # Scrape overview text from multiple tags
            overview = ""  # Initialize as an empty string to collect paragraphs
            overview_xpaths = [
                "//*[@id='contentarea']/section[3]/section/div/article/section[6]/div/p[1]",
                "//*[@id='contentarea']/section[3]/section/div/article/section[6]/div/p[2]",
                "//*[@id='contentarea']/section[3]/section/div/article/section[6]/div/p[3]",
                "//*[@id='contentarea']/section[3]/section/div/article/section[6]/div/p[4]",
                "//*[@id='contentarea']/section[3]/section/div/article/section[6]/div/p[5]",
                "//*[@id='contentarea']/section[3]/section/div/article/section[6]/div/p[6]",
                "//*[@id='contentarea']/section[3]/section/div/article/section[6]/div/p[7]",
                "//*[@id='contentarea']/section[3]/section/div/article/section[6]/div/p[8]",
                "//*[@id='contentarea']/section[3]/section/div/article/section[6]/div/p[9]",
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[1]",
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[2]",
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[3]",
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[4]",
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[4]", 
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[5]", 
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[6]", 
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[7]", 
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[8]", 
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[9]", 
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[10]", 
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[11]", 
                "//*[@id='contentarea']/section[3]/section/div/article/div[2]/p[12]"

            ]
            
            # Iterate through the list of XPaths to collect available overview paragraphs
            for xpath in overview_xpaths:
                try:
                    paragraph = driver.find_element(By.XPATH, xpath).text
                    if paragraph:  # Check if the paragraph has text
                        overview += paragraph + " "  # Append paragraph text with a space separator
                except NoSuchElementException:
                    # Skip if the element does not exist
                    continue
            
            overview = overview.strip()  # Remove any trailing whitespace
            print(overview)
                    


            # Initialize image_filename as None
            image_filename = None
            
            # Attempt to scrape image
            image_filename = ""  # Default to empty if no image is found
            try:
                image_element = driver.find_element(By.XPATH, "//*[@id='contentarea']/section[3]/section/div/article/section[5]/img")
                image_url = image_element.get_attribute('src')
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    image_filename = f"{title.replace(' ', '_').replace('/', '_')}_image.jpg"
                    full_image_path = f"scraped/images/{image_filename}"
                    with open(full_image_path, 'wb') as f:
                        f.write(image_response.content)
                    print(f"Image saved: {full_image_path}")
                else:
                    print("Image URL could not be accessed.")
            except (NoSuchElementException, requests.RequestException):
                print(f"No image found for {title} or failed to download the image.")
            
            # Attempt to scrape PDF
            pdf_filename = ""  # Default to empty if no PDF is found
            pdf_url = None
            pdf_xpaths = [
                "//*[@id='contentarea']/section[3]/section/div/article/section[4]/a[1]",
                "//*[@id='contentarea']/section[3]/section/div/article/section[3]/a",
                "//*[@id='contentarea']/section[3]/section/div/article/section[4]/a",
                "//*[@id='contentarea']/section[3]/section/div/article/section[5]/a"
            ]
            for xpath in pdf_xpaths:
                try:
                    pdf_element = driver.find_element(By.XPATH, xpath)
                    pdf_url = pdf_element.get_attribute('href')
                    if pdf_url:
                        pdf_response = requests.get(pdf_url)
                        if pdf_response.status_code == 200:
                            pdf_filename = f"{title.replace(' ', '_').replace('/', '_')}.pdf"
                            full_pdf_path = f"scraped/pdfs/{pdf_filename}"
                            with open(full_pdf_path, 'wb') as f:
                                f.write(pdf_response.content)
                            print(f"PDF saved: {full_pdf_path}")
                        else:
                            print("PDF URL could not be accessed.")
                        break  # Stop checking other xpaths if PDF is found
                except NoSuchElementException:
                    continue



            # Store scraped information in the list
            scraped_data.append({
                'Publication_Title': scraped_title,
                'Publication_Link': url,
                'Summary': summary,
                'Overview': overview,
                'Image_Path': full_image_path if image_filename else "",
                'PDF_Path': full_pdf_path if pdf_filename else "",
                'Image_Filename': image_filename,
                'PDF_Filename': pdf_filename
            })


        except Exception as e:
            print(f"Error scraping {title}: {e}")

    # Convert the scraped data into a DataFrame and save as CSV
    scraped_df = pd.DataFrame(scraped_data)
    scraped_df.to_csv('Detailed_Publications.csv', index=False, encoding='utf-8')
    print("Detailed scraping completed.")

    # Close the browser
    driver.quit()







# Transfering all files(psfs and images) to S3 bucket:  bigdata-team9
def upload_to_s3():
    import os
    import boto3
    from botocore.exceptions import NoCredentialsError, PartialCredentialsError

    # Set your S3 bucket name
    S3_BUCKET_NAME = 'bigdata-team9'
    S3_PARENT_FOLDER = 'scraped_raw'  # Folder in S3 to organize the upload

    # Local paths for the images and PDFs
    local_images_folder = '/Users/shubhamagarwal/Documents/Northeastern/Semester_3/project_3/scraping_cfainstitute/scraped/images'
    local_pdfs_folder = '/Users/shubhamagarwal/Documents/Northeastern/Semester_3/project_3/scraping_cfainstitute/scraped/pdfs'

    # Initialize an S3 client
    s3_client = boto3.client('s3')

    def upload_directory(folder_path, s3_bucket, s3_subfolder):
        for root, _, files in os.walk(folder_path):
            for file in files:
                local_file_path = os.path.join(root, file)
                # Set the S3 file path with parent folder and specific subfolder
                s3_file_path = f"{S3_PARENT_FOLDER}/{s3_subfolder}/{file}"
                
                try:
                    s3_client.upload_file(local_file_path, s3_bucket, s3_file_path)
                    print(f"Uploaded {file} to s3://{s3_bucket}/{s3_file_path}")
                except FileNotFoundError:
                    print(f"File not found: {local_file_path}")
                except NoCredentialsError:
                    print("Credentials not available.")
                except PartialCredentialsError:
                    print("Incomplete AWS credentials configuration.")

    # Upload images and PDFs
    upload_directory(local_images_folder, S3_BUCKET_NAME, 'images')
    upload_directory(local_pdfs_folder, S3_BUCKET_NAME, 'pdfs')

    print("All files uploaded to S3.")


# Moving the csv to snowflake
def load_to_snowflake():
    # Snowflake connection parameters
    conn_params = {
        'account': '',
        'user': '',
        'password': '',
        'warehouse': '',
        'database': 'TEAM9_DB',
        'schema': 'TEAM9_PROJECT3',
        'role': 'SYSADMIN'  # Use your appropriate role
    }

    # Establish a connection to Snowflake
    conn = snowflake.connector.connect(**conn_params)
    cursor = conn.cursor()

    # Create database and schema if they don't exist
    cursor.execute('CREATE OR REPLACE DATABASE PUBLICATIONS_DB')
    cursor.execute('CREATE OR REPLACE SCHEMA PUBLICATIONS_DB.PUBLICATIONS_SCHEMA')

    # Load the CSV file into a Pandas DataFrame
    csv_path = "Detailed_Publications.csv"
    df = pd.read_csv(csv_path)

    # Create a Snowflake table if not exists
    create_table_query = '''
    CREATE OR REPLACE TABLE PUBLICATIONS_SCHEMA.DETAILED_PUBLICATIONS (
        Publication_Title STRING,
        Publication_Link STRING,
        Summary STRING,
        Overview STRING,
        Image_Path STRING,
        PDF_Path STRING,
        S3_Image_Path STRING,
        S3_PDF_Path STRING
    )
    '''
    cursor.execute(create_table_query)

    # Write data to Snowflake in chunks for efficient handling
    for i, chunk in enumerate(df.to_records(index=False)):
        insert_query = f"INSERT INTO PUBLICATIONS_SCHEMA.DETAILED_PUBLICATIONS VALUES {str(tuple(chunk))}"
        cursor.execute(insert_query)

    print("CSV data successfully loaded into Snowflake.")

    # Close the cursor and connection
    cursor.close()
    conn.close()
