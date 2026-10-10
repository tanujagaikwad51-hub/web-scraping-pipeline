import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


URL = "https://quotes.toscrape.com/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    )
}


def create_session():
    """Create a requests session with retry logic."""

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def scrape_quotes():
    """Scrape quotes, authors and tags."""

    session = create_session()

    print("Starting web scraping...")
    print(f"URL: {URL}")

    try:
        response = session.get(
            URL,
            headers=HEADERS,
            timeout=10
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print(f"Error while requesting website: {error}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    quotes_data = []

    quote_blocks = soup.select("div.quote")

    print(f"Quotes found: {len(quote_blocks)}")

    for quote in quote_blocks:

        quote_text = quote.select_one("span.text")
        author = quote.select_one("small.author")
        tags = quote.select("div.tags a.tag")

        quote_text = (
            quote_text.get_text(strip=True)
            if quote_text
            else ""
        )

        author = (
            author.get_text(strip=True)
            if author
            else ""
        )

        tag_list = [
            tag.get_text(strip=True)
            for tag in tags
        ]

        quotes_data.append({
            "quote": quote_text,
            "author": author,
            "tags": ", ".join(tag_list)
        })

        # Rate limiting
        time.sleep(1)

    df = pd.DataFrame(quotes_data)

    # Save scraped data
    df.to_csv(
        "quotes.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Calculate statistics
    total_quotes = len(df)
    unique_authors = df["author"].nunique()
    unique_tags = df["tags"].nunique()

    # Create automatic report
    with open("report.txt", "w", encoding="utf-8") as report:

        report.write("WEB SCRAPING SUMMARY REPORT\n")
        report.write("=" * 35 + "\n\n")

        report.write(f"Source URL: {URL}\n\n")

        report.write("DATA SUMMARY\n")
        report.write("-" * 20 + "\n")
        report.write(f"Total quotes: {total_quotes}\n")
        report.write(f"Unique authors: {unique_authors}\n")
        report.write(f"Unique tag combinations: {unique_tags}\n\n")

        report.write("TOP AUTHORS\n")
        report.write("-" * 20 + "\n")

        author_counts = df["author"].value_counts()

        for author, count in author_counts.head(5).items():
            report.write(f"{author}: {count} quote(s)\n")

    print("\nScraping completed successfully!")
    print(f"Total records collected: {total_quotes}")
    print("Data saved to: quotes.csv")
    print("Summary report saved to: report.txt")

    print("\nSummary Statistics:")
    print(f"Total quotes: {total_quotes}")
    print(f"Unique authors: {unique_authors}")
    print(f"Unique tags: {unique_tags}")


if __name__ == "__main__":
    scrape_quotes()