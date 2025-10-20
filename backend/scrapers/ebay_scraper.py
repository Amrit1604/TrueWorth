"""
eBay India scraper
"""
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re


class EbayScraper(BaseScraper):
    """eBay India scraper"""

    def __init__(self):
        super().__init__("eBay", "https://www.ebay.in")

    def search(self, query, max_results=10):
        """Search eBay India for products"""
        if not self.driver:
            self.setup_driver()

        if not self.driver:
            return []

        try:
            self.safe_wait(2, 4)

            search_url = f"{self.base_url}/sch/i.html?_nkw={query.replace(' ', '+')}"
            print(f"🔍 {self.platform_name}: Searching {search_url}")

            self.driver.get(search_url)

            # Wait for results
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".s-item"))
                )
            except TimeoutException:
                print(f"⚠️ {self.platform_name}: Timeout")
                return []

            products = []
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, ".s-item")

            for element in product_elements[1:max_results+1]:  # Skip first (it's usually a header)
                try:
                    product = self._extract_product(element)
                    if product:
                        products.append(product)
                except:
                    continue

            print(f"✅ {self.platform_name}: Found {len(products)} products")
            return products

        except Exception as e:
            print(f"❌ {self.platform_name}: Error - {e}")
            return []

    def _extract_product(self, element):
        """Extract product from eBay element"""

        # Title
        title = "N/A"
        try:
            title_elem = element.find_element(By.CSS_SELECTOR, ".s-item__title")
            title = title_elem.text.strip()
        except:
            return None

        # Price
        price = "N/A"
        price_numeric = None
        try:
            price_elem = element.find_element(By.CSS_SELECTOR, ".s-item__price")
            price = price_elem.text.strip()
            price_numeric = self.extract_numeric_price(price)
        except:
            pass

        # URL
        url = "#"
        try:
            url_elem = element.find_element(By.CSS_SELECTOR, ".s-item__link")
            url = url_elem.get_attribute("href")
        except:
            pass

        # Image
        image_url = ""
        try:
            img_elem = element.find_element(By.CSS_SELECTOR, ".s-item__image-img")
            image_url = img_elem.get_attribute("src")
        except:
            pass

        # Rating
        rating = "N/A"

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
