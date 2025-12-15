from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import json

from vendors import get_scraper, ProductPrice
from utils import PriceValidator, PriceComparator, ErrorHandler

# Decodo API Token (Get your API token from https://visit.decodo.com/aOL4yR)
decodo_token = "VTAwMDAyNjc0Mzk6T3lkc19haU4yTTVucjIwd2pG"

# Create MCP server
mcp = FastMCP("EgaroshiPriceTracker")


def scrape_with_decodo(website_url: str) -> Optional[str]:
    """
    Scrapes a website using Decodo API and returns HTML content.
    """
    try:
        url = "https://scraper-api.decodo.com/v2/scrape"
        
        payload = {
            "url": website_url,
            "headless": "html"
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Basic " + decodo_token
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response_json = json.loads(response.text)
        
        status_code = response_json.get('results', [{}])[0].get("status_code", 0)
        if status_code != 200:
            return None
        
        html_string = response_json.get('results', [{}])[0].get("content", "")
        return html_string if html_string else None
        
    except Exception as e:
        print(f"Error scraping with Decodo: {str(e)}")
        return None


# Tool 1: Extract Product Price
@mcp.tool()
def extract_product_price(vendor_url: str) -> Dict[str, Any]:
    """
    Extracts product price from a vendor URL (Amazon, Walmart, etc.).
    Uses vendor-specific selectors for accurate price extraction.
    
    Input:
        vendor_url: The URL of the product page (Amazon, Walmart, etc.)
    
    Output:
        Dictionary containing:
        - vendor: Vendor name
        - product_name: Extracted product name
        - price: Extracted price (float)
        - currency: Currency code (USD)
        - availability: Product availability status
        - url: The provided URL
        - success: Whether extraction was successful
    """
    try:
        # Validate URL
        if not vendor_url or not vendor_url.startswith(('http://', 'https://')):
            return {
                "success": False,
                "error": "Invalid URL format",
                "url": vendor_url
            }
        
        # Scrape website with Decodo
        html_content = scrape_with_decodo(vendor_url)
        if not html_content:
            return {
                "success": False,
                "error": "Failed to scrape website with Decodo API",
                "url": vendor_url
            }
        
        # Get appropriate scraper for vendor
        scraper = get_scraper(vendor_url)
        
        # Extract price using vendor-specific logic
        product_price = scraper.extract_price(html_content, vendor_url)
        
        # Validate extracted data
        is_valid, validation_message = PriceValidator.validate_price(
            price=product_price.price,
            url=product_price.url,
            product_name=product_price.product_name,
            vendor=product_price.vendor
        )
        
        return {
            "success": is_valid,
            "vendor": product_price.vendor,
            "product_name": product_price.product_name,
            "price": product_price.price,
            "currency": product_price.currency,
            "availability": product_price.availability,
            "url": product_price.url,
            "validation_status": validation_message,
            "raw_price_text": product_price.raw_price_text
        }
        
    except Exception as e:
        error_result = ErrorHandler.handle_scraping_error(e, vendor_url, "Unknown")
        return error_result


# Tool 2: Compare Prices Across Vendors
@mcp.tool()
def compare_product_prices(vendor_urls: List[str]) -> Dict[str, Any]:
    """
    Compares product prices across multiple vendor URLs.
    Identifies the cheapest option and detects price anomalies.
    
    Input:
        vendor_urls: List of product URLs from different vendors
    
    Output:
        Dictionary containing:
        - min_price: Lowest price found
        - max_price: Highest price found
        - average_price: Average across all vendors
        - price_variance: Difference between min and max
        - price_variance_percent: Variance as percentage of average
        - cheapest_vendor: Vendor with lowest price
        - most_expensive_vendor: Vendor with highest price
        - price_details: Detailed pricing for each vendor
        - outliers: Prices detected as outliers
    """
    try:
        prices_data = []
        failed_extractions = []
        
        # Extract prices from all vendors
        for url in vendor_urls:
            result = extract_product_price(url)
            
            if result.get("success"):
                prices_data.append({
                    "vendor": result.get("vendor"),
                    "price": result.get("price"),
                    "product_name": result.get("product_name"),
                    "availability": result.get("availability"),
                    "url": url
                })
            else:
                failed_extractions.append({
                    "url": url,
                    "error": result.get("error")
                })
        
        if not prices_data:
            return {
                "success": False,
                "error": "No valid prices could be extracted from any vendor",
                "failed_extractions": failed_extractions
            }
        
        # Compare prices
        comparison_result = PriceComparator.compare_prices(prices_data)
        
        return {
            "success": True,
            "comparison": comparison_result,
            "price_details": prices_data,
            "failed_extractions": failed_extractions if failed_extractions else None,
            "summary": {
                "total_urls_processed": len(vendor_urls),
                "successful_extractions": len(prices_data),
                "failed_extractions": len(failed_extractions),
                "savings_potential": round(comparison_result.get("max_price", 0) - comparison_result.get("min_price", 0), 2)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Comparison failed: {str(e)}"
        }


# Tool 3: Get Article Text (Original functionality)
@mcp.tool()
def get_article_text(website_url: str) -> str:
    """
    Scrapes a website HTML and extracts the articles text.
    Useful for content extraction from news sites and blogs.
    
    Input:
        website_url: The URL of the website to scrape
    
    Output:
        The text content of the article
    """
    
    html_string = scrape_with_decodo(website_url)
    if not html_string:
        return "Website can't be crawled"
    
    return BeautifulSoup(html_string, "html.parser").get_text()


if __name__ == "__main__":
    mcp.run()


