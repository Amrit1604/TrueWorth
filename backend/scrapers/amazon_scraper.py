"""
Amazon India scraper with advanced product extraction
"""
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re


class AmazonScraper(BaseScraper):
    """Amazon India scraper"""

    def __init__(self):
        super().__init__("Amazon", "https://www.amazon.in")

    def search(self, query, max_results=10):
        """Search Amazon India for products"""
        if not self.driver:
            self.setup_driver()

        if not self.driver:
            return []

        try:
            self.safe_wait(2, 4)

            search_url = f"{self.base_url}/s?k={query.replace(' ', '+')}"
            print(f"🔍 {self.platform_name}: Searching {search_url}")

            self.driver.get(search_url)

            # Wait for results
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-component-type='s-search-result']"))
                )
            except TimeoutException:
                print(f"⚠️ {self.platform_name}: Timeout waiting for results")
                return []

            products = []
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")

            for element in product_elements[:max_results]:
                try:
                    product = self._extract_product(element)
                    if product:
                        products.append(product)
                except Exception as e:
                    continue

            print(f"✅ {self.platform_name}: Found {len(products)} products")
            return products

        except Exception as e:
            print(f"❌ {self.platform_name}: Search error - {e}")
            return []

    def _extract_product(self, element):
        """Extract product data from Amazon result element"""

        # Title
        title = "N/A"
        try:
            title_elem = element.find_element(By.CSS_SELECTOR, "h2 a span")
            title = title_elem.text.strip()
        except NoSuchElementException:
            return None

        # URL
        url = "#"
        try:
            url_elem = element.find_element(By.CSS_SELECTOR, "h2 a")
            href = url_elem.get_attribute("href")
            url = href if href.startswith('http') else f"{self.base_url}{href}"
        except NoSuchElementException:
            pass

        # Price
        price = "N/A"
        price_numeric = None
        try:
            price_elem = element.find_element(By.CSS_SELECTOR, ".a-price-whole")
            price_text = price_elem.text.replace(',', '').strip()
            price = f"₹{price_text}"
            price_numeric = self.extract_numeric_price(price)
        except NoSuchElementException:
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, ".a-price .a-offscreen")
                price = price_elem.get_attribute("textContent").strip()
                price_numeric = self.extract_numeric_price(price)
            except NoSuchElementException:
                pass

        # Rating
        rating = "N/A"
        try:
            rating_elem = element.find_element(By.CSS_SELECTOR, ".a-icon-alt")
            rating_text = rating_elem.get_attribute("textContent")
            if "out of" in rating_text:
                rating = rating_text.split()[0] + "⭐"
        except NoSuchElementException:
            pass

        # Image
        image_url = ""
        try:
            img_elem = element.find_element(By.CSS_SELECTOR, ".s-image")
            image_url = img_elem.get_attribute("src")
        except NoSuchElementException:
            pass

        # Availability
        availability = "In Stock"
        try:
            availability_elem = element.find_element(By.CSS_SELECTOR, ".a-color-price")
            if "unavailable" in availability_elem.text.lower():
                availability = "Out of Stock"
        except NoSuchElementException:
            pass

        # Discount
        discount = None
        try:
            discount_elem = element.find_element(By.CSS_SELECTOR, ".s-price-instructions-style .a-letter-space")
            discount_text = discount_elem.text.strip()
            discount_match = re.search(r'(\d+)%', discount_text)
            if discount_match:
                discount = int(discount_match.group(1))
        except NoSuchElementException:
            pass

        if title == "N/A" or price == "N/A":
            return None

        return {
            'title': title,
            'price': price,
            'price_numeric': price_numeric,
            'rating': rating,
            'url': url,
            'platform': self.platform_name,
            'image': image_url,
            'availability': availability,
            'discount': discount
        }
