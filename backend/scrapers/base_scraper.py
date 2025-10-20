"""
Base scraper class for all e-commerce platforms
Provides common functionality and interface for platform-specific scrapers
"""
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from datetime import datetime, timedelta
import threading


class BaseScraper(ABC):
    """Abstract base class for all platform scrapers"""

    def __init__(self, platform_name, base_url):
        self.platform_name = platform_name
        self.base_url = base_url
        self.driver = None
        self.last_request_time = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]

    def setup_driver(self):
        """Setup Chrome driver with TURBO performance options"""
        if self.driver:
            return

        chrome_options = Options()

        # SPEED OPTIMIZATIONS - JARVIS TURBO MODE
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-images")  # ⚡ Don't load images
        # JS ENABLED - Sites need it to load products
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # ⚡ Block images
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--log-level=3")

        # Performance boost
        chrome_options.add_argument("--window-size=800,600")  # Smaller = faster
        chrome_options.page_load_strategy = 'normal'  # ⚡ Let sites load properly

        # Random user agent
        user_agent = random.choice(self.user_agents)
        chrome_options.add_argument(f"--user-agent={user_agent}")

        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Disable images via prefs
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.cookies": 2,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # BALANCED TIMEOUTS FOR SPEED + RELIABILITY
            self.driver.set_page_load_timeout(15)  # ⚡ 15s max (balanced)
            self.driver.implicitly_wait(5)  # ⚡ 5s max (balanced)

            print(f"⚡ {self.platform_name}: TURBO driver initialized")

        except Exception as e:
            print(f"❌ {self.platform_name}: Driver setup failed - {e}")
            self.driver = None

    def safe_wait(self, min_delay=0.5, max_delay=1.5):
        """TURBO MODE: Minimal delays for speed"""
        current_time = time.time()

        if self.last_request_time:
            time_since_last = current_time - self.last_request_time
            if time_since_last < min_delay:
                sleep_time = random.uniform(min_delay, max_delay)
                time.sleep(sleep_time)

        self.last_request_time = time.time()

    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except:
                pass

    def extract_numeric_price(self, price_str):
        """Extract numeric price from string"""
        import re
        if not price_str or price_str == "N/A":
            return None

        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.]', '', price_str)
        try:
            return float(cleaned)
        except:
            return None

    def normalize_price(self, price_str, currency='₹'):
        """Normalize price string to standard format"""
        numeric = self.extract_numeric_price(price_str)
        if numeric:
            return f"{currency}{numeric:,.2f}"
        return "N/A"

    @abstractmethod
    def search(self, query, max_results=5):
        """
        Search for products on the platform
        Must be implemented by each platform scraper

        Returns:
            list: List of product dictionaries with keys:
                - title: Product name
                - price: Price string
                - price_numeric: Float price for sorting
                - rating: Rating string
                - url: Product URL
                - platform: Platform name
                - image: Image URL
                - availability: In stock status
                - discount: Discount percentage if available
        """
        pass

    def get_metadata(self):
        """Get scraper metadata"""
        return {
            'platform': self.platform_name,
            'base_url': self.base_url,
            'status': 'active' if self.driver else 'inactive'
        }
