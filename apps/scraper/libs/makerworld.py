import requests
from bs4 import BeautifulSoup
import json
from django.conf import settings

class MakerWorldProductScrap:
    def __init__(self, query, limit):
        """
        Initialize with the query and limit for scraping.
        """
        self.query = query
        self.limit = limit
        self.results = []
        self.key = "makerworld"

    def _apply_limit(self):
        self.results = self.results[:self.limit]

    def _fetch_html_from_microservice(self, url):
        """
        Fetch the HTML content using the microservice.

        :param url: The URL to scrape.
        :return: The HTML content as a string.
        """
        payload = {
            "operation": "scrape",
            "url": url
        }
        response = requests.post("https://scrape.distack-solutions.com/process/", json=payload)
        if response.status_code == 200:
            output = response.json()
            return output.get('content')
        else:
            raise Exception(f"Failed to scrape the URL. Status code: {response.status_code}, Response: {response.text}")

    def _extract_json_from_html(self, html_content):
        """
        Extract JSON data from the <script> tag with id "__NEXT_DATA__".

        :param html_content: The HTML content as a string.
        :return: The extracted JSON data.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
        if not script_tag:
            raise Exception("Could not find the '__NEXT_DATA__' script tag in the HTML.")
        
        json_content = script_tag.string
        data = json.loads(json_content)
        return data.get("props", {}).get("pageProps", {}).get("designs", [])

    def get_products(self):
        """
        Fetch and parse products from the microservice and extract relevant data.

        :return: List of raw product data.
        """
        search_url = f"https://makerworld.com/en/search/models?keyword={self.query}&licenses=BY,BY-SA,BY-ND"
        html_content = self._fetch_html_from_microservice(search_url)
        self.results = self._extract_json_from_html(html_content)
        self._apply_limit()
        return self.results

    def save_file(self):
        """
        Save the scraped data to a local JSON file.
        """
        with open("data.json", "w") as f:
            json.dump(self.results, f, indent=4)

    def to_model_data(self):
        """
        Convert raw product data into a structured format for creating models.

        :return: List of structured product data.
        """
        model_data = []
        for product in self.results:
            try:
                license_type = product.get("license")

                model = {
                    "sku": f'{self.key}-{str(product.get("id", ""))}',
                    "title": product.get("title", ""),
                    "description": ", ".join(product.get("tags", [])) if product.get("tags") else "No description available",
                    "category": ", ".join(product.get("tags", [])) if product.get("tags") else None,
                    "license": license_type,
                    "thumbnail_url": product.get("cover", ""),
                    "images": [product.get("cover")] if product.get("cover") else [],
                    "is_commercial_allowed": True,
                }
                model_data.append(model)
            except Exception as e:
                print(f"Error processing product data: {e}")
                continue

        return model_data


if __name__ == "__main__":
    # Example usage
    scraper = MakerWorldProductScrap(query="apple", limit=10)
    scraper.get_products()
    scraper.save_file()
    structured_data = scraper.to_model_data()
