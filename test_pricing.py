"""
Test suite for pricing accuracy and scraper validation.
Run with: python -m pytest test_pricing.py -v
"""

import pytest
from vendors import AmazonScraper, WalmartScraper, GenericScraper, get_scraper, ProductPrice
from utils import PriceValidator, PriceComparator, ErrorHandler, ValidationError


class TestAmazonScraper:
    """Tests for Amazon scraper."""
    
    def test_parse_price_string(self):
        """Test price string parsing."""
        scraper = AmazonScraper()
        
        # Test various price formats
        assert scraper.parse_price_string("$19.99") == 19.99
        assert scraper.parse_price_string("$1,299.99") == 1299.99
        assert scraper.parse_price_string("19.99") == 19.99
        assert scraper.parse_price_string("$0.99") == 0.99
        assert scraper.parse_price_string(None) is None
        assert scraper.parse_price_string("") is None
        assert scraper.parse_price_string("No price") is None
    
    def test_extract_price_with_html(self):
        """Test price extraction from HTML."""
        scraper = AmazonScraper()
        
        html = """
        <html>
            <h1 id="productTitle"><span>Amazon Product Name</span></h1>
            <span class="a-price-whole">$49.99</span>
            <span class="availability">In Stock</span>
        </html>
        """
        
        result = scraper.extract_price(html, "https://amazon.com/product")
        
        assert result.vendor == "Amazon"
        assert result.product_name == "Amazon Product Name"
        assert result.price == 49.99
        assert result.url == "https://amazon.com/product"


class TestWalmartScraper:
    """Tests for Walmart scraper."""
    
    def test_parse_price_string(self):
        """Test price string parsing."""
        scraper = WalmartScraper()
        
        assert scraper.parse_price_string("$34.99") == 34.99
        assert scraper.parse_price_string("$2,500.00") == 2500.00
        assert scraper.parse_price_string("34.99") == 34.99


class TestPriceValidator:
    """Tests for price validation."""
    
    def test_validate_valid_price(self):
        """Test validation of valid prices."""
        is_valid, message = PriceValidator.validate_price(
            price=29.99,
            url="https://amazon.com/product",
            product_name="Test Product",
            vendor="Amazon"
        )
        assert is_valid is True
        assert message == "Validation passed"
    
    def test_validate_missing_price(self):
        """Test validation of missing price."""
        is_valid, message = PriceValidator.validate_price(
            price=None,
            url="https://amazon.com/product",
            product_name="Test Product",
            vendor="Amazon"
        )
        assert is_valid is False
        assert "Price not extracted" in message
    
    def test_validate_negative_price(self):
        """Test validation of negative price."""
        is_valid, message = PriceValidator.validate_price(
            price=-10.00,
            url="https://amazon.com/product",
            product_name="Test Product",
            vendor="Amazon"
        )
        assert is_valid is False
        assert "must be positive" in message
    
    def test_validate_price_out_of_range(self):
        """Test validation of unreasonable prices."""
        is_valid, message = PriceValidator.validate_price(
            price=999999.00,
            url="https://amazon.com/product",
            product_name="Test Product",
            vendor="Amazon"
        )
        assert is_valid is False
        assert "outside reasonable range" in message
    
    def test_validate_missing_product_name(self):
        """Test validation of missing product name."""
        is_valid, message = PriceValidator.validate_price(
            price=29.99,
            url="https://amazon.com/product",
            product_name=None,
            vendor="Amazon"
        )
        assert is_valid is False
        assert "Product name not extracted" in message
    
    def test_validate_invalid_url(self):
        """Test validation of invalid URL."""
        is_valid, message = PriceValidator.validate_price(
            price=29.99,
            url="not-a-valid-url",
            product_name="Test Product",
            vendor="Amazon"
        )
        assert is_valid is False
        assert "Invalid" in message
    
    def test_validate_url_valid(self):
        """Test URL validation with valid URLs."""
        assert PriceValidator.validate_url("https://amazon.com/product") is True
        assert PriceValidator.validate_url("http://walmart.com/item") is True
        assert PriceValidator.validate_url("https://www.example.com") is True
    
    def test_validate_url_invalid(self):
        """Test URL validation with invalid URLs."""
        assert PriceValidator.validate_url("not-a-url") is False
        assert PriceValidator.validate_url("") is False
        assert PriceValidator.validate_url("www.example.com") is False


class TestPriceComparator:
    """Tests for price comparison functionality."""
    
    def test_compare_prices(self):
        """Test price comparison across vendors."""
        prices_data = [
            {"vendor": "Amazon", "price": 29.99},
            {"vendor": "Walmart", "price": 25.99},
            {"vendor": "Target", "price": 27.99},
        ]
        
        result = PriceComparator.compare_prices(prices_data)
        
        assert result["min_price"] == 25.99
        assert result["max_price"] == 29.99
        assert result["average_price"] == pytest.approx(27.99, 0.01)
        assert result["cheapest_vendor"] == "Walmart"
        assert result["most_expensive_vendor"] == "Amazon"
        assert result["price_count"] == 3
    
    def test_compare_prices_empty(self):
        """Test comparison with empty data."""
        result = PriceComparator.compare_prices([])
        assert "error" in result
    
    def test_compare_prices_with_invalid_prices(self):
        """Test comparison with invalid prices."""
        prices_data = [
            {"vendor": "Amazon", "price": 29.99},
            {"vendor": "Walmart", "price": None},
            {"vendor": "Target", "price": "invalid"},
        ]
        
        result = PriceComparator.compare_prices(prices_data)
        
        # Should only count valid price
        assert result["price_count"] == 1
        assert result["min_price"] == 29.99
    
    def test_detect_outliers(self):
        """Test outlier detection."""
        prices = [10.0, 12.0, 14.0, 16.0, 18.0, 100.0]  # 100 is outlier
        outliers = PriceComparator._detect_outliers(prices)
        assert 100.0 in outliers


class TestProductPrice:
    """Tests for ProductPrice data class."""
    
    def test_product_price_creation(self):
        """Test ProductPrice creation."""
        price = ProductPrice(
            vendor="Amazon",
            product_name="Test Product",
            price=29.99,
            currency="USD",
            availability="In Stock",
            url="https://amazon.com/product"
        )
        
        assert price.vendor == "Amazon"
        assert price.product_name == "Test Product"
        assert price.price == 29.99
        assert price.currency == "USD"
    
    def test_product_price_to_dict(self):
        """Test ProductPrice serialization."""
        price = ProductPrice(
            vendor="Amazon",
            product_name="Test Product",
            price=29.99,
            currency="USD",
            url="https://amazon.com/product"
        )
        
        price_dict = price.to_dict()
        assert price_dict["vendor"] == "Amazon"
        assert price_dict["product_name"] == "Test Product"
        assert price_dict["price"] == 29.99


class TestErrorHandler:
    """Tests for error handling."""
    
    def test_handle_connection_error(self):
        """Test handling of connection errors."""
        error = ConnectionError("Failed to connect")
        result = ErrorHandler.handle_scraping_error(
            error,
            "https://amazon.com/product",
            "Amazon"
        )
        
        assert result["success"] is False
        assert result["error_type"] == "ConnectionError"
        assert "check internet connection" in result["recovery_suggestion"].lower()
    
    def test_handle_timeout_error(self):
        """Test handling of timeout errors."""
        error = TimeoutError("Request timed out")
        result = ErrorHandler.handle_scraping_error(
            error,
            "https://walmart.com/product",
            "Walmart"
        )
        
        assert result["success"] is False
        assert "try again later" in result["recovery_suggestion"].lower()


class TestGetScraper:
    """Tests for scraper selection."""
    
    def test_get_amazon_scraper(self):
        """Test Amazon scraper selection."""
        scraper = get_scraper("https://amazon.com/product")
        assert isinstance(scraper, AmazonScraper)
    
    def test_get_walmart_scraper(self):
        """Test Walmart scraper selection."""
        scraper = get_scraper("https://www.walmart.com/item")
        assert isinstance(scraper, WalmartScraper)
    
    def test_get_generic_scraper(self):
        """Test generic scraper selection for unknown vendors."""
        scraper = get_scraper("https://www.bestbuy.com/product")
        assert isinstance(scraper, GenericScraper)
        assert scraper.vendor_name == "Bestbuy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
