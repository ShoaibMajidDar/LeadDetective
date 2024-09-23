import json
import os
import string
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from selenium import webdriver
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from selenium.webdriver.chrome.options import Options


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("openai_api_key")

# Function to check if a URL belongs to the same domain
def is_same_domain(url, base_domain):
    try:
        return urlparse(url).netloc == base_domain
    except Exception as e:
        return False
    
# Function to clean and extract all visible text from a page
def extract_text(soup):
    for script in soup(["script", "style"]):
        script.decompose()  # Remove script and style tags
    text = soup.get_text(separator="\n")  # Get all text and separate by newlines
    lines = [line.strip() for line in text.splitlines() if line.strip()]  # Clean lines
    return "\n".join(lines)

# Recursive function to scrape pages up to n levels
def scrape_website(url, base_domain, level, max_level, visited_urls, website_scrapped):
    if level > max_level or url in visited_urls:
        return
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Applicable for headless chrome on some environments
    chrome_options.add_argument("--remote-debugging-port=9222")  # Prevents DevToolsActivePort error
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        page_source = driver.page_source
        driver.close()

        # Mark this URL as visited
        visited_urls.add(url)

        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract the title
        page_title = soup.title.string if soup.title else "No Title"

        # Extract all text content from the page
        page_text = extract_text(soup)
        website_scrapped.append(f"{url} \n\n {page_title} \n\n {page_text} \n\n\n\n<<<>>>\n\n\n\n")

        if max_level == 1: return
        
        # Find all links on the page
        links = soup.find_all('a', href=True)

        # Recursively scrape each valid link
        for link in links:
            href = link.get('href')
            next_url = urljoin(url, href)  # Join with base URL in case of relative paths
            # Check if the URL is part of the same domain and not already visited
            if next_url not in visited_urls and is_same_domain(next_url, base_domain):
                # Scrape the next URL at the next level
                time.sleep(1)  # Optional: to avoid sending too many requests quickly
                scrape_website(next_url, base_domain, level + 1, max_level, visited_urls, website_scrapped)

    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")

# Main function to start scraping
def start_scraping(start_url, max_level, website_scrapped):
    base_domain = urlparse(start_url).netloc
    visited_urls = set()
    scrape_website(start_url, base_domain, 1, max_level, visited_urls, website_scrapped)


def get_company_contracts(domain_name: str, company_name: str, number: str, all_websites_contracts, all_websites_texts):
    website_scrapped = []
    domain_name = domain_name.strip("https://www.")
    if company_name not in all_websites_contracts:
        start_url = "https://www."+domain_name
        print(start_url)
        max_level = 3
        start_scraping(start_url, max_level, website_scrapped)
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        website_text = "".join(website_scrapped)
        all_websites_texts[company_name] = website_text
        
        index = faiss.IndexFlatL2(len(list(embeddings.embed_documents("hello world"))[0]))
        vector_store = FAISS(
                                embedding_function=embeddings,
                                index=index,
                                docstore=InMemoryDocstore(),
                                index_to_docstore_id={},
                            )
        document_list = []
        for i in range(len(website_scrapped)):
            document_list.append(Document(
                                            page_content=website_scrapped[i],
                                            metadata={"website":domain_name}
                                        )
                                )
        
        vector_store.add_documents(documents=document_list, ids=list(range(len(website_scrapped))))

        results = vector_store.similarity_search(f"all the contracts and projects of {company_name}", k=5, filter={"website": domain_name})

        ress = ""
        for res in results:
            ress+= res.page_content
        

        llm = ChatOpenAI(model = "gpt-4o-mini", temperature=0)

        template="""
    Given the text below, identify and name all the contracts of the company: {company_name}.
    return only the contract names

    Text for analysis:
    {search_result}
    """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm | StrOutputParser()
        res = chain.invoke({"company_name": company_name, "search_result":ress})
        all_websites_contracts[company_name] = res
    
    number_verification_flag = verify_number(number,all_websites_texts[company_name])

    return all_websites_contracts[company_name], number_verification_flag, all_websites_contracts, all_websites_texts
    




def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)

def verify_number(number: str, website_text: str):
    web_tt=remove_punctuation(website_text)
    web_tt = (web_tt.replace(" ","")).lower()

    number = remove_punctuation(number)

    return (web_tt.find(number) != -1)