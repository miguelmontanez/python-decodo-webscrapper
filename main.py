from mcp.server.fastmcp import FastMCP
from typing import List
import requests
from bs4 import BeautifulSoup
import json

# Decodo API Token (Get your API token from https://visit.decodo.com/aOL4yR)
decodo_token = "VTAwMDAyNjc0Mzk6T3lkc19haU4yTTVucjIwd2pG"

# Create MCP server
mcp = FastMCP("DecodoWebsiteScrapper")

# Tool: Get Article Text
@mcp.tool()
def get_article_text(website_url: str) -> str:
    """
        Scrapes a website HTML and extract the articles text
        Input:
            website_url: The URL of the website to scrape
        Output:
            The text content of the article
    """
    
    url = "https://scraper-api.decodo.com/v2/scrape"
    
    payload = {
        "url": website_url,
        "headless": "html"
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic "+decodo_token
    }
    
    crawled_article = requests.post(url, json=payload, headers=headers)
    crawled_article_json = json.loads(crawled_article.text)

    status_code = crawled_article_json['results'][0]["status_code"]
    if status_code !=200:
        return "Website Can't be crawled"
    
    html_string = crawled_article_json['results'][0]["content"]
    
    return BeautifulSoup(html_string, "html.parser").get_text()



if __name__ == "__main__":
    mcp.run()


