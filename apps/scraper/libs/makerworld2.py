from playwright.async_api import async_playwright
import asyncio
import uuid
import json
from urllib.parse import urljoin


class ScrapeSite:
    def __init__(self, query, base_url=None):
        self.query = query
        self.url = f"https://makerworld.com/en/search/models?keyword={self.query}&licenses=BY,BY-SA,BY-ND"
        self.error = False
        self.message = None
        self.title = None
        self.screenshot = None
        self.links = []
        self.products = []  # Store product details scraped from each product page
        self.base_url = base_url

    async def __run_playwright(self) -> None:
        try:
            # Launch Playwright asynchronously
            async with async_playwright() as p:
                # Launch a Firefox browser instance
                browser = await p.firefox.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Navigate to the search page
                await page.goto(self.url, timeout=60000)

                # Extract the page title
                self.title = await page.title()

                # Extract all <a> links within div.design-cover-wrap
                elements = await page.query_selector_all("div.design-cover-wrap a")
                self.links = [
                    urljoin(self.url, await element.get_attribute("href")) for element in elements
                ]

                # Close the browser
                await browser.close()

        except Exception as e:
            self.message = f"An error occurred: {e}"
            self.error = True

    async def scrape_links(self):
        """
        Visit each link and scrape the JSON data from the script tag.
        """
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.firefox.launch(headless=True)
                context = await browser.new_context()

                for link in self.links:
                    page = await context.new_page()
                    try:
                        await page.goto(link, timeout=60000)

                        # Extract JSON data from <script> tag
                        script_tag = await page.query_selector("script#__NEXT_DATA__")
                        if script_tag:
                            json_content = await script_tag.text_content()
                            product_data = self._process_json_data(json_content)
                            self.products.append(product_data)
                        else:
                            self.products.append({"link": link, "error": "No script tag found"})
                    except Exception as e:
                        self.products.append({"link": link, "error": str(e)})
                    finally:
                        await page.close()

                await browser.close()

        except Exception as e:
            self.message = f"An error occurred while scraping links: {e}"
            self.error = True

    def _process_json_data(self, json_content):
        """
        Parse and process JSON data from the script tag.
        """
        try:
            data = json.loads(json_content)
            design = data.get("props", {}).get("pageProps", {}).get("design", {})
            return design
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON data: {e}"}

    async def is_error(self) -> bool:
        await self.__run_playwright()
        if self.links:  # Scrape each link only if links are found
            await self.scrape_links()
        return self.error

    def info(self):
        context = {
            "site": self.url,
            "title": self.title,
            "search_links": self.links,
            "products": self.products,
            "message": self.message,
        }
        return context


# This block is for running the code asynchronously
async def main():
    # Example query provided by user
    query = "apple"
    x = ScrapeSite(query, "http://127.0.0.1:8000")
    await x.is_error()
    # result = json.dumps(x.info(), indent=4)

    with open("data.json", "w") as f:
        json.dump(x.info(), f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())
