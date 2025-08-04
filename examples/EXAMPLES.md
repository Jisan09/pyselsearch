# Examples — `pyselsearch`

Some practical usage examples.

## 1. Basic Example

```python
import json
from pyselsearch import GoogleSearch

scraper = GoogleSearch()
results = scraper.search('site:housing.com affordable housing in mumbai')
print(json.dumps(results, indent=2, ensure_ascii=False))
```

## 2. Non-Headless Mode

```python
from pyselsearch import GoogleSearch

scraper = GoogleSearch(headless=False)
results = scraper.search('site:housing.com newly launched projects in pune')
```

## 3. With Proxy

```python
from pyselsearch import GoogleSearch

scraper = GoogleSearch(proxy="user:pass@proxy.example.com:8080")
results = scraper.search('best co-living spaces in Bangalore')
```

## 4. Custom Language (e.g., Hindi)

```python
from pyselsearch import GoogleSearch

scraper = GoogleSearch(lang="hi")
results = scraper.search('सस्ती आवास योजनाएं दिल्ली')
```

## 5. Custom CSS Selectors

```python
# Change Result Selectors (if Google layout changes)

from pyselsearch import GoogleSearch

scraper = GoogleSearch(
    desc_selector=".custom-desc",
    search_selector="input[name='q']",
    results_selector="div.result"
)
results = scraper.search('site:housing.com luxury apartments in Hyderabad')
```

## 6. CLI Example

```bash
pyselsearch "site:housing.com plots near Gandhinagar"
```

### With Proxy, Non-Headless, and Custom Language:

```bash
pyselsearch "site:housing.com villa in goa" --proxy "user:pass@proxy.example.com:8080" --no-headless --lang hi
```

## Output Example

```json
[
  {
    "url": "https://housing.com/in/buy/projects/page/123456",
    "title": "Luxury Apartments in Pune",
    "description": "Find 2BHK, 3BHK flats in premium societies of Pune..."
  }
]
```

---

ℹ️ Use selectors and query syntax as per your scraping need. If Google blocks you or CAPTCHA appears frequently, try proxies or increase delay between steps.