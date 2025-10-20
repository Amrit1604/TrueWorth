"""
Snapdeal scraper
"""
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class SnapdealScraper(BaseScraper):
    """Snapdeal scraper"""

    def __init__(self):
        super().__init__("Snapdeal", "https://www.snapdeal.com")

    def search(self, query, max_results=10):
        """Search Snapdeal for products - TURBO MODE"""
        if not self.driver:
            self.setup_driver()

        if not self.driver:
            return []

        try:
            self.safe_wait(0.5, 1)  # ⚡ Reduced delay

            search_url = f"{self.base_url}/search?keyword={query.replace(' ', '%20')}"
            print(f"⚡ {self.platform_name}: TURBO searching...")

            self.driver.get(search_url)
            time.sleep(2)  # ⚡ Reduced from 3s

            products = []
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, ".product-tuple-listing")

            # ⚡ Max 5 for speed
            for element in product_elements[:min(max_results, 5)]:
                try:
                    product = self._extract_product(element)
                    if product:
                        products.append(product)
                except:
                    continue

            print(f"⚡ {self.platform_name}: {len(products)} products in TURBO mode")
            return products

        except Exception as e:
            print(f"❌ {self.platform_name}: Error - {e}")
            return []

    def _extract_product(self, element):
        """Extract product from Snapdeal element"""

        # Title
        title = "N/A"
        try:
            title_elem = element.find_element(By.CSS_SELECTOR, ".product-title")
            title = title_elem.text.strip()
        except:
            return None

        # Price
        price = "N/A"
        price_numeric = None
        try:
            price_elem = element.find_element(By.CSS_SELECTOR, ".product-price")
            price = price_elem.text.strip()
            price_numeric = self.extract_numeric_price(price)
        except:
            pass

        # URL
        url = "#"
        try:
            url_elem = element.find_element(By.CSS_SELECTOR, "a")
            href = url_elem.get_attribute("href")
            url = href if href.startswith("http") else f"{self.base_url}{href}"
        except:
            pass

        # Image
        image_url = ""
        try:
            img_elem = element.find_element(By.CSS_SELECTOR, "img")
            image_url = img_elem.get_attribute("src")
        except:
            pass

        # Rating
        rating = "N/A"
        try:
            rating_elem = element.find_element(By.CSS_SELECTOR, ".filled-stars")
            rating = rating_elem.get_attribute("style")
            # Extract percentage and convert to rating
        except:
            pass

        if price == "N/A":
            return None

        return {
            'title': title,
            'price': price,
            'price_numeric': price_numeric,
            'rating': rating,
            'url': url,
            'platform': self.platform_name,
            'image': image_url,
            'availability': 'Available',
            'discount': None
        }
