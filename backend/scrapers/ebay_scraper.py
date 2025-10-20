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
        """Search eBay India for products - TURBO MODE"""
        if not self.driver:
            self.setup_driver()

        if not self.driver:
            return []

        try:
            self.safe_wait(0.5, 1)  # ⚡ Reduced delay

            search_url = f"{self.base_url}/sch/i.html?_nkw={query.replace(' ', '+')}"
            print(f"⚡ {self.platform_name}: TURBO searching...")

            self.driver.get(search_url)

            # FASTER wait
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".s-item"))
                )
            except TimeoutException:
                print(f"⚠️ {self.platform_name}: Timeout")
                return []

            products = []
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, ".s-item")

            # ⚡ Max 5 for speed
            for element in product_elements[1:min(max_results, 5)+1]:
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
