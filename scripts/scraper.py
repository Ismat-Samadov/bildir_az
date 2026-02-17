#!/usr/bin/env python3
"""
bildir.az Company Scraper
Scrapes all companies from bildir.az/sirketler/ and their detail pages.
Output: data/data.csv
"""

import csv
import time
import logging
import os
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "https://www.bildir.az"
LIST_URL = f"{BASE_URL}/sirketler/"
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "data.csv")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "az,en-US;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

REQUEST_DELAY = 1.0   # seconds between requests
MAX_RETRIES   = 3
TIMEOUT       = 15

CSV_FIELDS = [
    "slug",
    "name",
    "category",
    "founded",
    "description",
    "website",
    "facebook",
    "instagram",
    "linkedin",
    "youtube",
    "twitter",
    "overall_rating",
    "total_reviews",
    "response_rate_pct",
    "resolved_complaints_pct",
    "customer_loyalty_pct",
    "star5_pct",
    "star4_pct",
    "star3_pct",
    "star2_pct",
    "star1_pct",
    "profile_url",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------
session = requests.Session()
session.headers.update(HEADERS)


def get(url: str) -> BeautifulSoup | None:
    """Fetch a URL with retries; return BeautifulSoup or None on failure."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as exc:
            log.warning("Attempt %d/%d failed for %s: %s", attempt, MAX_RETRIES, url, exc)
            if attempt < MAX_RETRIES:
                time.sleep(REQUEST_DELAY * attempt)
    log.error("Giving up on %s", url)
    return None


# ---------------------------------------------------------------------------
# Listing page – collect slugs
# ---------------------------------------------------------------------------
def get_total_pages(soup: BeautifulSoup) -> int:
    """Parse pagination to find the last page number."""
    # Look for pagination links with page numbers
    pagination = soup.select("ul.pagination a, .pagination a, a[href*='page=']")
    max_page = 1
    for tag in pagination:
        href = tag.get("href", "")
        m = re.search(r"page=(\d+)", href)
        if m:
            max_page = max(max_page, int(m.group(1)))
    # Also check text like "106" inside pagination spans
    for tag in soup.select("ul.pagination li, .pagination li"):
        txt = tag.get_text(strip=True)
        if txt.isdigit():
            max_page = max(max_page, int(txt))
    return max_page


def parse_listing_page(soup: BeautifulSoup) -> list[dict]:
    """Return list of {slug, name, category, rating, review_count} from a listing page."""
    companies = []
    for anchor in soup.select("a.company-wrapper"):
        href = anchor.get("href", "")
        slug = href.strip("/").split("/")[-1] if href else ""
        if not slug:
            continue

        name_tag = anchor.select_one("h5")
        name = name_tag.get_text(strip=True) if name_tag else ""

        # Category is usually the first <p> or a span after the name
        category = ""
        for p in anchor.select("p"):
            txt = p.get_text(strip=True)
            if txt and "Rəy" not in txt and "www" not in txt:
                category = txt
                break

        # Rating number
        rating_tag = anchor.select_one(".company-rating-number, .rating-number")
        rating = ""
        if rating_tag:
            rating = rating_tag.get_text(strip=True).replace(",", ".")
        else:
            # Try to grab the first float-like text node near stars
            for span in anchor.select("span, div"):
                t = span.get_text(strip=True).replace(",", ".")
                if re.match(r"^\d\.\d$", t):
                    rating = t
                    break

        # Review count
        review_count = ""
        full_text = anchor.get_text(" ", strip=True)
        m = re.search(r"Rəy\s*say[ıi]\s*:\s*(\d+)", full_text, re.IGNORECASE)
        if m:
            review_count = m.group(1)

        companies.append({
            "slug": slug,
            "name": name,
            "category": category,
            "rating_listing": rating,
            "review_count_listing": review_count,
        })
    return companies


def collect_all_slugs() -> list[dict]:
    """Iterate all listing pages and return company stubs."""
    log.info("Fetching page 1 to detect total pages …")
    soup = get(f"{LIST_URL}?page=1")
    if soup is None:
        log.error("Could not fetch listing page 1.")
        return []

    total = get_total_pages(soup)
    log.info("Total pages detected: %d", total)

    all_companies: list[dict] = []
    all_companies.extend(parse_listing_page(soup))
    time.sleep(REQUEST_DELAY)

    for page in range(2, total + 1):
        log.info("Listing page %d/%d …", page, total)
        soup = get(f"{LIST_URL}?page={page}")
        if soup:
            all_companies.extend(parse_listing_page(soup))
        time.sleep(REQUEST_DELAY)

    log.info("Collected %d company slugs.", len(all_companies))
    return all_companies


# ---------------------------------------------------------------------------
# Company detail page
# ---------------------------------------------------------------------------
def _text(soup: BeautifulSoup, *selectors) -> str:
    for sel in selectors:
        tag = soup.select_one(sel)
        if tag:
            return tag.get_text(strip=True)
    return ""


def _pct(text: str) -> str:
    """Extract numeric percentage from strings like '54,5%' → '54.5'."""
    m = re.search(r"([\d,\.]+)\s*%", text)
    if m:
        return m.group(1).replace(",", ".")
    m = re.search(r"([\d,\.]+)", text)
    if m:
        return m.group(1).replace(",", ".")
    return ""


def parse_company_page(slug: str) -> dict:
    """Fetch and parse a company detail page."""
    url = f"{BASE_URL}/{slug}/"
    soup = get(url)
    data: dict = {f: "" for f in CSV_FIELDS}
    data["slug"] = slug
    data["profile_url"] = url

    if soup is None:
        return data

    # Name
    data["name"] = _text(soup,
        "h1.company-name", "h1", ".company-title h1", ".company-info h1")

    # Category
    data["category"] = _text(soup,
        ".company-category", ".category-name", ".company-type")

    # Founded
    founded_tag = soup.find(string=re.compile(r"Quruluş tarixi|Founded|Yaranma", re.I))
    if founded_tag:
        parent = founded_tag.parent
        sibling = parent.find_next_sibling()
        if sibling:
            data["founded"] = sibling.get_text(strip=True)
        else:
            data["founded"] = parent.get_text(strip=True)

    # Description
    data["description"] = _text(soup,
        ".company-description p", ".about-company p",
        ".company-about", "#about p", ".description")

    # Website
    website_tag = soup.select_one("a.website-url-btn, [data-href], .company-website a")
    if website_tag:
        data["website"] = (
            website_tag.get("data-href")
            or website_tag.get("href", "")
        )
    if not data["website"]:
        for a in soup.select("a[href^='http']"):
            href = a.get("href", "")
            if BASE_URL not in href and "bildir" not in href:
                txt = a.get_text(strip=True).lower()
                if not any(s in txt for s in ["facebook", "instagram", "linkedin", "twitter", "youtube"]):
                    data["website"] = href
                    break

    # Social media
    social_map = {
        "facebook": "facebook",
        "instagram": "instagram",
        "linkedin": "linkedin",
        "youtube": "youtube",
        "twitter": "twitter",
    }
    for platform, key in social_map.items():
        tag = soup.select_one(f"a[href*='{platform}']")
        if tag:
            data[key] = tag.get("href", "")

    # Overall rating
    rating_tag = soup.select_one(
        ".overall-rating .rating-number, .company-rating span.number, "
        ".rating-score, .stars-number, .company-score"
    )
    if rating_tag:
        data["overall_rating"] = rating_tag.get_text(strip=True).replace(",", ".")

    # Total reviews
    reviews_tag = soup.select_one(
        ".total-reviews, .reviews-count, .review-count strong"
    )
    if reviews_tag:
        data["total_reviews"] = re.sub(r"\D", "", reviews_tag.get_text())
    else:
        m = re.search(r"(\d+)\s*rəy", soup.get_text(), re.IGNORECASE)
        if m:
            data["total_reviews"] = m.group(1)

    # Stats: response rate, resolved, loyalty
    full_text = soup.get_text(" ", strip=True)

    patterns = {
        "response_rate_pct":      r"Cavab\s+nisbəti[^\d]*([\d,\.]+)\s*%",
        "resolved_complaints_pct": r"Həll\s+edilmiş[^\d]*([\d,\.]+)\s*%",
        "customer_loyalty_pct":   r"Müştəri\s+loyallığı[^\d\-]*([\-\d,\.]+)\s*%",
    }
    for key, pat in patterns.items():
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            data[key] = m.group(1).replace(",", ".")

    # Star distribution  – look for elements with % next to star icons
    # Typical markup: <div class="star-row"><span>5 ulduz</span><span>54,5%</span></div>
    star_keys = {5: "star5_pct", 4: "star4_pct", 3: "star3_pct", 2: "star2_pct", 1: "star1_pct"}
    for row in soup.select(".star-row, .rating-row, .review-bar, li.star-item"):
        txt = row.get_text(" ", strip=True)
        for star_n, col in star_keys.items():
            if str(star_n) in txt:
                pct = _pct(txt)
                if pct and not data[col]:
                    data[col] = pct
                break

    # Fallback: scan full text for patterns like "5 ulduz ... 22,7%"
    for star_n, col in star_keys.items():
        if not data[col]:
            m = re.search(
                rf"{star_n}\s*(?:ulduz|star)[^\d]*?([\d,\.]+)\s*%",
                full_text, re.IGNORECASE
            )
            if m:
                data[col] = m.group(1).replace(",", ".")

    return data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    # Step 1: Collect all slugs from listing pages
    stubs = collect_all_slugs()
    if not stubs:
        log.error("No companies found – aborting.")
        return

    # Remove duplicates (keep order)
    seen = set()
    unique_stubs = []
    for s in stubs:
        if s["slug"] not in seen:
            seen.add(s["slug"])
            unique_stubs.append(s)
    log.info("Unique companies after dedup: %d", len(unique_stubs))

    # Step 2: Scrape each company detail page and write CSV incrementally
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()

        for idx, stub in enumerate(unique_stubs, 1):
            slug = stub["slug"]
            log.info("[%d/%d] Scraping %s …", idx, len(unique_stubs), slug)

            detail = parse_company_page(slug)

            # Backfill name/category from listing if detail page missed them
            if not detail["name"]:
                detail["name"] = stub.get("name", "")
            if not detail["category"]:
                detail["category"] = stub.get("category", "")
            if not detail["overall_rating"]:
                detail["overall_rating"] = stub.get("rating_listing", "")
            if not detail["total_reviews"]:
                detail["total_reviews"] = stub.get("review_count_listing", "")

            writer.writerow(detail)
            fh.flush()

            time.sleep(REQUEST_DELAY)

    log.info("Done! CSV saved to: %s", OUTPUT_CSV)


if __name__ == "__main__":
    main()
