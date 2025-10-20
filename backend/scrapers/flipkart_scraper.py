"""
Flipkart scraper with advanced product extraction
"""
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re


class FlipkartScraper(BaseScraper):
    """Flipkart scraper"""

    def __init__(self):
        super().__init__("Flipkart", "https://www.flipkart.com")

    def search(self, query, max_results=10):
        """Search Flipkart for products - TURBO MODE"""
        if not self.driver:
            self.setup_driver()

        if not self.driver:
            return []

        try:
            self.safe_wait(0.5, 1)  # ⚡ Reduced delay

            search_url = f"{self.base_url}/search?q={query.replace(' ', '%20')}"
            print(f"⚡ {self.platform_name}: TURBO searching...")

            self.driver.get(search_url)

            # FASTER wait
            time.sleep(2)  # ⚡ Reduced from 3-5s

            products = []

            # Try multiple selectors for Flipkart products
            product_selectors = [
                "[data-id]",
                "._1AtVbE",
                "._13oc-S",
                "._2kHMtA",
                ".cPHDOP"
            ]

            product_elements = []
            for selector in product_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 3:
                        product_elements = elements[:min(max_results, 5)]  # ⚡ Max 5
                        break
                except:
                    continue

            if not product_elements:
                print(f"⚠️ {self.platform_name}: No products")
                return []

            for element in product_elements:
                try:
                    product = self._extract_product(element)
                    if product:
                        products.append(product)
                except Exception as e:
                    continue

            print(f"⚡ {self.platform_name}: {len(products)} products in TURBO mode")
            return products

        except Exception as e:
            print(f"❌ {self.platform_name}: Error - {e}")
            return []

    def _extract_product(self, element):
        """Extract product data from Flipkart result element"""

        # Title
        title = "N/A"
        title_selectors = [
            ".KzDlHZ",
            ".s1Q9rs",
            "._4rR01T",
            ".IRpwTa",
            "._3pLy-c"
        ]

        for selector in title_selectors:
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, selector)
                title = title_elem.text.strip()
                if title:
                    break
            except:
                continue

        if title == "N/A":
            return None

        # Price
        price = "N/A"
        price_numeric = None
        price_selectors = [
            ".Nx9bqj",
            "._30jeq3",
            "._1_WHN1",
            ".hl05eU"
        ]

        for selector in price_selectors:
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, selector)
                price = price_elem.text.strip()
                if price:
                    price_numeric = self.extract_numeric_price(price)
                    break
            except:
                continue

        # Rating
        rating = "N/A"
        rating_selectors = [
            ".XQDdHH",
            "._3LWZlK",
            ".hGSR34"
        ]

        for selector in rating_selectors:
            try:
                rating_elem = element.find_element(By.CSS_SELECTOR, selector)
                rating_text = rating_elem.text.strip()
                if rating_text:
                    rating = rating_text + "⭐"
                    break
            except:
                continue

        # URL
        url = "#"
        try:
            url_elem = element.find_element(By.CSS_SELECTOR, "a")
            href = url_elem.get_attribute("href")
            if href:
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

        # Availability (Flipkart usually shows only in-stock items)
        availability = "In Stock"

        # Discount
        discount = None
        try:
            discount_elem = element.find_element(By.CSS_SELECTOR, ".UkUFwK")
            discount_text = discount_elem.text.strip()
            discount_match = re.search(r'(\d+)%', discount_text)
            if discount_match:
                discount = int(discount_match.group(1))
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
            'availability': availability,
            'discount': discount
        }
