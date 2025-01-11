# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import json
# import time

# # Setup Selenium WebDriver
# options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Run headless for background execution
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# # URL to open
# url = "https://makerworld.com/_next/data/T0a8pKW84lGO4a08npN-0/en/search/models.json?keyword={self.query}&limit={self.limit}&offset=0"

# # Open the URL
# driver.get(url)

# # Wait for the page to load (adjust if needed)
# time.sleep(5)

# # Get the page content
# page_source = driver.page_source

# # Assuming the JSON data is available within the page's source code, you can now parse it.
# # If the JSON is rendered in the page's JavaScript, you might need to inspect the page source more thoroughly.

# # Alternatively, if the data is in a script tag, you could use this method:
# json_data = driver.find_element(By.TAG_NAME, 'pre').text  # Or whatever the element contains JSON

# # Load the content as JSON
# data = json.loads(json_data)

# # Print the data
# print(json.dumps(data, indent=4))

# # Close the browser
# driver.quit()






import asyncio
from pyppeteer import launch
from pyppeteer.install import install

# Ensure that Chromium is installed (this downloads it if not already installed)
install()

async def main():
    # Launch a headless browser
    browser = await launch(headless=True)  # headless=True runs without GUI
    
    # Create a new browser page
    page = await browser.newPage()
    limit = 4
    query = "Apple"
    # Navigate to the website
    url = "https://makerworld.com/_next/data/T0a8pKW84lGO4a08npN-0/en/search/models.json?keyword={query}&limit={limit}&offset=0"

    await page.goto(url)

    # Take a screenshot of the webpage
    await page.screenshot({'path': 'example_screenshot.png'})

    # Print the title of the page
    title = await page.title()
    print(f"Page Title: {title}")

    # Close the browser
    await browser.close()

# Run the async function
asyncio.get_event_loop().run_until_complete(main())
