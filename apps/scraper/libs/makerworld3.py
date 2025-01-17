import asyncio
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import json
import datetime
from django.core.files import File
from tempfile import NamedTemporaryFile
from apps.scraper.models import PageScreenshot
from django.conf import settings
import os

class MakerWorldProductScraper:
    def __init__(self, query, limit):
        """
        Initialize with the query and limit for scraping.
        """
        self.query = query
        self.limit = limit
        self.search_url = f"https://makerworld.com/en/search/models?keyword={self.query}&licenses=BY,BY-SA,BY-ND"
        self.results = []
        self.products = []
        self.key = "makerworld"
        self.error = None

    def _fetch_search_results(self):
        """
        Fetch search results and extract product links using Playwright.
        """
        try:
            with sync_playwright() as p:
                browser = p.firefox.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )
                context = browser.new_context()
                page = context.new_page()
                
                # Add logging
                page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
                page.on("pageerror", lambda err: print(f"Page error: {err}"))

                # Set a longer timeout and add logging
                print(f"Navigating to: {self.search_url}")
                page.goto(self.search_url, timeout=60000)
                print("Page loaded successfully")

                # Wait for the content to load
                page.wait_for_selector("div.design-cover-wrap", timeout=30000)
                print("Content loaded successfully")

                # Extract all <a> links within div.design-cover-wrap
                elements = page.query_selector_all("div.design-cover-wrap a")
                self.results = [
                    urljoin(self.search_url, element.get_attribute("href"))
                    for element in elements
                ]

                # Limit the results based on the provided limit
                self.results = self.results[:self.limit]
                print(f"Found {len(self.results)} results")

                # Close the browser
                browser.close()

        except Exception as e:
            import traceback
            print(f"Error in _fetch_search_results: {str(e)}")
            print(traceback.format_exc())
            self.error = f"Failed to fetch search results: {str(e)}"

    def _process_and_save_screenshot(self, page, product_id):
        """
        Capture a screenshot, save it to the database, and return the database ID.
        """

        try:
            screenshot_filename_name = f"{product_id}_screenshot.png"
            # Take a screenshot of the product page
            screenshot_filename = os.path.join(
                settings.MEDIA_ROOT, "page-screenshot", screenshot_filename_name
            )
            os.makedirs(os.path.dirname(screenshot_filename), exist_ok=True)
            page.screenshot(path=screenshot_filename, full_page=True)

            # Return the database ID of the saved screenshot
            return {
                "path": screenshot_filename,
                "filename" : screenshot_filename_name 
            }
            
        except Exception as e:
            print(f"Error processing screenshot for product {product_id}: {e}")
            return None


    def _scrape_product_page(self, product_url):
        """
        Scrape a product page and extract JSON data from the <script> tag.
        """
        try:
            with sync_playwright() as p:
                print(f"Fetching product: {product_url}")
                browser = p.firefox.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )
                context = browser.new_context()
                page = context.new_page()

                # Add logging
                page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
                page.on("pageerror", lambda err: print(f"Page error: {err}"))

                # Navigate to the product page with logging
                print(f"Navigating to product page: {product_url}")
                page.goto(product_url, timeout=60000)
                print("Product page loaded successfully")

                # Extract JSON data from <script> tag with id "__NEXT_DATA__"
                script_tag = page.query_selector("script#__NEXT_DATA__")
                if not script_tag:
                    print("No script tag found on page")
                    return {"url": product_url, "error": "No script tag found"}

                json_content = script_tag.text_content()
                product_data = self._process_json_data(json_content)

                # Process and save the screenshot
                screenshot = self._process_and_save_screenshot(page, product_data["id"])
                if screenshot:
                    product_data["screenshot_info"] = screenshot

                return product_data

        except Exception as e:
            import traceback
            print(f"Error scraping product page {product_url}: {str(e)}")
            print(traceback.format_exc())
            return {"url": product_url, "error": str(e)}
        
    def _check_environment(self):
        """
        Check if the environment is properly set up for scraping.
        """
        try:
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.goto("about:blank")
                browser.close()
                return True
        except Exception as e:
            print(f"Environment check failed: {str(e)}")
            return False
   
    def _process_json_data(self, json_content):
        """
        Parse and process JSON data from the script tag.
        """
        try:
            data = json.loads(json_content)
            design = data.get("props", {}).get("pageProps", {}).get("design", {})
            images = design.get("designExtension", {}).get("design_pictures", [])
            image_urls = [image.get("url") for image in images]
            return {
                "id": design.get("id"),
                "title": design.get("title"),
                "summary": design.get("summary"),
                "categories": [category.get("name") for category in design.get("categories", [])],
                "coverUrl": design.get("coverUrl"),
                "like_count": design.get("likeCount"),
                "collection_count": design.get("collectionCount"),
                "print_count": design.get("printCount"),
                "download_count": design.get("downloadCount"),
                "image_urls": image_urls,
                "creator": {
                    "name": design.get("designCreator", {}).get("name"),
                    "handle": design.get("designCreator", {}).get("handle"),
                },
                "create_time": design.get("createTime"),
            }
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON data: {e}"}

    def get_products(self):
        """
        Fetch search results and scrape each product page.
        """
        if not self._check_environment():
            raise Exception("Browser environment is not properly configured")

        self._fetch_search_results()
        self._apply_limit()

        if self.error:
            raise Exception(self.error)

        # Fetch product details for each link
        for product_url in self.results:
            product_data = self._scrape_product_page(product_url)
            self.products.append(product_data)

        return self.products

    def _apply_limit(self):
        self.results = self.results[:self.limit]

    def save_file(self, filename="data.json"):
        """
        Save the scraped product data to a local JSON file.
        """
        with open(filename, "w") as f:
            json.dump(self.products, f, indent=4)

    def to_model_data(self):
        """
        Convert raw product data into a structured format for creating models.
        """
        model_data = []
        for product in self.products:
            if "error" in product:
                continue  # Skip products with errors

            try:
                model = {
                    "sku": f'{self.key}-{product.get("id", "")}',
                    "author_name": product.get("creator", {}).get("name", ""),
                    "title": product.get("title", ""),
                    "description": product.get("summary", ""),  # You can enhance this with actual tags if available
                    "category": ",".join(product.get("categories")),
                    "thumbnail_url": product.get("coverUrl", ""),
                    "images": product.get("image_urls", []),
                    "is_commercial_allowed": True,
                    "screenshot_info": product.get("screenshot_info"),
                }
                model_data.append(model)
            except Exception as e:
                print(f"Error processing product data: {e}")
                continue

        return model_data


# Example usage
def main():
    scraper = MakerWorldProductScraper(query="apple", limit=2)
    scraper.get_products()
    scraper.save_file()
    structured_data = scraper.to_model_data()
    print(json.dumps(structured_data, indent=4))



if __name__ == "__main__":
    print("started", datetime.datetime.now())
    main()
    print("ended",datetime.datetime.now())
