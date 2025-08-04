import argparse
import json
from pyselsearch import GoogleSearch


def main():
    parser = argparse.ArgumentParser(description="Google Search scraper using SeleniumBase")
    parser.add_argument("query", type=str, help="Search query string")
    parser.add_argument("--no-headless", action="store_true", help="Disable headless mode (browser will be visible)")
    parser.add_argument("--proxy", type=str, default=None, help="Proxy server, e.g., 'user:pass@1.2.3.4:8080'")
    parser.add_argument("--lang", type=str, default="en", help="Google language code, e.g., 'en', 'bn', 'hi'")
    parser.add_argument("--sleep", type=int, default=2, help="Sleep time between actions (seconds)")
    args = parser.parse_args()

    scraper = GoogleSearch(
        headless=not args.no_headless,
        lang=args.lang,
        proxy=args.proxy
    )
    results = scraper.search(args.query, sleep_time=args.sleep)
    print(json.dumps(results, indent=3, ensure_ascii=False))


if __name__ == "__main__":
    main()
