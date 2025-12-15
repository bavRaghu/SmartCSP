import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright


def extract_domain(url):
    try:
        return urlparse(url).netloc
    except:
        return None


def static_scan(url):
    result = {
        "scripts": set(),
        "styles": set(),
        "images": set(),
        "iframes": set(),
        "inline_scripts": 0
    }

    response = requests.get(
        url,
        timeout=10,
        headers={"User-Agent": "SmartCSP-Scanner"}
    )

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup.find_all("script"):
        if tag.get("src"):
            result["scripts"].add(extract_domain(urljoin(url, tag["src"])))
        else:
            if tag.text.strip():
                result["inline_scripts"] += 1

    for tag in soup.find_all("link", rel="stylesheet"):
        if tag.get("href"):
            result["styles"].add(extract_domain(urljoin(url, tag["href"])))

    for tag in soup.find_all("img"):
        if tag.get("src"):
            result["images"].add(extract_domain(urljoin(url, tag["src"])))

    for tag in soup.find_all("iframe"):
        if tag.get("src"):
            result["iframes"].add(extract_domain(urljoin(url, tag["src"])))

    # convert sets → lists
    for key in result:
        if isinstance(result[key], set):
            result[key] = list(filter(None, result[key]))

    return result


def dynamic_scan(url):
    network_requests = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on(
            "request",
            lambda req: network_requests.append({
                "url": req.url,
                "type": req.resource_type
            })
        )

        try:
            page.goto(url, wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(2000)
        except Exception as e:
            network_requests.append({"error": str(e)})

        browser.close()

    return network_requests
