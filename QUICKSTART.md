# Quick Start Guide - Egaroshi Price Tracker

Get started with the Egaroshi Price Tracker in minutes!

## Installation (2 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/miguelmontanez/python-decodo-webscrapper
cd python-decodo-webscrapper

# 2. Install dependencies
pip install uv
uv sync

# 3. Update your Decodo API token in main.py
# Open main.py and replace: decodo_token = "YOUR_TOKEN_HERE"
# Get your token from: https://visit.decodo.com/aOL4yR
```

## Basic Usage

### 1. Extract a Single Product Price

```python
from main import extract_product_price

# Extract price from Amazon
result = extract_product_price(
    "https://amazon.com/dp/B08W3XYZAB"
)

if result["success"]:
    print(f"Product: {result['product_name']}")
    print(f"Price: ${result['price']}")
    print(f"Vendor: {result['vendor']}")
else:
    print(f"Error: {result['error']}")
```

**Output:**
```
Product: Example Wireless Headphones
Price: $29.99
Vendor: Amazon
```

### 2. Compare Prices Across Vendors

```python
from main import compare_product_prices

# Compare the same product across vendors
result = compare_product_prices([
    "https://amazon.com/dp/B08W3XYZAB",
    "https://walmart.com/ip/123456789",
    "https://target.com/p/123456789"
])

if result["success"]:
    comparison = result["comparison"]
    print(f"Cheapest: {comparison['cheapest_vendor']} - ${comparison['min_price']}")
    print(f"Most Expensive: {comparison['most_expensive_vendor']} - ${comparison['max_price']}")
    print(f"Price Difference: ${comparison['price_variance']}")
    print(f"You can save: ${comparison['price_variance']}")
else:
    print(f"Error: {result['error']}")
```

**Output:**
```
Cheapest: Walmart - $24.99
Most Expensive: Amazon - $29.99
Price Difference: $5.00
You can save: $5.00
```

### 3. Run Tests

```bash
# Run all tests
pytest test_pricing.py -v

# Run with coverage
pytest test_pricing.py --cov=. --cov-report=html

# Run specific vendor tests
pytest test_pricing.py::TestAmazonScraper -v
pytest test_pricing.py::TestWalmartScraper -v
```

## Common Scenarios

### Scenario 1: Monitor a Product on Multiple Sites

```python
from main import compare_product_prices
import json

# Product URLs
product_urls = [
    "https://amazon.com/dp/B0C1XYZAB",
    "https://walmart.com/ip/987654321",
    "https://bestbuy.com/site/123456789"
]

# Get comparison
result = compare_product_prices(product_urls)

# Save results
with open("price_comparison.json", "w") as f:
    json.dump(result, f, indent=2)

# Print summary
if result["success"]:
    print(f"✓ Successfully extracted prices from {result['summary']['successful_extractions']} vendors")
    print(f"✗ Failed to extract from {result['summary']['failed_extractions']} vendors")
    print(f"💰 Savings potential: ${result['summary']['savings_potential']}")
```

### Scenario 2: Find Price Anomalies

```python
from main import compare_product_prices

result = compare_product_prices([
    "https://amazon.com/dp/B0C1XYZAB",
    "https://walmart.com/ip/987654321",
    "https://target.com/p/123456789",
    "https://bestbuy.com/site/123456789"
])

if result["success"] and result["comparison"]["outliers"]:
    print("⚠️ Price Anomalies Detected:")
    for outlier_price in result["comparison"]["outliers"]:
        for price_data in result["price_details"]:
            if price_data["price"] == outlier_price:
                print(f"  - {price_data['vendor']}: ${outlier_price}")
                print(f"    (Average: ${result['comparison']['average_price']})")
```

### Scenario 3: Track Price from Specific Vendor

```python
from main import extract_product_price

vendor = "amazon"
product_id = "B0C1XYZAB"
url = f"https://amazon.com/dp/{product_id}"

result = extract_product_price(url)

if result["success"]:
    print(f"✓ {result['vendor']}: ${result['price']}")
    print(f"  Availability: {result.get('availability', 'Unknown')}")
else:
    print(f"✗ Error: {result['error']}")
    print(f"  Suggestion: {result.get('recovery_suggestion', 'Try again later')}")
```

## API Response Examples

### Extract Product Price Response

```json
{
  "success": true,
  "vendor": "Amazon",
  "product_name": "Wireless Headphones Pro",
  "price": 29.99,
  "currency": "USD",
  "availability": "In Stock",
  "url": "https://amazon.com/dp/B08W3XYZAB",
  "validation_status": "Validation passed",
  "raw_price_text": "$29.99"
}
```

### Compare Prices Response

```json
{
  "success": true,
  "comparison": {
    "min_price": 24.99,
    "max_price": 34.99,
    "average_price": 29.66,
    "price_variance": 10.0,
    "price_variance_percent": 33.67,
    "cheapest_vendor": "Walmart",
    "most_expensive_vendor": "BestBuy",
    "price_count": 3,
    "outliers": []
  },
  "price_details": [
    {
      "vendor": "Amazon",
      "price": 29.99,
      "product_name": "Wireless Headphones Pro",
      "availability": "In Stock",
      "url": "https://amazon.com/dp/B08W3XYZAB"
    }
  ],
  "summary": {
    "total_urls_processed": 3,
    "successful_extractions": 3,
    "failed_extractions": 0,
    "savings_potential": 10.0
  }
}
```

## Error Handling

### Graceful Error Handling

```python
from main import extract_product_price

urls = [
    "https://amazon.com/dp/INVALID",
    "https://walmart.com/ip/987654321",
    "not-a-valid-url"
]

for url in urls:
    result = extract_product_price(url)
    
    if result["success"]:
        print(f"✓ {url}")
        print(f"  Price: ${result['price']}")
    else:
        print(f"✗ {url}")
        print(f"  Error: {result['error']}")
        if "recovery_suggestion" in result:
            print(f"  Fix: {result['recovery_suggestion']}")
```

## Supported Vendors

| Vendor | URL Example | Status |
|--------|------------|--------|
| Amazon | amazon.com/dp/ASIN | ✅ Optimized |
| Walmart | walmart.com/ip/ID | ✅ Optimized |
| Target | target.com/p/ID | ✅ Generic |
| Best Buy | bestbuy.com/site/ID | ✅ Generic |
| eBay | ebay.com/itm/ID | ✅ Generic |
| Any other site | example.com/product | ✅ Generic |

## Tips & Best Practices

### ✅ Do's

- ✅ Use complete product URLs with product IDs
- ✅ Check the `success` field in responses
- ✅ Handle failed extractions gracefully
- ✅ Use `compare_product_prices()` for same product across vendors
- ✅ Check `validation_status` for quality assurance
- ✅ Review outliers before using data

### ❌ Don'ts

- ❌ Use shortened URLs (like bit.ly links)
- ❌ Make rapid sequential requests (use caching)
- ❌ Assume all extractions will succeed
- ❌ Trust prices without checking validation status
- ❌ Compare prices from different products
- ❌ Share API tokens in public repositories

## Performance Tips

### 1. Cache Results

```python
import json
from datetime import datetime, timedelta
from main import extract_product_price

cache_file = "price_cache.json"

def get_price_cached(url, cache_hours=1):
    # Load cache
    try:
        with open(cache_file) as f:
            cache = json.load(f)
    except:
        cache = {}
    
    # Check if cached and fresh
    if url in cache:
        cached_time = datetime.fromisoformat(cache[url]["timestamp"])
        if datetime.now() - cached_time < timedelta(hours=cache_hours):
            return cache[url]["result"]
    
    # Fetch fresh data
    result = extract_product_price(url)
    
    # Save to cache
    cache[url] = {
        "timestamp": datetime.now().isoformat(),
        "result": result
    }
    with open(cache_file, "w") as f:
        json.dump(cache, f)
    
    return result
```

### 2. Batch Processing

```python
from main import extract_product_price
import time

def batch_extract(urls, delay=1):
    """Extract prices with delay between requests"""
    results = []
    for i, url in enumerate(urls):
        print(f"Processing {i+1}/{len(urls)}: {url}")
        result = extract_product_price(url)
        results.append(result)
        
        if i < len(urls) - 1:
            time.sleep(delay)  # Avoid rate limiting
    
    return results
```

## Troubleshooting

### Issue: "Price not extracted"

**Solution 1**: Verify the URL is correct
```python
result = extract_product_price("https://amazon.com/dp/B08W3XYZAB")
print(result.get("error"))  # Check error message
```

**Solution 2**: Website HTML may have changed
- Update vendor scraper selectors in `vendors.py`
- Test with generic scraper: update URL to a different retailer to verify Decodo works

### Issue: "Website can't be crawled"

**Solution**: Check Decodo API
```bash
curl -X POST https://scraper-api.decodo.com/v2/scrape \
  -H "Authorization: Basic YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://amazon.com", "headless": "html"}'
```

### Issue: Invalid API Token

**Solution**: Get new token
- Visit https://visit.decodo.com/aOL4yR
- Copy token without spaces
- Update `decodo_token` in `main.py`

## Next Steps

1. **Read**: [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for technical details
2. **Test**: Run `pytest test_pricing.py -v` to verify setup
3. **Integrate**: Use the tools in your Egaroshi platform
4. **Monitor**: Track prices and detect anomalies
5. **Extend**: Add support for more vendors as needed

## Support

- 📖 Full Documentation: See [README.md](README.md)
- 🔧 Implementation Details: See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- 📋 Changes: See [CHANGELOG.md](CHANGELOG.md)
- 🧪 Tests: Run `pytest test_pricing.py -v`

---

**Ready to get started? Run your first price extraction in 30 seconds!**

```python
from main import extract_product_price

result = extract_product_price("https://amazon.com/s?k=laptop")
print(f"Price: ${result['price']}")
```
