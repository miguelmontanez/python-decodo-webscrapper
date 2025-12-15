# Egaroshi Price Tracker

A Model Context Protocol (MCP) server for accurate product price tracking and comparison across multiple vendors (Amazon, Walmart, and others). Built for the Egaroshi platform to ensure reliable price data extraction and vendor comparison.

## Features

- **Multi-Vendor Price Extraction**: Vendor-specific scrapers for Amazon, Walmart, and generic retailers
- **Accurate Price Parsing**: Extracts prices with validation to ensure data accuracy
- **Price Comparison**: Compare prices across multiple vendors and identify the cheapest option
- **Anomaly Detection**: Detects price outliers using statistical analysis
- **Error Handling**: Graceful error handling with recovery suggestions
- **Data Validation**: Comprehensive validation of extracted prices and product information
- **MCP Integration**: Built as an MCP server for seamless integration with AI assistants like Claude
- **Decodo API Integration**: Uses Decodo web scraping API for reliable content extraction

## Project Structure

```
egaroshi-price-tracker/
├── main.py                 # MCP server with pricing tools
├── vendors.py             # Vendor-specific scraper implementations
├── utils.py               # Validation, comparison, and error handling utilities
├── test_pricing.py        # Comprehensive test suite
├── pyproject.toml         # Project dependencies and metadata
└── README.md              # This file
```

## Prerequisites

- Python 3.13 or higher
- A Decodo API token (get a free trial at https://visit.decodo.com/aOL4yR)
- Claude Desktop application (for MCP integration)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/miguelmontanez/python-decodo-webscrapper
cd python-decodo-webscrapper
```

### 2. Create a Decodo Account

- Visit https://visit.decodo.com/aOL4yR to claim your free trial
- Copy your API token from the dashboard

### 3. Update API Token

Open `main.py` and replace the `decodo_token` variable with your actual API token:

```python
decodo_token = "YOUR_DECODO_API_TOKEN_HERE"
```

### 4. Install Dependencies

```bash
pip install uv
uv sync
```

### 5. Connect to Claude Desktop (Optional)

```bash
uv run mcp install main.py
```

## Available Tools

### 1. `extract_product_price(vendor_url: str)`

Extracts product price from a single vendor URL.

**Parameters:**
- `vendor_url` (string): The URL of the product page (must be valid HTTP/HTTPS URL)

**Returns:**
- `success` (boolean): Whether extraction was successful
- `vendor` (string): Vendor name (Amazon, Walmart, etc.)
- `product_name` (string): Extracted product name
- `price` (float): Extracted price value
- `currency` (string): Currency code (USD)
- `availability` (string): Product availability status (if found)
- `url` (string): The provided URL
- `validation_status` (string): Result of price validation
- `raw_price_text` (string): Original price text before parsing

**Example:**

```python
result = extract_product_price("https://amazon.com/dp/B08XYZ123")
# Returns:
# {
#   "success": True,
#   "vendor": "Amazon",
#   "product_name": "Example Product Name",
#   "price": 29.99,
#   "currency": "USD",
#   "availability": "In Stock",
#   "url": "https://amazon.com/dp/B08XYZ123",
#   "validation_status": "Validation passed"
# }
```

### 2. `compare_product_prices(vendor_urls: List[str])`

Compares product prices across multiple vendor URLs.

**Parameters:**
- `vendor_urls` (list): List of product URLs from different vendors

**Returns:**
- `success` (boolean): Whether comparison was successful
- `comparison` (object): Price comparison statistics:
  - `min_price` (float): Lowest price found
  - `max_price` (float): Highest price found
  - `average_price` (float): Average price across vendors
  - `price_variance` (float): Difference between max and min
  - `price_variance_percent` (float): Variance as percentage
  - `cheapest_vendor` (string): Vendor with lowest price
  - `most_expensive_vendor` (string): Vendor with highest price
  - `outliers` (list): Prices detected as anomalies
- `price_details` (list): Detailed pricing for each vendor
- `summary` (object): Summary statistics
- `failed_extractions` (list): URLs where extraction failed

**Example:**

```python
result = compare_product_prices([
    "https://amazon.com/dp/B08XYZ123",
    "https://walmart.com/ip/123456",
    "https://target.com/p/123456"
])
# Returns:
# {
#   "success": True,
#   "comparison": {
#     "min_price": 24.99,
#     "max_price": 29.99,
#     "average_price": 27.49,
#     "price_variance": 5.00,
#     "price_variance_percent": 18.21,
#     "cheapest_vendor": "Walmart",
#     "most_expensive_vendor": "Amazon",
#     "price_count": 3
#   },
#   "summary": {
#     "total_urls_processed": 3,
#     "successful_extractions": 3,
#     "failed_extractions": 0,
#     "savings_potential": 5.00
#   }
# }
```

### 3. `get_article_text(website_url: str)`

Scrapes a website and extracts plain text content. Useful for content extraction from news sites and blogs.

**Parameters:**
- `website_url` (string): The URL of the website to scrape

**Returns:**
- (string): The plain text content extracted from the webpage

## Supported Vendors

### Amazon
- Smart price extraction from various Amazon page layouts
- Handles different price display formats
- Extracts availability information

### Walmart
- Targets Walmart-specific price selectors
- Extracts product names and availability
- Handles dynamic pricing

### Generic Vendors
- Works with any e-commerce website
- Uses heuristic pattern matching
- Falls back to common CSS selectors

## Data Validation

All extracted prices are validated to ensure accuracy:

- **Price Exists**: Price must be successfully extracted
- **Price Range**: Price must be between $0.01 and $100,000
- **Positive Value**: Price must be a positive number
- **URL Validation**: URL must be valid and accessible
- **Product Name**: Product information must be present

## Price Comparison & Anomaly Detection

The comparison tool uses statistical analysis to:

- Calculate average price across vendors
- Identify price variance and percentage differences
- Detect outlier prices using the IQR (Interquartile Range) method
- Recommend the cheapest option

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest test_pricing.py -v

# Run specific test class
pytest test_pricing.py::TestAmazonScraper -v

# Run with coverage report
pytest test_pricing.py --cov=. --cov-report=html
```

### Test Coverage

- **Scraper Tests**: Price extraction from HTML
- **Validation Tests**: Price and URL validation logic
- **Comparison Tests**: Price comparison and outlier detection
- **Error Handling Tests**: Error recovery suggestions
- **Scraper Selection Tests**: Correct vendor scraper selection

## Troubleshooting

### Issue: "Website can't be crawled"

**Cause**: The website either blocks automated scraping or is temporarily unavailable.

**Solutions**:
- Check if the website's `robots.txt` allows scraping
- Verify the URL is correct and the website is accessible
- Try again after a few minutes
- Check the website's terms of service for scraping restrictions

### Issue: "Price not extracted"

**Cause**: The website structure may have changed or the product page is invalid.

**Solutions**:
- Update the vendor scraper selectors in `vendors.py`
- Verify the URL points to a valid product page
- Check if the website requires JavaScript (Decodo uses headless mode)

### Issue: "Invalid API token"

**Cause**: Decodo token is incorrect or expired.

**Solutions**:
- Verify the token in `main.py`
- Get a new token from https://visit.decodo.com/aOL4yR
- Ensure the token is correctly copied without extra spaces

### Issue: Module import errors

**Cause**: Dependencies not installed correctly.

**Solutions**:
```bash
uv sync
# or
pip install -r requirements.txt
```

## Architecture

### Vendor-Specific Scrapers (`vendors.py`)

Each vendor has a custom scraper class with vendor-specific CSS selectors and price extraction logic:
- `AmazonScraper`: Handles Amazon product pages
- `WalmartScraper`: Handles Walmart product pages
- `GenericScraper`: Fallback for unknown vendors

### Utilities (`utils.py`)

- `PriceValidator`: Validates extracted price data
- `PriceComparator`: Compares prices and detects anomalies
- `ErrorHandler`: Centralized error handling with recovery suggestions

### Main Server (`main.py`)

- MCP server setup with FastMCP
- Decodo API integration
- Tool definitions and implementations
- Error handling and response formatting

## Performance Considerations

- **API Rate Limiting**: Respect Decodo API rate limits
- **Timeout Settings**: Requests timeout set to 30 seconds
- **Concurrent Requests**: Use with caution to avoid IP blocking
- **Cache Strategy**: Consider caching results to reduce API calls

## Future Enhancements

- [ ] Database caching for price history tracking
- [ ] Scheduled price monitoring for specific products
- [ ] Email alerts for significant price drops
- [ ] Support for more vendors (eBay, Best Buy, etc.)
- [ ] Image extraction for product verification
- [ ] Bulk URL processing
- [ ] Price trend analysis and predictions

## Dependencies

- `beautifulsoup4` - HTML parsing and content extraction
- `requests` - HTTP requests handling
- `mcp` - Model Context Protocol server framework
- `pandas` - Data manipulation (optional)
- `pytest` - Testing framework

## License

This project is provided as-is for educational and commercial use.

## References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Decodo Scraper API](https://decodo.com/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/)
- [MCP FastMCP](https://github.com/jlowin/fastmcp)

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Review test cases for usage examples
3. Open an issue on GitHub

---

**Built for Egaroshi - Your Trusted Price Comparison Platform**

Then run this command

```bash
uv run mcp install -e. main.py
```

## 🚀 Usage

Once installed and connected to Claude Desktop, you can use the scraper by asking Claude to scrape websites. The tool will extract content from specified HTML elements using the Decodo API.

## ⚙️ Requirements

- Python 3.8+
- uv package manager
- Decodo API key
- Claude Desktop

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
