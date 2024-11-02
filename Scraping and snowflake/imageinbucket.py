import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import boto3

# AWS S3 setup with your provided credentials
s3 = boto3.client('s3',
                  aws_access_key_id='',
                  aws_secret_access_key='',
                  region_name='us-east-1')

# S3 bucket name
BUCKET_NAME = 'bigd3'

# Local folder to temporarily store images before uploading
LOCAL_FOLDER = r'C:\bigdata3\contents'

# Function to upload files to S3
def upload_to_s3(file_path, s3_folder_name):
    try:
        print(f"Uploading {file_path} to S3 bucket {BUCKET_NAME}...")
        s3_key = f"{s3_folder_name}/{os.path.basename(file_path)}"
        s3.upload_file(file_path, BUCKET_NAME, s3_key)
        print(f"Uploaded {file_path} to S3: {s3_key}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")

# Function to download an image and upload it to S3
def download_image(image_url, folder_name):
    try:
        # Remove query parameters from image URL
        parsed_url = urlparse(image_url)
        base_image_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

        response = requests.get(base_image_url)
        if response.status_code == 200:
            # Create a folder for the specific document locally
            local_folder = os.path.join(LOCAL_FOLDER, folder_name)
            os.makedirs(local_folder, exist_ok=True)

            # Save the image locally
            image_path = os.path.join(local_folder, os.path.basename(parsed_url.path))  # Save only the base name of the image
            with open(image_path, "wb") as img_file:
                img_file.write(response.content)
            print(f"Downloaded image: {image_path}")

            # Upload image to the correct S3 folder where the PDF resides
            upload_to_s3(image_path, folder_name)
        else:
            print(f"Failed to download image from {base_image_url}")
    except Exception as e:
        print(f"Error downloading image: {e}")

# Function to scrape the image URL from the webpage
def scrape_image_from_page(url):
    print(f"Scraping page: {url}")
    
    # Setup Selenium WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)
    
    try:
        # Wait for the page to fully load and look for the image tag
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "img")))

        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Scrape the image URL (based on the `<img src>` tag provided)
        image_tag = soup.find("img", class_="article-cover")  # Look for the specific class "article-cover"
        image_url = urljoin(url, image_tag['src']) if image_tag else None

        driver.quit()

        # Return the image URL
        return image_url
    except Exception as e:
        driver.quit()
        print(f"Error scraping image from page: {e}")
        return None

# Main function to scrape and upload images
def scrape_and_upload_image_for_pdf(url, pdf_folder_name):
    print(f"Processing URL: {url}")
    image_url = scrape_image_from_page(url)

    if image_url:
        print(f"Found image: {image_url}")
        # Use the same folder name for both PDF and image uploads
        download_image(image_url, pdf_folder_name)
    else:
        print(f"No image found for {url}")

# List of URLs for which we need to scrape and upload images with folder names
urls = [
    # 1st Page
    {"url": "https://rpc.cfainstitute.org/research/foundation/2024/beyond-active-and-passive-investing", "folder": "Beyond Active and Passive Investing"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2024/investment-model-validation", "folder": "Investment Model Validation"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2024/economics-of-private-equity", "folder": "Economics of Private Equity"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2024/valuation-handbook-2023", "folder": "Valuation Handbook 2023"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2024/an-introduction-to-alternative-credit", "folder": "An Introduction to Alternative Credit"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2024/lifetime-financial-advice-a-personalized-optimal-multilevel-approach", "folder": "Lifetime Financial Advice A Personalized Optimal Multilevel Approach"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2023/revisiting-equity-risk-premium-2021", "folder": "Revisiting Equity Risk Premium 2021"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2023/ai-and-big-data-in-investments-handbook", "folder": "AI and Big Data in Investments Handbook"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2022/igcc-summary-edition-2022", "folder": "IGCC Summary Edition 2022"},
    
    # 2nd Page
    {"url": "https://rpc.cfainstitute.org/research/foundation/2022/esg-investment-outcomes-performance-evaluation-and-attribution", "folder": "ESG Investment Outcomes"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2022/rfbr-middle-east-capital-markets", "folder": "Middle East Capital Markets"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2022/rfbr-managing-material-risk", "folder": "Managing Material Risk"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2022/rflr-stock-buybacks", "folder": "Stock Buybacks"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2021/twenty-five-years-rf-vertin-award", "folder": "Twenty-Five Years RF Vertin Award"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2021/puzzles-of-inflation-money-debt", "folder": "Puzzles of Inflation Money Debt"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2021/igcc-2021-summary-edition", "folder": "IGCC 2021 Summary Edition"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2021/defined-contribution-plans", "folder": "Defined Contribution Plans"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2021/negative-interest-rates", "folder": "Negative Interest Rates"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2021/apac-capital-markets", "folder": "APAC Capital Markets"},

    # 3rd Page
    {"url": "https://rpc.cfainstitute.org/research/foundation/2021/capitalism-for-everyone", "folder": "Capitalism for Everyone"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2021/sbbi-2021-summary-edition", "folder": "SBBI 2021 Summary Edition"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2021/geo-economics", "folder": "Geo Economics"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2021/bursting-the-bubble", "folder": "Bursting the Bubble"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2021/cryptoassets", "folder": "Cryptoassets"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2020/learning-about-risk-management", "folder": "Learning about Risk Management"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2020/sbbi-2020-summary-edition", "folder": "SBBI 2020 Summary Edition"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2020/rflr-artificial-intelligence-in-asset-management", "folder": "Artificial Intelligence in Asset Management"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2020/is-there-a-retirement-crisis", "folder": "Is There a Retirement Crisis"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2020/robert-merton-science-of-finance", "folder": "Robert Merton Science of Finance"},

    # 4th Page
    {"url": "https://rpc.cfainstitute.org/research/foundation/2020/esg-and-responsible-institutional-investing", "folder": "ESG and Responsible Institutional Investing"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2020/vix-index-and-volatility-based-global-indexes", "folder": "VIX Index and Volatility Based Global Indexes"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2020/research-foundation-review-2019", "folder": "Research Foundation Review 2019"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2020/etfs-and-systemic-risks", "folder": "ETFs and Systemic Risks"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/performance-attribution", "folder": "Performance Attribution"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/behavioral-finance-the-second-generation", "folder": "Behavioral Finance The Second Generation"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/african-capital-markets", "folder": "African Capital Markets"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/the-productivity-puzzle", "folder": "The Productivity Puzzle"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/secure-retirement", "folder": "Secure Retirement"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/cash-flow-focus-endowments-trusts", "folder": "Cash Flow Focus Endowments Trusts"},
    
    # 5th Page
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/university-endowments-primer", "folder": "University Endowments Primer"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/tontines", "folder": "Tontines"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/ten-years-after", "folder": "Ten Years After"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/investment-governance-for-fiduciaries", "folder": "Investment Governance for Fiduciaries"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/beyer-brief", "folder": "Beyer Brief"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2018/popularity-bridge-between-classical-and-behavioral-finance", "folder": "Popularity Bridge Between Classical and Behavioral Finance"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2018/future-of-investment-management", "folder": "Future of Investment Management"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2018/some-like-it-hedged", "folder": "Some Like It Hedged"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2018/mainstreaming-sustainable-investing", "folder": "Mainstreaming Sustainable Investing"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2019/research-foundation-review-2018", "folder": "Research Foundation Review 2018"},

    # 6th Page
    {"url": "https://rpc.cfainstitute.org/research/foundation/2018/foundations-of-high-yield-analysis", "folder": "Foundations of High Yield Analysis"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2018/current-state-of-quantitative-equity-investing", "folder": "Current State of Quantitative Equity Investing"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2018/risk-profiling-and-tolerance", "folder": "Risk Profiling and Tolerance"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2018/risk-tolerance-and-circumstances", "folder": "Risk Tolerance and Circumstances"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2018/research-foundation-review-2017", "folder": "Research Foundation Review 2017"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2018/alternative-investments-a-primer-for-investment-professionals", "folder": "Alternative Investments A Primer for Investment Professionals"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/handbook-on-sustainable-investments", "folder": "Handbook on Sustainable Investments"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/equity-valuation-science-art-or-craft", "folder": "Equity Valuation Science Art or Craft"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/equity-risk-premium", "folder": "Equity Risk Premium"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/a-primer-for-investment-trustees", "folder": "A Primer for Investment Trustees"},

    # 7th Page
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/new-vistas-in-risk-profiling", "folder": "New Vistas in Risk Profiling"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/asian-structured-products", "folder": "Asian Structured Products"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/fintech-and-regtech-in-a-nutshell-and-the-future-in-a-sandbox", "folder": "Fintech and Regtech in a Nutshell and the Future in a Sandbox"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/financial-risk-tolerance", "folder": "Financial Risk Tolerance"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/the-importance-of-manager-selection-chinese-mandarin", "folder": "The Importance of Manager Selection Chinese Mandarin"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/research-foundation-review-2016", "folder": "Research Foundation Review 2016"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/impact-of-reporting-frequency-on-uk-public-companies", "folder": "Impact of Reporting Frequency on UK Public Companies"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2016/factor-investing-and-asset-allocation-a-business-cycle-perspective", "folder": "Factor Investing and Asset Allocation A Business Cycle Perspective"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2016/financial-market-history", "folder": "Financial Market History"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2017/technical-analysis", "folder": "Technical Analysis"},

    # 8th Page
    {"url": "https://rpc.cfainstitute.org/research/foundation/2016/gender-diversity-in-investment-management", "folder": "Gender Diversity in Investment Management"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2016/portfolio-structuring-and-the-value-of-forecasting", "folder": "Portfolio Structuring and the Value of Forecasting"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2016/lets-all-learn-how-to-fish----to-sustain-long-term-economic-growth", "folder": "Let's All Learn How to Fish to Sustain Long Term Economic Growth"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2016/overcoming-the-notion-of-a-single-reference-currency-a-currency-basket-approach", "folder": "Overcoming the Notion of a Single Reference Currency A Currency Basket Approach"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2016/risk-profiling-through-a-behavioral-finance-lens", "folder": "Risk Profiling Through a Behavioral Finance Lens"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2016/annuities-and-retirement-income-planning", "folder": "Annuities and Retirement Income Planning"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2016/research-foundation-review-2015", "folder": "Research Foundation Review 2015"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2015/longevity-risk-and-retirement-income-planning", "folder": "Longevity Risk and Retirement Income Planning"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2015/the-industrial-organization-of-the-global-asset-management-business", "folder": "The Industrial Organization of the Global Asset Management Business"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2015/trading-and-electronic-markets-what-investment-professionals-need-to-know", "folder": "Trading and Electronic Markets What Investment Professionals Need to Know"},

    # 9th Page
    {"url": "https://rpc.cfainstitute.org/research/foundation/2015/a-comprehensive-guide-to-exchange-traded-funds-etfs", "folder": "A Comprehensive Guide to Exchange Traded Funds ETFs"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2015/research-foundation-year-in-review-2014", "folder": "Research Foundation Year in Review 2014"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2015/investor-risk-profiling-an-overview", "folder": "Investor Risk Profiling An Overview"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2014/the-new-economics-of-liquidity-and-financial-frictions", "folder": "The New Economics of Liquidity and Financial Frictions"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2014/islamic-finance-ethics-concepts-practice", "folder": "Islamic Finance Ethics Concepts Practice"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2014/investment-professionals-and-fiduciary-duties", "folder": "Investment Professionals and Fiduciary Duties"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2014/investment-management-a-science-to-teach-or-an-art-to-learn", "folder": "Investment Management A Science to Teach or an Art to Learn"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2014/the-principalagent-problem-in-finance", "folder": "The Principal Agent Problem in Finance"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2014/research-foundation-year-in-review-2013", "folder": "Research Foundation Year in Review 2013"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2014/environmental-markets-a-new-asset-class", "folder": "Environmental Markets A New Asset Class"},

    # 10th Page
    {"url": "https://rpc.cfainstitute.org/research/foundation/2013/manager-selection", "folder": "Manager Selection"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2013/fundamentals-of-futures-and-options-corrected-april-2014", "folder": "Fundamentals of Futures and Options Corrected April 2014"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2013/errata", "folder": "Errata"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2013/ethics-and-financial-markets-the-role-of-the-analyst", "folder": "Ethics and Financial Markets The Role of the Analyst"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2013/research-foundation-year-in-review-2012", "folder": "Research Foundation Year in Review 2012"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2013/life-annuities-an-optimal-product-for-retirement-income", "folder": "Life Annuities An Optimal Product for Retirement Income"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2013/the-evolution-of-assetliability-management", "folder": "The Evolution of Asset Liability Management"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2012/a-new-look-at-currency-investing", "folder": "A New Look at Currency Investing"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2012/life-cycle-investing-financial-education-and-consumer-protection-corrected-january-2013", "folder": "Life Cycle Investing Financial Education and Consumer Protection Corrected January 2013"},
    {"url": "https://rpc.cfainstitute.org/research/foundation/2018/latin-american-local-capital-markets", "folder": "Latin American Local Capital Markets"},
   
]

if __name__ == "__main__":
    for item in urls:
        folder_name = item["folder"].lower()  # Folder name where the corresponding PDF is stored
        url = item["url"]  # URL of the page to scrape
        scrape_and_upload_image_for_pdf(url, folder_name)

    print("Image scraping and uploading process completed.")
