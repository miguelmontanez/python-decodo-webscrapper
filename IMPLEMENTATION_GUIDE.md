# Implementation Guide - Egaroshi Price Tracker

## Overview

This document outlines the changes made to resolve pricing accuracy issues on the Egaroshi platform.

## Problem Statement

The original implementation used a generic web scraper (`get_article_text`) that extracted all text from a page without specific price data extraction. This resulted in:
- Inaccurate price capture across different vendors
- No vendor-specific handling for diverse HTML structures
- Lack of price validation
- No anomaly detection for outlier prices
- Limited error handling and recovery

## Solution Architecture

### 1. Vendor-Specific Scrapers (`vendors.py`)

**Problem Solved**: Different vendors use different HTML structures, making generic selectors unreliable.

**Implementation**:
- Created `VendorScraper` base class with common functionality
- Implemented `AmazonScraper` with Amazon-specific CSS selectors
- Implemented `WalmartScraper` with Walmart-specific CSS selectors
- Created `GenericScraper` for unknown vendors with heuristic matching
- `get_scraper()` function automatically selects the correct scraper based on URL

**Key Features**:
```python
class AmazonScraper(VendorScraper):
    - Handles multiple Amazon page layouts
    - Extracts from: h1 span, #productTitle, a-price-whole
    - Parses availability status
    - Returns structured ProductPrice data

class WalmartScraper(VendorScraper):
    - Targets Walmart selectors: [data-testid="product-price"]
    - Handles dynamic pricing
    - Extracts availability information
```

### 2. Price Validation (`utils.py`)

**Problem Solved**: No validation of extracted prices, allowing invalid or suspicious data.

**Implementation**:
- `PriceValidator` class with comprehensive validation rules:
  - Price must exist and be non-null
  - Price must be positive
  - Price must be within reasonable range ($0.01 - $100,000)
  - URL must be valid and properly formatted
  - Product name must be present

**Validation Example**:
```python
is_valid, message = PriceValidator.validate_price(
    price=29.99,
    url="https://amazon.com/product",
    product_name="Product Name",
    vendor="Amazon"
)
```

### 3. Price Comparison & Anomaly Detection

**Problem Solved**: No way to compare prices across vendors or detect suspicious pricing.

**Implementation**:
- `PriceComparator` class for multi-vendor comparison
- Calculates statistics: min, max, average, variance
- Detects outliers using IQR (Interquartile Range) method
- Identifies cheapest vendor and savings potential

**Comparison Example**:
```python
result = PriceComparator.compare_prices([
    {"vendor": "Amazon", "price": 29.99},
    {"vendor": "Walmart", "price": 25.99},
    {"vendor": "Target", "price": 27.99}
])
# Returns: min=25.99, max=29.99, avg=27.99, savings=4.00
```

### 4. Centralized Error Handling

**Problem Solved**: Generic error messages without recovery guidance.

**Implementation**:
- `ErrorHandler` class with specific error type handling
- Recovery suggestions for different error scenarios:
  - ConnectionError: Check internet and website availability
  - Timeout: Website unresponsive, try again later
  - HTTPError: Verify URL validity
  - AttributeError: HTML structure changed, update selectors

### 5. Enhanced MCP Tools

**Updated `main.py`** with three tools:

#### Tool 1: `extract_product_price(vendor_url)`
Extracts single product price with validation.

**Flow**:
```
vendor_url 
  ↓
Validate URL format
  ↓
Scrape with Decodo API
  ↓
Get vendor-specific scraper
  ↓
Extract price using vendor selectors
  ↓
Validate extracted data
  ↓
Return structured result
```

#### Tool 2: `compare_product_prices(vendor_urls)`
Compares prices across multiple vendors.

**Flow**:
```
List of vendor URLs
  ↓
Extract price from each URL (using Tool 1)
  ↓
Collect valid prices
  ↓
Compare prices (min, max, avg, variance)
  ↓
Detect outliers
  ↓
Return comparison results with summary
```

#### Tool 3: `get_article_text(website_url)`
Original text extraction (preserved for compatibility).

## Testing Strategy

### Test Suite (`test_pricing.py`)

Comprehensive test coverage for:

1. **Scraper Tests**
   - Amazon scraper: Title and price extraction
   - Walmart scraper: Price parsing
   - Generic scraper: Fallback matching

2. **Price Parsing Tests**
   - `$19.99` → 19.99
   - `$1,299.99` → 1299.99
   - `€25.50` → 25.50
   - Invalid formats → None

3. **Validation Tests**
   - Valid prices pass validation
   - Missing/negative prices fail
   - Out-of-range prices detected
   - Invalid URLs rejected
   - Missing product names rejected

4. **Comparison Tests**
   - Accurate min/max/average calculation
   - Correct cheapest vendor identification
   - Outlier detection with IQR method
   - Empty data handling

5. **Error Handling Tests**
   - Connection errors caught with recovery suggestions
   - Timeout errors handled gracefully
   - Appropriate error messages returned

### Running Tests

```bash
# Install dev dependencies
uv pip install pytest pytest-cov

# Run all tests with verbose output
pytest test_pricing.py -v

# Run with coverage report
pytest test_pricing.py --cov=. --cov-report=html

# Run specific test class
pytest test_pricing.py::TestAmazonScraper -v
```

## Files Changed

### New Files
- `vendors.py` - Vendor-specific scraper implementations (380+ lines)
- `utils.py` - Validation, comparison, and error handling (250+ lines)
- `test_pricing.py` - Comprehensive test suite (400+ lines)

### Modified Files
- `main.py` - Enhanced with 2 new pricing tools (100+ new lines)
- `pyproject.toml` - Updated dependencies and metadata
- `README.md` - Complete documentation (250+ lines)

### Total Addition: ~1,300+ lines of production code and tests

## Key Improvements

| Issue | Original | Improved |
|-------|----------|----------|
| Vendor Support | 1 (Generic) | 3 (Amazon, Walmart, Generic) |
| Price Extraction | Text-only | Vendor-specific selectors |
| Validation | None | Comprehensive validation |
| Price Comparison | Not available | Full comparison with stats |
| Anomaly Detection | Not available | IQR-based outlier detection |
| Error Handling | Basic | Detailed with recovery suggestions |
| Testing | None | 40+ test cases |
| Documentation | Basic | Comprehensive with examples |

## Pricing Accuracy Improvements

### Before
- Generic text extraction could miss prices
- No validation of extracted prices
- No vendor-specific handling
- Difficult to compare across vendors

### After
- Vendor-specific CSS selectors for accurate extraction
- Multi-level validation ensures data quality
- Automatic vendor detection and handling
- Built-in price comparison with anomaly detection
- Clear error messages and recovery suggestions

## Usage Examples

### Example 1: Extract Price from Amazon

```python
result = extract_product_price(
    "https://amazon.com/dp/B08W3XYZAB"
)
# Returns:
# {
#   "success": True,
#   "vendor": "Amazon",
#   "product_name": "Example Product",
#   "price": 29.99,
#   "currency": "USD",
#   "availability": "In Stock",
#   "validation_status": "Validation passed"
# }
```

### Example 2: Compare Prices Across Vendors

```python
result = compare_product_prices([
    "https://amazon.com/dp/B08W3XYZAB",
    "https://walmart.com/ip/123456789",
    "https://target.com/p/123456789"
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
#     "most_expensive_vendor": "Amazon"
#   },
#   "summary": {
#     "successful_extractions": 3,
#     "savings_potential": 5.00
#   }
# }
```

## Migration Guide

### For Existing Egaroshi Users

1. **Update Integration**:
   - Replace calls to `get_article_text()` with `extract_product_price()`
   - For multi-vendor comparison, use `compare_product_prices()`

2. **API Response Changes**:
   - Old: String text content
   - New: Structured JSON with price details and validation status

3. **Error Handling**:
   - Check `success` field in response
   - Use `error` field for troubleshooting
   - Reference `recovery_suggestion` for resolution

## Performance Considerations

- **API Rate Limiting**: Each URL makes one Decodo API call
- **Timeout**: 30-second timeout per request
- **Concurrent Processing**: Can process URLs in parallel
- **Caching**: Consider caching results to reduce API calls

## Future Enhancements

1. **Price History Tracking**
   - Store prices in database
   - Track price changes over time

2. **Automated Monitoring**
   - Scheduled price checks
   - Real-time alerts for significant drops

3. **Extended Vendor Support**
   - eBay, Best Buy, Newegg, AliExpress
   - International vendors and currencies

4. **Advanced Analytics**
   - Price trend analysis
   - Predictive pricing models
   - Competitive intelligence

## Support & Troubleshooting

### Common Issues

1. **"Website can't be crawled"**
   - Verify URL is accessible
   - Check website's robots.txt
   - Confirm Decodo API is working

2. **"Price not extracted"**
   - Website HTML structure may have changed
   - Update CSS selectors in vendor scraper
   - Try generic scraper with manual selector

3. **Invalid prices in comparison**
   - Check validation logs
   - Verify product pages are similar (same product)
   - Review raw_price_text in response

## Conclusion

The enhanced Egaroshi Price Tracker provides:
- ✅ Accurate price extraction across multiple vendors
- ✅ Comprehensive data validation
- ✅ Price comparison and anomaly detection
- ✅ Robust error handling
- ✅ Extensive test coverage
- ✅ Production-ready implementation

The system is now ready for deployment and will significantly improve pricing accuracy for the Egaroshi platform.
