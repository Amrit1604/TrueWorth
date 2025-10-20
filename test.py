from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Set True to run in background
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.fill("textarea[name='q']", "Pizza")
    page.press("textarea[name='q']", "Enter")
    page.wait_for_timeout(2000)  # Wait for results to load
    page.screenshot(path="result.png")
    browser.close()
