# import os
# import re
# import requests
# from urllib.parse import urljoin
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# import boto3
# import snowflake.connector

# # AWS S3 setup
# s3 = boto3.client('s3',
#                   aws_access_key_id='',
#                   aws_secret_access_key='',
#                   region_name='us-east-1')

# # Snowflake connection details
# SNOWFLAKE_USER = 'Pranaav1392'
# SNOWFLAKE_PASSWORD = ''
# SNOWFLAKE_ACCOUNT = 'rghxtqa-yub04874'
# SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
# SNOWFLAKE_DATABASE = 'TEST_CFA_PUBLISH'
# SNOWFLAKE_SCHEMA = 'PUBLIC'
# SNOWFLAKE_TABLE = 'CFA_PUBLICATIONS_TABLE_TEST'

# # S3 bucket name
# BUCKET_NAME = 'testingbucketbig'

# # Local folder to store PDFs and images temporarily before uploading
# LOCAL_FOLDER = r'C:\bigdata3\contents_test'

# # Sanitize folder names for Windows compatibility
# def sanitize_folder_name(name):
#     name = re.sub(r'[\n\r\t]', ' ', name)
#     name = re.sub(r'[<>:"/\\|?*]', '', name)
#     name = re.sub(r'\s+', ' ', name).strip()
#     return name

# # Function to upload to S3
# def upload_to_s3(file_path, s3_folder_name):
#     try:
#         s3_key = f"{s3_folder_name}/{os.path.basename(file_path)}"
#         s3.upload_file(file_path, BUCKET_NAME, s3_key)
#         s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
#         print(f"Uploaded {file_path} to S3: {s3_url}")
#         return s3_url
#     except Exception as e:
#         print(f"Error uploading to S3: {e}")
#         return None

# # Function to extract title from the URL
# def extract_title(url):
#     print(f"Extracting title from {url}")
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#     driver.get(url)
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "spotlight-hero__title")))

#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     driver.quit()

#     title_tag = soup.find("h1", class_="spotlight-hero__title")
#     title = title_tag.get_text(strip=True) if title_tag else None
#     return title

# # Function to scrape PDF and image links from a content URL
# def scrape_content_links(url, listing_page_soup=None):
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#     driver.get(url)
    
#     pdf_link, image_link = None, None
    
#     try:
#         WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        
#         links = driver.find_elements(By.TAG_NAME, "a")
#         for link in links:
#             href = link.get_attribute("href")
#             if href and href.lower().endswith(".pdf"):
#                 pdf_link = urljoin(url, href)
#                 break

#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         image_tag = soup.find("img", class_="article-cover")
#         if image_tag:
#             image_link = urljoin(url, image_tag['src'])

#         # Use listing page as fallback if no image found on content page
#         if not image_link and listing_page_soup:
#             image_tag_listing = listing_page_soup.find("img", class_="coveo-result-image")
#             if image_tag_listing:
#                 image_link = urljoin(url, image_tag_listing['src'])
#                 print("Using image from listing page as fallback.")

#     except Exception as e:
#         print(f"Error scraping links from {url}: {e}")
#     finally:
#         driver.quit()
    
#     return pdf_link, image_link

# # Function to download and upload content to S3
# def download_and_upload_content(content_url, folder_name, content_type):
#     try:
#         response = requests.get(content_url)
#         if response.status_code == 200:
#             local_folder = os.path.join(LOCAL_FOLDER, folder_name)
#             os.makedirs(local_folder, exist_ok=True)
#             file_extension = ".pdf" if content_type == "pdf" else ".jpg"
#             file_path = os.path.join(local_folder, f"{folder_name}{file_extension}")
            
#             with open(file_path, "wb") as file:
#                 file.write(response.content)
            
#             s3_url = upload_to_s3(file_path, folder_name)
#             return s3_url
#         else:
#             print(f"Failed to download {content_type} from {content_url}")
#             return None
#     except Exception as e:
#         print(f"Error downloading {content_type}: {e}")
#         return None

# # Snowflake insert or update function
# def insert_or_update_snowflake(title, pdf_url, image_url):
#     try:
#         conn = snowflake.connector.connect(
#             user=SNOWFLAKE_USER,
#             password=SNOWFLAKE_PASSWORD,
#             account=SNOWFLAKE_ACCOUNT,
#             warehouse=SNOWFLAKE_WAREHOUSE,
#             database=SNOWFLAKE_DATABASE,
#             schema=SNOWFLAKE_SCHEMA
#         )
#         cursor = conn.cursor()
        
#         check_query = f"SELECT COUNT(*) FROM {SNOWFLAKE_TABLE} WHERE TITLE = %s;"
#         cursor.execute(check_query, (title,))
#         result = cursor.fetchone()
        
#         if result[0] == 0:
#             insert_query = f"""
#                 INSERT INTO {SNOWFLAKE_TABLE} (TITLE, PDF_LINK, IMAGE_LINK)
#                 VALUES (%s, %s, %s);
#             """
#             cursor.execute(insert_query, (title, pdf_url, image_url))
#             print(f"Inserted new record for {title}")
#         else:
#             update_query = f"""
#                 UPDATE {SNOWFLAKE_TABLE}
#                 SET PDF_LINK = %s, IMAGE_LINK = %s
#                 WHERE TITLE = %s;
#             """
#             cursor.execute(update_query, (pdf_url, image_url, title))
#             print(f"Updated existing record for {title}")
        
#         conn.commit()
#         cursor.close()
#         conn.close()
#         print(f"Completed Snowflake operation for {title}")
        
#     except Exception as e:
#         print(f"Error updating Snowflake for {title}: {e}")

# # Function to gather content URLs from listing URLs
# def gather_content_urls_from_listing(listing_urls):
#     content_urls = []
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#     try:
#         for url in listing_urls:
#             driver.get(url)
#             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "result-link")))
#             soup = BeautifulSoup(driver.page_source, 'html.parser')
#             links = soup.select("a.result-link")
#             for link in links:
#                 href = link.get("href")
#                 if href:
#                     content_urls.append((urljoin(url, href), soup))  # Store content URL with listing page soup
#     except Exception as e:
#         print(f"Error gathering content URLs from listings: {e}")
#     finally:
#         driver.quit()
    
#     return content_urls

# # Main processing function for content URLs
# def process_content_urls(content_urls):
#     if not content_urls:
#         print("No content URLs were gathered. Please check the listing URLs.")
#         return
    
#     for url, listing_page_soup in content_urls:
#         title = extract_title(url)
#         if not title:
#             print(f"Could not extract title from {url}")
#             continue
        
#         folder_name = sanitize_folder_name(title)
#         print(f"Processing {title} from {url}")
        
#         pdf_url, image_url = scrape_content_links(url, listing_page_soup)
        
#         if not image_url:
#             print(f"No image found for {title}")

#         s3_pdf_url = download_and_upload_content(pdf_url, folder_name, "pdf") if pdf_url else None
#         s3_image_url = download_and_upload_content(image_url, folder_name, "image") if image_url else None
        
#         insert_or_update_snowflake(title, s3_pdf_url, s3_image_url)

# # Main Execution
# content_urls = [
#     # Add your 100 content URLs here
# # 1st Page
#     "https://rpc.cfainstitute.org/research/foundation/2024/beyond-active-and-passive-investing",
#     "https://rpc.cfainstitute.org/research/foundation/2024/investment-model-validation",
#     "https://rpc.cfainstitute.org/research/foundation/2024/economics-of-private-equity",
#     "https://rpc.cfainstitute.org/research/foundation/2024/valuation-handbook-2023",
#     "https://rpc.cfainstitute.org/research/foundation/2024/an-introduction-to-alternative-credit",
#     "https://rpc.cfainstitute.org/research/foundation/2024/lifetime-financial-advice-a-personalized-optimal-multilevel-approach",
#     "https://rpc.cfainstitute.org/research/foundation/2023/revisiting-equity-risk-premium-2021",
#     "https://rpc.cfainstitute.org/research/foundation/2023/ai-and-big-data-in-investments-handbook",
#     "https://rpc.cfainstitute.org/research/foundation/2022/igcc-summary-edition-2022",
#     "https://rpc.cfainstitute.org/research/foundation/2022/rfbr-middle-east-capital-markets",

#     # 2nd Page
#     "https://rpc.cfainstitute.org/research/foundation/2022/esg-investment-outcomes-performance-evaluation-and-attribution",
#     "https://rpc.cfainstitute.org/research/foundation/2022/rfbr-middle-east-capital-markets",
#     "https://rpc.cfainstitute.org/research/foundation/2022/rfbr-managing-material-risk",
#     "https://rpc.cfainstitute.org/research/foundation/2022/rflr-stock-buybacks",
#     "https://rpc.cfainstitute.org/research/foundation/2021/twenty-five-years-rf-vertin-award",
#     "https://rpc.cfainstitute.org/research/foundation/2021/puzzles-of-inflation-money-debt",
#     "https://rpc.cfainstitute.org/research/foundation/2021/igcc-2021-summary-edition",
#     "https://rpc.cfainstitute.org/research/foundation/2021/defined-contribution-plans",
#     "https://rpc.cfainstitute.org/research/foundation/2021/negative-interest-rates",
#     "https://rpc.cfainstitute.org/research/foundation/2021/apac-capital-markets",

#     # 3rd Page
#     "https://rpc.cfainstitute.org/research/foundation/2021/capitalism-for-everyone",
#     "https://rpc.cfainstitute.org/research/foundation/2021/sbbi-2021-summary-edition",
#     "https://rpc.cfainstitute.org/research/foundation/2021/geo-economics",
#     "https://rpc.cfainstitute.org/research/foundation/2021/bursting-the-bubble",
#     "https://rpc.cfainstitute.org/research/foundation/2021/cryptoassets",
#     "https://rpc.cfainstitute.org/research/foundation/2020/learning-about-risk-management",
#     "https://rpc.cfainstitute.org/research/foundation/2020/sbbi-2020-summary-edition",
#     "https://rpc.cfainstitute.org/research/foundation/2020/rflr-artificial-intelligence-in-asset-management",
#     "https://rpc.cfainstitute.org/research/foundation/2020/is-there-a-retirement-crisis",
#     "https://rpc.cfainstitute.org/research/foundation/2020/robert-merton-science-of-finance",

#     # 4th Page
#     "https://rpc.cfainstitute.org/research/foundation/2020/esg-and-responsible-institutional-investing",
#     "https://rpc.cfainstitute.org/research/foundation/2020/vix-index-and-volatility-based-global-indexes",
#     "https://rpc.cfainstitute.org/research/foundation/2020/research-foundation-review-2019",
#     "https://rpc.cfainstitute.org/research/foundation/2020/etfs-and-systemic-risks",
#     "https://rpc.cfainstitute.org/research/foundation/2019/performance-attribution",
#     "https://rpc.cfainstitute.org/research/foundation/2019/behavioral-finance-the-second-generation",
#     "https://rpc.cfainstitute.org/research/foundation/2019/african-capital-markets",
#     "https://rpc.cfainstitute.org/research/foundation/2019/the-productivity-puzzle",
#     "https://rpc.cfainstitute.org/research/foundation/2019/secure-retirement",
#     "https://rpc.cfainstitute.org/research/foundation/2019/cash-flow-focus-endowments-trusts",

#     # 5th Page
#     "https://rpc.cfainstitute.org/research/foundation/2019/university-endowments-primer",
#     "https://rpc.cfainstitute.org/research/foundation/2019/tontines",
#     "https://rpc.cfainstitute.org/research/foundation/2019/ten-years-after",
#     "https://rpc.cfainstitute.org/research/foundation/2019/investment-governance-for-fiduciaries",
#     "https://rpc.cfainstitute.org/research/foundation/2019/beyer-brief",
#     "https://rpc.cfainstitute.org/research/foundation/2018/popularity-bridge-between-classical-and-behavioral-finance",
#     "https://rpc.cfainstitute.org/research/foundation/2018/future-of-investment-management",
#     "https://rpc.cfainstitute.org/research/foundation/2018/some-like-it-hedged",
#     "https://rpc.cfainstitute.org/research/foundation/2018/mainstreaming-sustainable-investing",
#     "https://rpc.cfainstitute.org/research/foundation/2019/research-foundation-review-2018",

#     # 6th Page
#     "https://rpc.cfainstitute.org/research/foundation/2018/foundations-of-high-yield-analysis",
#     "https://rpc.cfainstitute.org/research/foundation/2018/current-state-of-quantitative-equity-investing",
#     "https://rpc.cfainstitute.org/research/foundation/2018/risk-profiling-and-tolerance",
#     "https://rpc.cfainstitute.org/research/foundation/2018/risk-tolerance-and-circumstances",
#     "https://rpc.cfainstitute.org/research/foundation/2018/research-foundation-review-2017",
#     "https://rpc.cfainstitute.org/research/foundation/2018/alternative-investments-a-primer-for-investment-professionals",
#     "https://rpc.cfainstitute.org/research/foundation/2017/handbook-on-sustainable-investments",
#     "https://rpc.cfainstitute.org/research/foundation/2017/equity-valuation-science-art-or-craft",
#     "https://rpc.cfainstitute.org/research/foundation/2017/equity-risk-premium",
#     "https://rpc.cfainstitute.org/research/foundation/2017/a-primer-for-investment-trustees",

#     # 7th Page
#     "https://rpc.cfainstitute.org/research/foundation/2017/new-vistas-in-risk-profiling",
#     "https://rpc.cfainstitute.org/research/foundation/2017/asian-structured-products",
#     "https://rpc.cfainstitute.org/research/foundation/2017/fintech-and-regtech-in-a-nutshell-and-the-future-in-a-sandbox",
#     "https://rpc.cfainstitute.org/research/foundation/2017/financial-risk-tolerance",
#     "https://rpc.cfainstitute.org/research/foundation/2017/the-importance-of-manager-selection-chinese-mandarin",
#     "https://rpc.cfainstitute.org/research/foundation/2017/research-foundation-review-2016",
#     "https://rpc.cfainstitute.org/research/foundation/2017/impact-of-reporting-frequency-on-uk-public-companies",
#     "https://rpc.cfainstitute.org/research/foundation/2016/factor-investing-and-asset-allocation-a-business-cycle-perspective",
#     "https://rpc.cfainstitute.org/research/foundation/2016/financial-market-history",
#     "https://rpc.cfainstitute.org/research/foundation/2017/technical-analysis",

#     # 8th Page
#     "https://rpc.cfainstitute.org/research/foundation/2016/gender-diversity-in-investment-management",
#     "https://rpc.cfainstitute.org/research/foundation/2016/portfolio-structuring-and-the-value-of-forecasting",
#     "https://rpc.cfainstitute.org/research/foundation/2016/lets-all-learn-how-to-fish----to-sustain-long-term-economic-growth",
#     "https://rpc.cfainstitute.org/research/foundation/2016/overcoming-the-notion-of-a-single-reference-currency-a-currency-basket-approach",
#     "https://rpc.cfainstitute.org/research/foundation/2016/risk-profiling-through-a-behavioral-finance-lens",
#     "https://rpc.cfainstitute.org/research/foundation/2016/annuities-and-retirement-income-planning",
#     "https://rpc.cfainstitute.org/research/foundation/2016/research-foundation-review-2015",
#     "https://rpc.cfainstitute.org/research/foundation/2015/longevity-risk-and-retirement-income-planning",
#     "https://rpc.cfainstitute.org/research/foundation/2015/the-industrial-organization-of-the-global-asset-management-business",
#     "https://rpc.cfainstitute.org/research/foundation/2015/trading-and-electronic-markets-what-investment-professionals-need-to-know",

#     # 9th Page
#     "https://rpc.cfainstitute.org/research/foundation/2015/a-comprehensive-guide-to-exchange-traded-funds-etfs",
#     "https://rpc.cfainstitute.org/research/foundation/2015/research-foundation-year-in-review-2014",
#     "https://rpc.cfainstitute.org/research/foundation/2015/investor-risk-profiling-an-overview",
#     "https://rpc.cfainstitute.org/research/foundation/2014/the-new-economics-of-liquidity-and-financial-frictions",
#     "https://rpc.cfainstitute.org/research/foundation/2014/islamic-finance-ethics-concepts-practice",
#     "https://rpc.cfainstitute.org/research/foundation/2014/investment-professionals-and-fiduciary-duties",
#     "https://rpc.cfainstitute.org/research/foundation/2014/investment-management-a-science-to-teach-or-an-art-to-learn",
#     "https://rpc.cfainstitute.org/research/foundation/2014/the-principalagent-problem-in-finance",
#     "https://rpc.cfainstitute.org/research/foundation/2014/research-foundation-year-in-review-2013",
#     "https://rpc.cfainstitute.org/research/foundation/2014/environmental-markets-a-new-asset-class",

#     # 10th Page
#     "https://rpc.cfainstitute.org/research/foundation/2013/manager-selection",
#     "https://rpc.cfainstitute.org/research/foundation/2013/fundamentals-of-futures-and-options-corrected-april-2014",
#     "https://rpc.cfainstitute.org/research/foundation/2013/errata",
#     "https://rpc.cfainstitute.org/research/foundation/2013/ethics-and-financial-markets-the-role-of-the-analyst",
#     "https://rpc.cfainstitute.org/research/foundation/2013/research-foundation-year-in-review-2012",
#     "https://rpc.cfainstitute.org/research/foundation/2013/life-annuities-an-optimal-product-for-retirement-income",
#     "https://rpc.cfainstitute.org/research/foundation/2013/the-evolution-of-assetliability-management",
#     "https://rpc.cfainstitute.org/research/foundation/2012/a-new-look-at-currency-investing",
#     "https://rpc.cfainstitute.org/research/foundation/2012/life-cycle-investing-financial-education-and-consumer-protection-corrected-january-2013",
#     "https://rpc.cfainstitute.org/research/foundation/2018/latin-american-local-capital-markets"
# ]

# listing_urls = [
# "https://rpc.cfainstitute.org/en/research-foundation/publications#sort=%40officialz32xdate%20descending",
# "https://rpc.cfainstitute.org/en/research-foundation/publications#first=10&sort=%40officialz32xdate%20descending",
# "https://rpc.cfainstitute.org/en/research-foundation/publications#first=20&sort=%40officialz32xdate%20descending",
# "https://rpc.cfainstitute.org/en/research-foundation/publications#first=30&sort=%40officialz32xdate%20descending",
# "https://rpc.cfainstitute.org/en/research-foundation/publications#first=40&sort=%40officialz32xdate%20descending",
# "https://rpc.cfainstitute.org/en/research-foundation/publications#first=50&sort=%40officialz32xdate%20descending",
# "https://rpc.cfainstitute.org/en/research-foundation/publications#first=60&sort=%40officialz32xdate%20descending",
# "https://rpc.cfainstitute.org/en/research-foundation/publications#first=70&sort=%40officialz32xdate%20descending",
# "https://rpc.cfainstitute.org/en/research-foundation/publications#first=80&sort=%40officialz32xdate%20descending",
# "https://rpc.cfainstitute.org/en/research-foundation/publications#first=90&sort=%40officialz32xdate%20descending",
    
# ]

# if __name__ == "__main__":
#     # Process individual content URLs directly
#     process_content_urls([(url, None) for url in content_urls])
    
#     # Gather additional content URLs from listing pages and process
#     listing_content_urls = gather_content_urls_from_listing(listing_urls)
#     process_content_urls(listing_content_urls)
    
#     print("Completed processing all URLs.")


import os
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import boto3
import snowflake.connector
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import SSLError
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# AWS S3 setup
s3 = boto3.client('s3',
                  aws_access_key_id='AKIAQIJRSDTXXVW6DVT5',
                  aws_secret_access_key='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',
                  region_name='us-east-1')

# Snowflake connection details
SNOWFLAKE_USER = 'Pranaav1392'
SNOWFLAKE_PASSWORD = 'Pran@av1392'
SNOWFLAKE_ACCOUNT = 'rghxtqa-yub04874'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
SNOWFLAKE_DATABASE = 'TEST_CFA_PUBLISH'
SNOWFLAKE_SCHEMA = 'PUBLIC'
SNOWFLAKE_TABLE = 'CFA_PUBLICATIONS_TABLE_TEST'

# S3 bucket name
BUCKET_NAME = 'testingbucketbig'

# Local folder to store PDFs temporarily before uploading
LOCAL_FOLDER = r'C:\bigdata3\contents_test'

# Retry configuration for requests
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)

# Sanitize folder names for Windows compatibility
def sanitize_folder_name(name):
    name = re.sub(r'[\n\r\t]', ' ', name)
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# Function to upload to S3
def upload_to_s3(file_path, s3_folder_name):
    try:
        s3_key = f"{s3_folder_name}/{os.path.basename(file_path)}"
        s3.upload_file(file_path, BUCKET_NAME, s3_key)
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        print(f"Uploaded {file_path} to S3: {s3_url}")
        return s3_url
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None

# Function to download PDF and upload to S3
def download_and_upload_pdf(pdf_url, title):
    folder_name = sanitize_folder_name(title)
    local_folder = os.path.join(LOCAL_FOLDER, folder_name)
    os.makedirs(local_folder, exist_ok=True)
    pdf_path = os.path.join(local_folder, f"{folder_name}.pdf")

    attempts = 3
    for attempt in range(1, attempts + 1):
        try:
            response = session.get(pdf_url, timeout=10)
            response.raise_for_status()
            if response.status_code == 200:
                with open(pdf_path, "wb") as file:
                    file.write(response.content)
                s3_url = upload_to_s3(pdf_path, folder_name)
                return s3_url
        except SSLError as ssl_error:
            print(f"SSL error encountered on attempt {attempt} for {pdf_url}: {ssl_error}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading PDF from {pdf_url} on attempt {attempt}: {e}")
    
    print(f"Failed to download PDF from {pdf_url} after {attempts} attempts.")
    return None

# Function to extract PDF link from a webpage
def extract_pdf_link_from_page(page_url):
    try:
        response = session.get(page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for PDF links (modify the selector as needed based on the page structure)
        pdf_link_tag = soup.find('a', href=lambda href: href and href.endswith('.pdf'))
        if pdf_link_tag:
            pdf_url = urljoin(page_url, pdf_link_tag['href'])
            print(f"Found PDF link: {pdf_url}")
            return pdf_url
        else:
            print(f"No PDF link found on page: {page_url}")
            return None
    except Exception as e:
        print(f"Error fetching PDF link from {page_url}: {e}")
        return None

# Function to extract title from the URL
def extract_title(url):
    print(f"Extracting title from {url}")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    # Parse the page content
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Find the title using the unique class or tag
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else None
    return title

# Function to insert or update the PDF link in Snowflake for a specific title
def update_pdf_link_in_snowflake(title, pdf_url):
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA
        )
        cursor = conn.cursor()
        
        # Update the PDF link in the table if the title exists
        update_query = f"""
            UPDATE {SNOWFLAKE_TABLE}
            SET PDF_LINK = %s
            WHERE TITLE = %s;
        """
        cursor.execute(update_query, (pdf_url, title))
        print(f"Updated PDF link for {title} in Snowflake.")
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error updating Snowflake for {title}: {e}")

# Main function to handle the process
def process_book(page_url):
    # Step 1: Extract title from the webpage
    title = extract_title(page_url)
    if not title:
        print(f"Failed to find a title on {page_url}")
        return

    # Step 2: Extract PDF link from the webpage
    pdf_url = extract_pdf_link_from_page(page_url)
    if not pdf_url:
        print(f"Failed to find a PDF link on {page_url}")
        return

    # Step 3: Download and upload the PDF to S3
    s3_pdf_url = download_and_upload_pdf(pdf_url, title)
    if not s3_pdf_url:
        print(f"Failed to process PDF for {title}.")
        return

    # Step 4: Update Snowflake with the S3 URL of the PDF
    update_pdf_link_in_snowflake(title, s3_pdf_url)

# Example usage
page_url = "https://rpc.cfainstitute.org/research/foundation/2017/equity-valuation-science-art-or-craft"
process_book(page_url)








