import pandas as pd
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Load the CSV with state, precinct and link columns
INPUT_CSV = "US Vote Foundation - Cleaned_Voting_Office_Data.csv"
OUTPUT_CSV = "US_Vote_Office_Data_Parsed.csv"


def extract_info_from_html(html: str) -> dict:
    """Parse a single page of office information."""
    soup = BeautifulSoup(html, "html.parser")
    data: dict[str, str] = {}

    # Addresses, emails, phones, faxes, websites are grouped under the
    # .office-addresses container.
    address_blocks = soup.select(".office-addresses .address")
    for i, block in enumerate(address_blocks, start=1):
        addr = block.select_one(".physical")
        email = block.select("a[href^='mailto:']")
        website = block.select("a[href^='http']")
        phone = block.select("a[href^='tel:']:not([href*='fax'])")
        fax = block.select("a[href^='tel:'][href*='fax']")

        if addr:
            data[f"Address {i}"] = addr.get_text(" ", strip=True)
        if email:
            data[f"Email {i}"] = email[0].get_text(strip=True)
        if website:
            data[f"Website {i}"] = website[0].get("href")
        if phone:
            data[f"Phone {i}"] = phone[0].get_text(strip=True)
        if fax:
            data[f"Fax {i}"] = fax[0].get_text(strip=True)

    # Officials with their contact info live inside the .office-officials section.
    officials = soup.select(".office-officials .official")
    for i, official in enumerate(officials, start=1):
        title = official.select_one(".title-row .label h4")
        name = official.select_one(".title-row .value")
        phone = official.select_one("a[href^='tel:']:not([href*='fax'])")
        fax = official.select_one("a[href^='tel:'][href*='fax']")
        email = official.select_one("a[href^='mailto:']")

        if title:
            data[f"Official {i} Title"] = title.get_text(strip=True)
        if name:
            data[f"Official {i} Name"] = name.get_text(strip=True)
        if phone:
            data[f"Official {i} Phone"] = phone.get_text(strip=True)
        if fax:
            data[f"Official {i} Fax"] = fax.get_text(strip=True)
        if email:
            data[f"Official {i} Email"] = email.get_text(strip=True)

    return data


def parse_links(df: pd.DataFrame) -> pd.DataFrame:
    """Visit each link in the CSV and extract information."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for idx, row in df.iterrows():
            url = row.get("Link")
            if not isinstance(url, str) or not url:
                continue
            try:
                print(f"Processing: {url}")
                page.goto(url, timeout=60000)
                time.sleep(3)  # allow dynamic content to load
                html = page.content()
                extracted = extract_info_from_html(html)

                # Add columns as needed and populate values
                for key, value in extracted.items():
                    if key not in df.columns:
                        df[key] = ""
                    df.at[idx, key] = str(value)
            except Exception as exc:  # broad catch to continue processing
                print(f"Failed to process {url}: {exc}")

        browser.close()

    return df


def main() -> None:
    # Read all columns as strings to avoid dtype warnings when assigning
    df = pd.read_csv(INPUT_CSV, dtype=str)
    updated = parse_links(df)
    updated.to_csv(OUTPUT_CSV, index=False)


if __name__ == "__main__":
    main()
