import requests
from django.conf import settings
from bs4 import BeautifulSoup
import time


def fetch_jsearch(query, location="India", num_pages=1):
    """Fetch jobs from JSearch (covers LinkedIn/Indeed/Glassdoor/ZipRecruiter)."""
    url = "https://jsearch.p.rapidapi.com/search-v2"
    headers = {
        "x-rapidapi-key": settings.JSEARCH_API_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
    }
    params = {
        "query": f"{query} jobs in {location}",
        "num_pages": num_pages,
        "date_posted": "all",
        "country": "in",
    }

    response = requests.get(url, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    data = response.json().get("data", {}).get("jobs", [])

    jobs = []
    for item in data:
        jobs.append({
            "title": item.get("job_title", ""),
            "company": item.get("employer_name", ""),
            "description": item.get("job_description", ""),
            "location": item.get("job_city") or item.get("job_country") or "",
            "source": "jsearch",
            "source_url": item.get("job_apply_link", ""),
        })
    return jobs


def fetch_adzuna(query, location="India", results=20):
    """Fetch jobs from Adzuna."""
    country_code = "in"  # Adzuna's country code for India
    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    params = {
        "app_id": settings.ADZUNA_APP_ID,
        "app_key": settings.ADZUNA_APP_KEY,
        "what": query,
        "where": location,
        "results_per_page": results,
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json().get("results", [])

    jobs = []
    for item in data:
        jobs.append({
            "title": item.get("title", ""),
            "company": item.get("company", {}).get("display_name", ""),
            "description": item.get("description", ""),
            "location": item.get("location", {}).get("display_name", ""),
            "source": "adzuna",
            "source_url": item.get("redirect_url", ""),
        })
    return jobs

def fetch_internshala(query, location="india", max_results=20):
    """
    Scrapes Internshala's public search results. No API exists, so this
    parses their HTML directly. Respects them with a real User-Agent and
    a small delay; keep result counts modest to stay a good citizen.
    """
    slug_query = query.lower().replace(' ', '-')
    url = f"https://internshala.com/internships/{slug_query}-internship"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    cards = soup.select('div.internship_meta')[:max_results]

    for card in cards:
        title_tag = card.select_one('a.job-title-href') or card.select_one('h3')
        company_tag = card.select_one('a.link_display_like_text') or card.select_one('p.company-name')

        title = title_tag.get_text(strip=True) if title_tag else None
        company = company_tag.get_text(strip=True) if company_tag else None
        link = title_tag['href'] if title_tag and title_tag.has_attr('href') else None

        if title and link:
            jobs.append({
                "title": title,
                "company": company or "Unknown",
                "description": title,  # detail page would have more; keeping it light for now
                "location": location,
                "source": "internshala",
                "source_url": f"https://internshala.com{link}" if link.startswith('/') else link,
            })

    time.sleep(1)  # be polite between requests
    return jobs