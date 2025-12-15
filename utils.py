"""
Utility functions for price validation and error handling.
"""

import re
from typing import Optional, Dict, Any
from enum import Enum


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class PriceValidation(Enum):
    """Validation result status."""
    VALID = "valid"
    INVALID_PRICE = "invalid_price"
    INVALID_URL = "invalid_url"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    EXTRACTION_FAILED = "extraction_failed"


class PriceValidator:
    """Validates extracted price data for accuracy and consistency."""
    
    # Reasonable price ranges for different categories (USD)
    PRICE_RANGES = {
        "default": (0.01, 100000.00),
        "electronics": (10.00, 50000.00),
        "appliances": (50.00, 10000.00),
        "books": (0.99, 300.00),
        "clothing": (5.00, 500.00),
    }
    
    @staticmethod
    def validate_price(
        price: Optional[float],
        url: str,
        product_name: Optional[str],
        vendor: str
    ) -> tuple[bool, str]:
        """
        Validate extracted price data.
        Returns (is_valid, message)
        """
        # Check if price exists
        if price is None:
            return False, "Price not extracted"
        
        # Check if price is positive
        if price <= 0:
            return False, f"Invalid price value: {price} (must be positive)"
        
        # Check if price is within reasonable range
        min_price, max_price = PriceValidator.PRICE_RANGES["default"]
        if price < min_price or price > max_price:
            return False, f"Price {price} outside reasonable range ({min_price}-{max_price})"
        
        # Check if URL is valid
        if not PriceValidator.validate_url(url):
            return False, "Invalid or missing URL"
        
        # Check if product name exists
        if not product_name or len(product_name.strip()) == 0:
            return False, "Product name not extracted"
        
        return True, "Validation passed"
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        url_pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return bool(re.match(url_pattern, url))
    
    @staticmethod
    def validate_vendor(vendor: str) -> bool:
        """Validate vendor name."""
        return isinstance(vendor, str) and len(vendor.strip()) > 0


class PriceComparator:
    """Compare prices across vendors and detect anomalies."""
    
    @staticmethod
    def compare_prices(prices_data: list[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare prices across multiple vendors.
        Detects outliers and price variations.
        """
        if not prices_data:
            return {"error": "No price data to compare"}
        
        # Extract valid prices
        valid_prices = [
            p for p in prices_data
            if p.get("price") and isinstance(p["price"], (int, float))
        ]
        
        if not valid_prices:
            return {"error": "No valid prices found"}
        
        prices = [p["price"] for p in valid_prices]
        
        # Calculate statistics
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        price_variance = max_price - min_price
        price_variance_percent = (price_variance / avg_price * 100) if avg_price > 0 else 0
        
        # Find cheapest and most expensive
        cheapest = next(p for p in valid_prices if p["price"] == min_price)
        most_expensive = next(p for p in valid_prices if p["price"] == max_price)
        
        # Detect potential outliers (prices > 1.5x IQR from median)
        outliers = PriceComparator._detect_outliers(prices)
        
        return {
            "min_price": min_price,
            "max_price": max_price,
            "average_price": round(avg_price, 2),
            "price_variance": round(price_variance, 2),
            "price_variance_percent": round(price_variance_percent, 2),
            "cheapest_vendor": cheapest["vendor"],
            "most_expensive_vendor": most_expensive["vendor"],
            "price_count": len(valid_prices),
            "outliers": outliers,
        }
    
    @staticmethod
    def _detect_outliers(prices: list[float]) -> list[float]:
        """Detect outlier prices using IQR method."""
        if len(prices) < 4:
            return []
        
        sorted_prices = sorted(prices)
        q1_index = len(sorted_prices) // 4
        q3_index = (3 * len(sorted_prices)) // 4
        
        q1 = sorted_prices[q1_index]
        q3 = sorted_prices[q3_index]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [p for p in prices if p < lower_bound or p > upper_bound]
        return outliers


class ErrorHandler:
    """Centralized error handling for scraping operations."""
    
    @staticmethod
    def handle_scraping_error(error: Exception, url: str, vendor: str) -> Dict[str, Any]:
        """
        Handle scraping errors gracefully.
        """
        error_message = str(error)
        error_type = type(error).__name__
        
        return {
            "success": False,
            "error": error_message,
            "error_type": error_type,
            "vendor": vendor,
            "url": url,
            "recovery_suggestion": ErrorHandler._get_recovery_suggestion(error_type)
        }
    
    @staticmethod
    def _get_recovery_suggestion(error_type: str) -> str:
        """Provide recovery suggestions based on error type."""
        suggestions = {
            "ConnectionError": "Check internet connection and website availability",
            "Timeout": "Website is taking too long to respond. Try again later.",
            "HTTPError": "Check if the URL is valid and accessible",
            "ValueError": "Invalid data format. Verify the scraped content",
            "AttributeError": "HTML structure may have changed. Update selectors.",
        }
        return suggestions.get(error_type, "Check logs and try again")
