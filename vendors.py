"""
Vendor-specific scraper implementations for price extraction.
Each vendor has different HTML structures, so we need custom extractors.
"""

import re
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class ProductPrice:
    """Structured data for extracted product price information."""
    vendor: str
    product_name: Optional[str]
    price: Optional[float]
    currency: str = "USD"
    availability: Optional[str] = None
    url: str = ""
    raw_price_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "vendor": self.vendor,
            "product_name": self.product_name,
            "price": self.price,
            "currency": self.currency,
            "availability": self.availability,
            "url": self.url,
        }


class VendorScraper:
    """Base class for vendor-specific scrapers."""
    
    def __init__(self, vendor_name: str):
        self.vendor_name = vendor_name
    
    def extract_price(self, html_content: str, url: str) -> ProductPrice:
        """
        Extract price information from HTML content.
        Must be implemented by subclasses.
        """
        raise NotImplementedError
    
    def parse_price_string(self, price_text: str) -> Optional[float]:
        """
        Parse a price string and extract the numerical value.
        Handles various formats: $19.99, €25,50, £15.00, etc.
        """
        if not price_text:
            return None
        
        # Remove whitespace
        price_text = price_text.strip()
        
        # Extract numerical value (handles both . and , as decimal separators)
        match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', '.'))
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None


class AmazonScraper(VendorScraper):
    """Scraper for Amazon product pages."""
    
    def __init__(self):
        super().__init__("Amazon")
    
    def extract_price(self, html_content: str, url: str) -> ProductPrice:
        """Extract price from Amazon product page."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extract product name
        product_name = self._extract_product_name(soup)
        
        # Extract price
        price_text, price_value = self._extract_price(soup)
        
        # Extract availability
        availability = self._extract_availability(soup)
        
        return ProductPrice(
            vendor=self.vendor_name,
            product_name=product_name,
            price=price_value,
            availability=availability,
            url=url,
            raw_price_text=price_text,
        )
    
    def _extract_product_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title from Amazon page."""
        # Try multiple selectors for product title
        selectors = [
            'h1 span',
            '#productTitle',
            'span.product-title',
            'h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and len(text) > 5:
                    return text
        return None
    
    def _extract_price(self, soup: BeautifulSoup) -> tuple[Optional[str], Optional[float]]:
        """Extract price from Amazon page."""
        # Try multiple price selectors
        price_selectors = [
            'span.a-price-whole',
            'span.a-price',
            'span[data-a-color="price"]',
            '.a-price-range .a-price-range-min .a-price-whole',
            'span.reinventPrice',
            '.aok-inline-block span.a-price'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                if price_text:
                    price_value = self.parse_price_string(price_text)
                    if price_value:
                        return price_text, price_value
        
        return None, None
    
    def _extract_availability(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract availability status from Amazon page."""
        availability_selectors = [
            'span.availability',
            'div[data-feature-name="availability"]',
            'span.a-size-base'
        ]
        
        for selector in availability_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if 'in stock' in text.lower() or 'out of stock' in text.lower():
                    return text
        return None


class WalmartScraper(VendorScraper):
    """Scraper for Walmart product pages."""
    
    def __init__(self):
        super().__init__("Walmart")
    
    def extract_price(self, html_content: str, url: str) -> ProductPrice:
        """Extract price from Walmart product page."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extract product name
        product_name = self._extract_product_name(soup)
        
        # Extract price
        price_text, price_value = self._extract_price(soup)
        
        # Extract availability
        availability = self._extract_availability(soup)
        
        return ProductPrice(
            vendor=self.vendor_name,
            product_name=product_name,
            price=price_value,
            availability=availability,
            url=url,
            raw_price_text=price_text,
        )
    
    def _extract_product_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title from Walmart page."""
        selectors = [
            'h1',
            'span.font-bold',
            '[data-testid="product-title"]',
            'h1.heading-headline'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and len(text) > 5:
                    return text
        return None
    
    def _extract_price(self, soup: BeautifulSoup) -> tuple[Optional[str], Optional[float]]:
        """Extract price from Walmart page."""
        price_selectors = [
            '[data-testid="product-price"]',
            'div[data-testid="PriceSummary"]',
            'span.product-price',
            '.price-now',
            '[itemprop="price"]'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                if price_text:
                    price_value = self.parse_price_string(price_text)
                    if price_value:
                        return price_text, price_value
        
        return None, None
    
    def _extract_availability(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract availability status from Walmart page."""
        availability_selectors = [
            '[data-testid="availability"]',
            'span.availability-status',
            '.avail-status'
        ]
        
        for selector in availability_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        return None


class GenericScraper(VendorScraper):
    """Generic scraper for unknown vendors."""
    
    def __init__(self, vendor_name: str = "Unknown"):
        super().__init__(vendor_name)
    
    def extract_price(self, html_content: str, url: str) -> ProductPrice:
        """Extract price from generic HTML using heuristics."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extract product name from title or h1
        product_name = self._extract_product_name(soup)
        
        # Extract price using common patterns
        price_text, price_value = self._extract_price(soup, html_content)
        
        return ProductPrice(
            vendor=self.vendor_name,
            product_name=product_name,
            price=price_value,
            url=url,
            raw_price_text=price_text,
        )
    
    def _extract_product_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product name from page title or h1."""
        # Try title tag first
        title = soup.find('title')
        if title:
            text = title.get_text(strip=True)
            if text:
                return text
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            text = h1.get_text(strip=True)
            if text:
                return text
        
        return None
    
    def _extract_price(self, soup: BeautifulSoup, html_content: str) -> tuple[Optional[str], Optional[float]]:
        """Extract price using generic selectors and patterns."""
        # Try common price selectors
        price_patterns = [
            r'\$\s*[\d,]+\.?\d*',  # $19.99
            r'€\s*[\d,]+\.?\d*',   # €25.50
            r'£\s*[\d,]+\.?\d*',   # £15.00
            r'price["\']?\s*:\s*[\d,]+\.?\d*',  # price: 19.99
        ]
        
        # Search in HTML text
        for pattern in price_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                price_text = matches[0]
                price_value = self.parse_price_string(price_text)
                if price_value:
                    return price_text, price_value
        
        # Try common price selectors
        price_selectors = [
            'span.price',
            'div.price',
            '[data-price]',
            'span[data-value]',
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text(strip=True)
                if price_text:
                    price_value = self.parse_price_string(price_text)
                    if price_value:
                        return price_text, price_value
        
        return None, None


def get_scraper(url: str) -> VendorScraper:
    """
    Get appropriate scraper based on URL.
    """
    url_lower = url.lower()
    
    if 'amazon' in url_lower:
        return AmazonScraper()
    elif 'walmart' in url_lower:
        return WalmartScraper()
    else:
        # Extract vendor name from URL
        vendor_name = url.split('/')[2].replace('www.', '').split('.')[0].title()
        return GenericScraper(vendor_name)
