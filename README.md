# Decodo Website Scraper

A Model Context Protocol (MCP) server that provides website scraping capabilities using the Decodo scraping API. This tool allows you to extract text content from web pages for processing and analysis.

## Features

- **Website Scraping**: Scrapes publicly accessible websites using the Decodo API
- **Content Extraction**: Extracts clean text content from HTML pages
- **MCP Integration**: Built as an MCP server for seamless integration with AI assistants like Claude
- **Error Handling**: Gracefully handles HTTP errors and unreachable websites

## Project Structure

```
python-decodo-webscrapper/
├── main.py           # MCP server with scraping tool
├── pyproject.toml    # Project dependencies and metadata
└── README.md         # This file
```

## Prerequisites

- Python 3.13 or higher
- A Decodo API token (get a free trial at https://visit.decodo.com/aOL4yR)
- Claude Desktop application

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/miguelmontanez/python-decodo-webscrapper
cd python-decodo-webscrapper
```

2. **Create a Decodo account and obtain your API key**:
   - Visit https://visit.decodo.com/aOL4yR to claim your free trial
   - Copy your API token

3. **Update the API token**:
   - Open `main.py` and replace the `decodo_token` variable with your API token

4. **Install dependencies**:
   - The project uses `uv` for dependency management
```bash
pip install uv
uv sync
```

5. **Connect to Claude Desktop**:
```bash
uv run mcp install main.py
```

## Usage

Once installed, the MCP server provides the following tool:

### `get_article_text(website_url: str) -> str`

Scrapes a website and extracts text content.

**Parameters:**
- `website_url` (string): The URL of the website to scrape

**Returns:**
- The plain text content extracted from the webpage

**Example:**
```python
text = get_article_text("https://example.com/article")
```

## Dependencies

- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `mcp` - Model Context Protocol server
- `pandas` - Data manipulation (optional)

## Configuration

- **API Token**: Set in the `decodo_token` variable in `main.py`
- **Scraping Mode**: Currently configured for HTML headless scraping

## Troubleshooting

- **Website can't be crawled**: The website either blocks automated scraping or is temporarily unavailable. Check the website's robots.txt and terms of service.
- **Invalid API token**: Verify your Decodo API token is correctly set in `main.py`
- **Module not found errors**: Ensure dependencies are installed with `uv sync`

## License

This project is provided as-is for educational and research purposes.

## References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Decodo Scraper API](https://decodo.com/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/)

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
