from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json
import time


class MakeWorldProductScrap:
    def __init__(self, query, limit):
        self.query = query
        self.limit = limit
        self.results = []
        self.buildId = None

    def __set_buildId(self):
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(
                headless=False
            )  # headless=False for visible browser
            page = browser.new_page()
            page.goto("https://makerworld.com/en")

            html_content = page.content()
            # Parse the HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # Locate the <script> tag by its ID
            script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
            if script_tag:

                # Extract the content of the <script> tag
                json_content = script_tag.string
                # Parse the JSON data
                data = json.loads(json_content)
                # Get the buildId value
                build_id = data.get("buildId")
                self.buildId = build_id

            return self.buildId

    def __hit_query(self):
        self.__set_buildId()
        url = f"https://makerworld.com/_next/data/{self.buildId}/en/search/models.json?keyword={self.query}&limit={self.limit}&offset=0"
        print(url)
        # Start Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False
            )  # Set headless=True for no browser UI
            page = browser.new_page()

            # Define a callback to handle the response
            def handle_response(response):
                if url in response.url:
                    try:
                        # Parse the JSON data from the response
                        json_data = response.json()
                        self.results = json_data
                        # Save the data to a file
                        # save_json(json_data, 'models.json')
                    except Exception as e:
                        print(f"Error processing JSON: {e}")

            # Set up the response listener
            page.on("response", handle_response)

            # Navigate to the page that triggers the request for the JSON data
            page.goto(url)
            time.sleep(1)
            # Close the browser
            browser.close()

        return None

    def get_products(self):
        self.__hit_query()
        return self.results

    def save_file(self):
        with open("data.json", "w") as f:
            json.dump(self.results, f, indent=4)


if __name__ == "__main__":

    x = MakeWorldProductScrap("apple", 20)
    x.get_products()
    x.save_file()