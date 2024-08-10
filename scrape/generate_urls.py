import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def should_visit(url):
    unwanted_terms = ["terms-of-use", "privacy-policy", "talk-to-sales"]
    return not any(term in url.lower() for term in unwanted_terms)


def get_domain_urls(url, max_pages=1000):
    visited = set()
    to_visit = [url]
    domain = urlparse(url).netloc

    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)

        if not should_visit(current_url):
            continue

        try:
            response = requests.get(current_url)
            if response.status_code == 200:
                visited.add(current_url)
                print(f"Visited: {current_url}")

                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(current_url, link['href'])
                    if urlparse(full_url).netloc == domain and full_url not in visited and full_url not in to_visit:
                        if should_visit(full_url):
                            to_visit.append(full_url)
                        else:
                            pass
            else:
                print(f"Failed to access: {current_url}")
        except Exception as e:
            print(f"Error accessing {current_url}: {str(e)}")

    return list(visited)

base_url = "https://artisan.co"
urls = get_domain_urls(base_url)
urls = sorted(urls)

# Save URLs to CSV in a single column
with open('./scrape/urls.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    for url in urls:
        writer.writerow([url])
