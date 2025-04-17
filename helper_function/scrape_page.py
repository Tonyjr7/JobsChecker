from bs4 import BeautifulSoup
import requests
import logging


class ScrapePage:
    def scrape_page(self, url: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except requests.RequestException as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to scrape {url}: {str(e)}")

scrape = ScrapePage()