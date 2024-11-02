# import os
# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# import snowflake.connector

# # Snowflake connection details
# SNOWFLAKE_USER = "Pranaav1392"
# SNOWFLAKE_PASSWORD = ""
# SNOWFLAKE_ACCOUNT = "rghxtqa-yub04874"
# SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
# SNOWFLAKE_DATABASE = "CFA_PUBLICATIONS"
# SNOWFLAKE_SCHEMA = "PUBLIC"
# SNOWFLAKE_TABLE = "CFA_PUBLICATIONS_TABLE"

# # Initialize Snowflake connection
# def get_snowflake_connection():
#     conn = snowflake.connector.connect(
#         user=SNOWFLAKE_USER,
#         password=SNOWFLAKE_PASSWORD,
#         account=SNOWFLAKE_ACCOUNT,
#         warehouse=SNOWFLAKE_WAREHOUSE,
#         database=SNOWFLAKE_DATABASE,
#         schema=SNOWFLAKE_SCHEMA
#     )
#     return conn

# # Update brief summary in Snowflake
# def update_brief_summary_in_snowflake(title, brief_summary):
#     conn = get_snowflake_connection()
#     try:
#         with conn.cursor() as cursor:
#             # Update query to set the brief summary for the corresponding title
#             update_query = f"""
#                 UPDATE {SNOWFLAKE_TABLE}
#                 SET brief_summary = %s
#                 WHERE title = %s
#             """
#             cursor.execute(update_query, (brief_summary, title))
#         conn.commit()
#         print(f"Updated brief summary for title: {title}")
#     finally:
#         conn.close()

# # Extract title and brief summary from the URL
# def extract_title_summary(url):
#     print(f"Extracting data from {url}")
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#     driver.get(url)
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     driver.quit()
    
#     # Extract the title based on the specified class
#     title = soup.find("h1", class_="spotlight-hero__title spotlight-max-width-item").get_text(strip=True)
    
#     # Initialize an empty brief summary
#     brief_summary = ''
    
#     # Look for summary in various structures
#     # 1. <p class="Paragraph"> inside <div>
#     paragraphs = soup.find_all("p", class_="Paragraph")
#     if paragraphs:
#         brief_summary = " ".join(p.get_text(strip=True) for p in paragraphs)

#     # 2. <div class="article__paragraph"> (contains multiple <p> tags)
#     if not brief_summary:
#         article_paragraph_div = soup.find("div", class_="article__paragraph")
#         if article_paragraph_div:
#             brief_summary = " ".join(p.get_text(strip=True) for p in article_paragraph_div.find_all("p"))

#     # 3. <p class="article-description">
#     if not brief_summary:
#         article_description = soup.find("p", class_="article-description")
#         if article_description:
#             brief_summary = article_description.get_text(strip=True)

#     # 4. <section class="overview grid__item--article-element">
#     if not brief_summary:
#         overview_section = soup.find("section", class_="overview grid__item--article-element")
#         if overview_section:
#             brief_summary = overview_section.get_text(strip=True)

#     # 5. <span class="overview__content">
#     if not brief_summary:
#         overview_content_span = soup.find("span", class_="overview__content")
#         if overview_content_span:
#             brief_summary = overview_content_span.get_text(strip=True)

#     # 6. <div class="TextItem"> (container for unclassed <div> or <span>)
#     if not brief_summary:
#         text_item_div = soup.find("div", class_="TextItem")
#         if text_item_div:
#             brief_summary = " ".join(p.get_text(strip=True) for p in text_item_div.find_all("p"))

#     # 7. Additional fallback for unclassed <div> or <span> within <div class="TextItem">
#     if not brief_summary:
#         unclassed_divs_in_textitem = soup.find_all("div", class_="TextItem")
#         for div in unclassed_divs_in_textitem:
#             p_tags = div.find_all("p")
#             if p_tags:
#                 brief_summary = " ".join(p.get_text(strip=True) for p in p_tags)
#                 if brief_summary:
#                     break

#     # 8. Check all <p> tags within unclassed <div> in main content
#     if not brief_summary:
#         content_divs = soup.find_all("div")
#         for content_div in content_divs:
#             p_tags = content_div.find_all("p")
#             if p_tags:
#                 brief_summary = " ".join(p.get_text(strip=True) for p in p_tags)
#                 if brief_summary:
#                     break

#     # 9. Additional span tags within unclassed or minimal class containers
#     if not brief_summary:
#         span_tags = soup.find_all("span")
#         if span_tags:
#             brief_summary = " ".join(span.get_text(strip=True) for span in span_tags)
    
#     return title, brief_summary

# # Main function to process URLs and update the brief summary in Snowflake
# def process_data(urls):
#     for url in urls:
#         try:
#             # Extract title and summary
#             title, summary = extract_title_summary(url)

#             # Only update if both title and summary are found
#             if title and summary:
#                 update_brief_summary_in_snowflake(title, summary)
#             else:
#                 print(f"Skipped URL due to missing title or summary: {url}")

#         except Exception as e:
#             print(f"Error processing {url}: {e}")

# # List of URLs to process (add the URLs here)
# urls = [
#     # 1st page
#     "https://rpc.cfainstitute.org/research/foundation/2024/beyond-active-and-passive-investing",
#     "https://rpc.cfainstitute.org/research/foundation/2024/investment-model-validation",
#     "https://rpc.cfainstitute.org/research/foundation/2024/economics-of-private-equity",
#     "https://rpc.cfainstitute.org/research/foundation/2024/valuation-handbook-2023",
#     "https://rpc.cfainstitute.org/research/foundation/2024/an-introduction-to-alternative-credit",
#     "https://rpc.cfainstitute.org/research/foundation/2024/lifetime-financial-advice-a-personalized-optimal-multilevel-approach",
#     "https://rpc.cfainstitute.org/research/foundation/2023/revisiting-equity-risk-premium-2021",
#     "https://rpc.cfainstitute.org/research/foundation/2023/ai-and-big-data-in-investments-handbook",
#     "https://rpc.cfainstitute.org/research/foundation/2022/igcc-summary-edition-2022",
#     "https://rpc.cfainstitute.org/research/foundation/2022/rfbr-middle-east-capital-markets"
    
#     # 2nd page
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
    
#     # 3rd page
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
    
#     # 4th page
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
    
#     # 5th page
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
    
#     # 6th page
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
    
#     # 7th page
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
    
#     # 8th page
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
    
#     # 9th page
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
    
#     # 10th page
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

# # Run the data processing
# process_data(urls)











# working code final 

# import os
# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# import snowflake.connector

# # Snowflake connection details
# SNOWFLAKE_USER = "Pranaav1392"
# SNOWFLAKE_PASSWORD = "Pran@av1392"
# SNOWFLAKE_ACCOUNT = "rghxtqa-yub04874"
# SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
# SNOWFLAKE_DATABASE = "CFA_PUBLICATIONS"
# SNOWFLAKE_SCHEMA = "PUBLIC"
# SNOWFLAKE_TABLE = "CFA_PUBLICATIONS_TABLE"

# # Initialize Snowflake connection
# def get_snowflake_connection():
#     conn = snowflake.connector.connect(
#         user=SNOWFLAKE_USER,
#         password=SNOWFLAKE_PASSWORD,
#         account=SNOWFLAKE_ACCOUNT,
#         warehouse=SNOWFLAKE_WAREHOUSE,
#         database=SNOWFLAKE_DATABASE,
#         schema=SNOWFLAKE_SCHEMA
#     )
#     return conn

# # Update brief summary in Snowflake
# def update_brief_summary_in_snowflake(title, brief_summary):
#     conn = get_snowflake_connection()
#     try:
#         with conn.cursor() as cursor:
#             # Update query to set the brief summary for the corresponding title
#             update_query = f"""
#                 UPDATE {SNOWFLAKE_TABLE}
#                 SET brief_summary = %s
#                 WHERE title = %s
#             """
#             cursor.execute(update_query, (brief_summary, title))
#         conn.commit()
#         print(f"Updated brief summary for title: {title}")
#     finally:
#         conn.close()

# # Extract title and brief summary from the URL
# def extract_title_summary(url):
#     print(f"Extracting data from {url}")
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#     driver.get(url)
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     driver.quit()
    
#     # Extract the title based on the specified class
#     title = soup.find("h1", class_="spotlight-hero__title spotlight-max-width-item").get_text(strip=True)
    
#     # Initialize an empty brief summary
#     brief_summary = ''
    
#     # Look for summary in various structures based on provided images and previous code
#     # 1. <p class="Paragraph"> inside <div>
#     paragraphs = soup.find_all("p", class_="Paragraph")
#     if paragraphs:
#         brief_summary = " ".join(p.get_text(strip=True) for p in paragraphs)

#     # 2. <div class="article__paragraph"> (contains multiple <p> tags)
#     if not brief_summary:
#         article_paragraph_div = soup.find("div", class_="article__paragraph")
#         if article_paragraph_div:
#             brief_summary = " ".join(p.get_text(strip=True) for p in article_paragraph_div.find_all("p"))

#     # 3. <p class="article-description">
#     if not brief_summary:
#         article_description = soup.find("p", class_="article-description")
#         if article_description:
#             brief_summary = article_description.get_text(strip=True)

#     # 4. <section class="overview grid__item--article-element">
#     if not brief_summary:
#         overview_section = soup.find("section", class_="overview grid__item--article-element")
#         if overview_section:
#             brief_summary = overview_section.get_text(strip=True)

#     # 5. <span class="overview__content">
#     if not brief_summary:
#         overview_content_span = soup.find("span", class_="overview__content")
#         if overview_content_span:
#             brief_summary = overview_content_span.get_text(strip=True)

#     # 6. <section class="grid__item--article-element"> (observed in images)
#     if not brief_summary:
#         section_article_element = soup.find("section", class_="grid__item--article-element")
#         if section_article_element:
#             brief_summary = " ".join(p.get_text(strip=True) for p in section_article_element.find_all("p"))

#     # 7. <div class="TextItem"> (container for unclassed <div> or <span>)
#     if not brief_summary:
#         text_item_div = soup.find("div", class_="TextItem")
#         if text_item_div:
#             brief_summary = " ".join(p.get_text(strip=True) for p in text_item_div.find_all("p"))

#     # 8. Additional fallback for unclassed <div> or <span> within <div class="TextItem">
#     if not brief_summary:
#         unclassed_divs_in_textitem = soup.find_all("div", class_="TextItem")
#         for div in unclassed_divs_in_textitem:
#             p_tags = div.find_all("p")
#             if p_tags:
#                 brief_summary = " ".join(p.get_text(strip=True) for p in p_tags)
#                 if brief_summary:
#                     break

#     # 9. Check all <p> tags within unclassed <div> in main content
#     if not brief_summary:
#         content_divs = soup.find_all("div")
#         for content_div in content_divs:
#             p_tags = content_div.find_all("p")
#             if p_tags:
#                 brief_summary = " ".join(p.get_text(strip=True) for p in p_tags)
#                 if brief_summary:
#                     break

#     # 10. Additional span tags within unclassed or minimal class containers (observed in images)
#     if not brief_summary:
#         span_tags = soup.find_all("span")
#         if span_tags:
#             brief_summary = " ".join(span.get_text(strip=True) for span in span_tags)
    
#     return title, brief_summary

# # Main function to process URLs and update the brief summary in Snowflake
# def process_data(urls):
#     for url in urls:
#         try:
#             # Extract title and summary
#             title, summary = extract_title_summary(url)

#             # Only update if both title and summary are found
#             if title and summary:
#                 update_brief_summary_in_snowflake(title, summary)
#             else:
#                 print(f"Skipped URL due to missing title or summary: {url}")

#         except Exception as e:
#             print(f"Error processing {url}: {e}")

# # List of URLs to process (add the URLs here)
# urls = [
#     # 1st page
#     "https://rpc.cfainstitute.org/research/foundation/2024/beyond-active-and-passive-investing",
#     "https://rpc.cfainstitute.org/research/foundation/2024/investment-model-validation",
#     "https://rpc.cfainstitute.org/research/foundation/2024/economics-of-private-equity",
#     "https://rpc.cfainstitute.org/research/foundation/2024/valuation-handbook-2023",
#     "https://rpc.cfainstitute.org/research/foundation/2024/an-introduction-to-alternative-credit",
#     "https://rpc.cfainstitute.org/research/foundation/2024/lifetime-financial-advice-a-personalized-optimal-multilevel-approach",
#     "https://rpc.cfainstitute.org/research/foundation/2023/revisiting-equity-risk-premium-2021",
#     "https://rpc.cfainstitute.org/research/foundation/2023/ai-and-big-data-in-investments-handbook",
#     "https://rpc.cfainstitute.org/research/foundation/2022/igcc-summary-edition-2022",
#     "https://rpc.cfainstitute.org/research/foundation/2022/rfbr-middle-east-capital-markets"
    
#     # 2nd page
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
    
#     # 3rd page
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
    
#     # 4th page
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
    
#     # 5th page
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
    
#     # 6th page
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
    
#     # 7th page
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
    
#     # 8th page
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
    
#     # 9th page
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
    
#     # 10th page
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

# # Run the data processing
# process_data(urls)





# test table 

import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import snowflake.connector

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
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    return conn

# Update brief summary in Snowflake
def update_brief_summary_in_snowflake(title, brief_summary):
    conn = get_snowflake_connection()
    try:
        with conn.cursor() as cursor:
            # Update query to set the brief summary for the corresponding title
            update_query = f"""
                UPDATE {SNOWFLAKE_TABLE}
                SET brief_summary = %s
                WHERE title = %s
            """
            cursor.execute(update_query, (brief_summary, title))
        conn.commit()
        print(f"Updated brief summary for title: {title}")
    finally:
        conn.close()

# Extract title and brief summary from the URL
def extract_title_summary(url):
    print(f"Extracting data from {url}")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    # Extract the title based on the specified class
    title = soup.find("h1", class_="spotlight-hero__title spotlight-max-width-item").get_text(strip=True)
    
    # Initialize an empty brief summary
    brief_summary = ''
    
    # Look for summary in various structures based on provided images and previous code
    paragraphs = soup.find_all("p", class_="Paragraph")
    if paragraphs:
        brief_summary = " ".join(p.get_text(strip=True) for p in paragraphs)

    # Try alternative structures for summary extraction
    if not brief_summary:
        article_paragraph_div = soup.find("div", class_="article__paragraph")
        if article_paragraph_div:
            brief_summary = " ".join(p.get_text(strip=True) for p in article_paragraph_div.find_all("p"))

    if not brief_summary:
        article_description = soup.find("p", class_="article-description")
        if article_description:
            brief_summary = article_description.get_text(strip=True)

    if not brief_summary:
        overview_section = soup.find("section", class_="overview grid__item--article-element")
        if overview_section:
            brief_summary = overview_section.get_text(strip=True)

    if not brief_summary:
        overview_content_span = soup.find("span", class_="overview__content")
        if overview_content_span:
            brief_summary = overview_content_span.get_text(strip=True)

    if not brief_summary:
        section_article_element = soup.find("section", class_="grid__item--article-element")
        if section_article_element:
            brief_summary = " ".join(p.get_text(strip=True) for p in section_article_element.find_all("p"))

    if not brief_summary:
        text_item_div = soup.find("div", class_="TextItem")
        if text_item_div:
            brief_summary = " ".join(p.get_text(strip=True) for p in text_item_div.find_all("p"))

    if not brief_summary:
        unclassed_divs_in_textitem = soup.find_all("div", class_="TextItem")
        for div in unclassed_divs_in_textitem:
            p_tags = div.find_all("p")
            if p_tags:
                brief_summary = " ".join(p.get_text(strip=True) for p in p_tags)
                if brief_summary:
                    break

    if not brief_summary:
        content_divs = soup.find_all("div")
        for content_div in content_divs:
            p_tags = content_div.find_all("p")
            if p_tags:
                brief_summary = " ".join(p.get_text(strip=True) for p in p_tags)
                if brief_summary:
                    break

    if not brief_summary:
        span_tags = soup.find_all("span")
        if span_tags:
            brief_summary = " ".join(span.get_text(strip=True) for span in span_tags)
    
    return title, brief_summary

# Main function to process URLs and update the brief summary in Snowflake
def process_data(urls):
    for url in urls:
        try:
            # Extract title and summary
            title, summary = extract_title_summary(url)

            # Only update if both title and summary are found
            if title and summary:
                update_brief_summary_in_snowflake(title, summary)
            else:
                print(f"Skipped URL due to missing title or summary: {url}")

        except Exception as e:
            print(f"Error processing {url}: {e}")

# List of URLs to process (add the URLs here)
urls = [
     # 1st page
    "https://rpc.cfainstitute.org/research/foundation/2024/beyond-active-and-passive-investing",
    "https://rpc.cfainstitute.org/research/foundation/2024/investment-model-validation",
    "https://rpc.cfainstitute.org/research/foundation/2024/economics-of-private-equity",
    "https://rpc.cfainstitute.org/research/foundation/2024/valuation-handbook-2023",
    "https://rpc.cfainstitute.org/research/foundation/2024/an-introduction-to-alternative-credit",
    "https://rpc.cfainstitute.org/research/foundation/2024/lifetime-financial-advice-a-personalized-optimal-multilevel-approach",
    "https://rpc.cfainstitute.org/research/foundation/2023/revisiting-equity-risk-premium-2021",
    "https://rpc.cfainstitute.org/research/foundation/2023/ai-and-big-data-in-investments-handbook",
    "https://rpc.cfainstitute.org/research/foundation/2022/igcc-summary-edition-2022",
    "https://rpc.cfainstitute.org/research/foundation/2022/rfbr-middle-east-capital-markets"
    
    # 2nd page
    "https://rpc.cfainstitute.org/research/foundation/2022/esg-investment-outcomes-performance-evaluation-and-attribution",
    "https://rpc.cfainstitute.org/research/foundation/2022/rfbr-middle-east-capital-markets",
    "https://rpc.cfainstitute.org/research/foundation/2022/rfbr-managing-material-risk",
    "https://rpc.cfainstitute.org/research/foundation/2022/rflr-stock-buybacks",
    "https://rpc.cfainstitute.org/research/foundation/2021/twenty-five-years-rf-vertin-award",
    "https://rpc.cfainstitute.org/research/foundation/2021/puzzles-of-inflation-money-debt",
    "https://rpc.cfainstitute.org/research/foundation/2021/igcc-2021-summary-edition",
    "https://rpc.cfainstitute.org/research/foundation/2021/defined-contribution-plans",
    "https://rpc.cfainstitute.org/research/foundation/2021/negative-interest-rates",
    "https://rpc.cfainstitute.org/research/foundation/2021/apac-capital-markets",
    
    # 3rd page
    "https://rpc.cfainstitute.org/research/foundation/2021/capitalism-for-everyone",
    "https://rpc.cfainstitute.org/research/foundation/2021/sbbi-2021-summary-edition",
    "https://rpc.cfainstitute.org/research/foundation/2021/geo-economics",
    "https://rpc.cfainstitute.org/research/foundation/2021/bursting-the-bubble",
    "https://rpc.cfainstitute.org/research/foundation/2021/cryptoassets",
    "https://rpc.cfainstitute.org/research/foundation/2020/learning-about-risk-management",
    "https://rpc.cfainstitute.org/research/foundation/2020/sbbi-2020-summary-edition",
    "https://rpc.cfainstitute.org/research/foundation/2020/rflr-artificial-intelligence-in-asset-management",
    "https://rpc.cfainstitute.org/research/foundation/2020/is-there-a-retirement-crisis",
    "https://rpc.cfainstitute.org/research/foundation/2020/robert-merton-science-of-finance",
    
    # 4th page
    "https://rpc.cfainstitute.org/research/foundation/2020/esg-and-responsible-institutional-investing",
    "https://rpc.cfainstitute.org/research/foundation/2020/vix-index-and-volatility-based-global-indexes",
    "https://rpc.cfainstitute.org/research/foundation/2020/research-foundation-review-2019",
    "https://rpc.cfainstitute.org/research/foundation/2020/etfs-and-systemic-risks",
    "https://rpc.cfainstitute.org/research/foundation/2019/performance-attribution",
    "https://rpc.cfainstitute.org/research/foundation/2019/behavioral-finance-the-second-generation",
    "https://rpc.cfainstitute.org/research/foundation/2019/african-capital-markets",
    "https://rpc.cfainstitute.org/research/foundation/2019/the-productivity-puzzle",
    "https://rpc.cfainstitute.org/research/foundation/2019/secure-retirement",
    "https://rpc.cfainstitute.org/research/foundation/2019/cash-flow-focus-endowments-trusts",
    
    # 5th page
    "https://rpc.cfainstitute.org/research/foundation/2019/university-endowments-primer",
    "https://rpc.cfainstitute.org/research/foundation/2019/tontines",
    "https://rpc.cfainstitute.org/research/foundation/2019/ten-years-after",
    "https://rpc.cfainstitute.org/research/foundation/2019/investment-governance-for-fiduciaries",
    "https://rpc.cfainstitute.org/research/foundation/2019/beyer-brief",
    "https://rpc.cfainstitute.org/research/foundation/2018/popularity-bridge-between-classical-and-behavioral-finance",
    "https://rpc.cfainstitute.org/research/foundation/2018/future-of-investment-management",
    "https://rpc.cfainstitute.org/research/foundation/2018/some-like-it-hedged",
    "https://rpc.cfainstitute.org/research/foundation/2018/mainstreaming-sustainable-investing",
    "https://rpc.cfainstitute.org/research/foundation/2019/research-foundation-review-2018",
    
    # 6th page
    "https://rpc.cfainstitute.org/research/foundation/2018/foundations-of-high-yield-analysis",
    "https://rpc.cfainstitute.org/research/foundation/2018/current-state-of-quantitative-equity-investing",
    "https://rpc.cfainstitute.org/research/foundation/2018/risk-profiling-and-tolerance",
    "https://rpc.cfainstitute.org/research/foundation/2018/risk-tolerance-and-circumstances",
    "https://rpc.cfainstitute.org/research/foundation/2018/research-foundation-review-2017",
    "https://rpc.cfainstitute.org/research/foundation/2018/alternative-investments-a-primer-for-investment-professionals",
    "https://rpc.cfainstitute.org/research/foundation/2017/handbook-on-sustainable-investments",
    "https://rpc.cfainstitute.org/research/foundation/2017/equity-valuation-science-art-or-craft",
    "https://rpc.cfainstitute.org/research/foundation/2017/equity-risk-premium",
    "https://rpc.cfainstitute.org/research/foundation/2017/a-primer-for-investment-trustees",
    
    # 7th page
    "https://rpc.cfainstitute.org/research/foundation/2017/new-vistas-in-risk-profiling",
    "https://rpc.cfainstitute.org/research/foundation/2017/asian-structured-products",
    "https://rpc.cfainstitute.org/research/foundation/2017/fintech-and-regtech-in-a-nutshell-and-the-future-in-a-sandbox",
    "https://rpc.cfainstitute.org/research/foundation/2017/financial-risk-tolerance",
    "https://rpc.cfainstitute.org/research/foundation/2017/the-importance-of-manager-selection-chinese-mandarin",
    "https://rpc.cfainstitute.org/research/foundation/2017/research-foundation-review-2016",
    "https://rpc.cfainstitute.org/research/foundation/2017/impact-of-reporting-frequency-on-uk-public-companies",
    "https://rpc.cfainstitute.org/research/foundation/2016/factor-investing-and-asset-allocation-a-business-cycle-perspective",
    "https://rpc.cfainstitute.org/research/foundation/2016/financial-market-history",
    "https://rpc.cfainstitute.org/research/foundation/2017/technical-analysis",
    
    # 8th page
    "https://rpc.cfainstitute.org/research/foundation/2016/gender-diversity-in-investment-management",
    "https://rpc.cfainstitute.org/research/foundation/2016/portfolio-structuring-and-the-value-of-forecasting",
    "https://rpc.cfainstitute.org/research/foundation/2016/lets-all-learn-how-to-fish----to-sustain-long-term-economic-growth",
    "https://rpc.cfainstitute.org/research/foundation/2016/overcoming-the-notion-of-a-single-reference-currency-a-currency-basket-approach",
    "https://rpc.cfainstitute.org/research/foundation/2016/risk-profiling-through-a-behavioral-finance-lens",
    "https://rpc.cfainstitute.org/research/foundation/2016/annuities-and-retirement-income-planning",
    "https://rpc.cfainstitute.org/research/foundation/2016/research-foundation-review-2015",
    "https://rpc.cfainstitute.org/research/foundation/2015/longevity-risk-and-retirement-income-planning",
    "https://rpc.cfainstitute.org/research/foundation/2015/the-industrial-organization-of-the-global-asset-management-business",
    "https://rpc.cfainstitute.org/research/foundation/2015/trading-and-electronic-markets-what-investment-professionals-need-to-know",
    
    # 9th page
    "https://rpc.cfainstitute.org/research/foundation/2015/a-comprehensive-guide-to-exchange-traded-funds-etfs",
    "https://rpc.cfainstitute.org/research/foundation/2015/research-foundation-year-in-review-2014",
    "https://rpc.cfainstitute.org/research/foundation/2015/investor-risk-profiling-an-overview",
    "https://rpc.cfainstitute.org/research/foundation/2014/the-new-economics-of-liquidity-and-financial-frictions",
    "https://rpc.cfainstitute.org/research/foundation/2014/islamic-finance-ethics-concepts-practice",
    "https://rpc.cfainstitute.org/research/foundation/2014/investment-professionals-and-fiduciary-duties",
    "https://rpc.cfainstitute.org/research/foundation/2014/investment-management-a-science-to-teach-or-an-art-to-learn",
    "https://rpc.cfainstitute.org/research/foundation/2014/the-principalagent-problem-in-finance",
    "https://rpc.cfainstitute.org/research/foundation/2014/research-foundation-year-in-review-2013",
    "https://rpc.cfainstitute.org/research/foundation/2014/environmental-markets-a-new-asset-class",
    
    # 10th page
    "https://rpc.cfainstitute.org/research/foundation/2013/manager-selection",
    "https://rpc.cfainstitute.org/research/foundation/2013/fundamentals-of-futures-and-options-corrected-april-2014",
    "https://rpc.cfainstitute.org/research/foundation/2013/errata",
    "https://rpc.cfainstitute.org/research/foundation/2013/ethics-and-financial-markets-the-role-of-the-analyst",
    "https://rpc.cfainstitute.org/research/foundation/2013/research-foundation-year-in-review-2012",
    "https://rpc.cfainstitute.org/research/foundation/2013/life-annuities-an-optimal-product-for-retirement-income",
    "https://rpc.cfainstitute.org/research/foundation/2013/the-evolution-of-assetliability-management",
    "https://rpc.cfainstitute.org/research/foundation/2012/a-new-look-at-currency-investing",
    "https://rpc.cfainstitute.org/research/foundation/2012/life-cycle-investing-financial-education-and-consumer-protection-corrected-january-2013",
    "https://rpc.cfainstitute.org/research/foundation/2018/latin-american-local-capital-markets"
]

# Run the data processing
process_data(urls)
