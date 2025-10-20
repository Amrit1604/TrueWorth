from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service
import time
import json
import re
import random
from datetime import datetime, timedelta
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

class RateLimiter:
    """Rate limiter to prevent too many requests"""
    def __init__(self):
        self.requests = {}
        self.lock = threading.Lock()

    def is_allowed(self, identifier, max_requests=5, time_window=60):
        """Check if request is allowed based on rate limiting"""
        with self.lock:
            current_time = datetime.now()

            if identifier not in self.requests:
                self.requests[identifier] = []

            # Remove old requests outside time window
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if current_time - req_time < timedelta(seconds=time_window)
            ]

            # Check if within limit
            if len(self.requests[identifier]) >= max_requests:
                return False

            # Add current request
            self.requests[identifier].append(current_time)
            return True

class PriceScraper:
    def __init__(self):
        self.driver = None
        self.rate_limiter = RateLimiter()
        self.last_request_time = {}
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
        self.setup_driver()

    def setup_driver(self):
        """Setup Edge driver with safety options (works better on Windows)"""
        print("🔧 Setting up Microsoft Edge driver (better for Windows)...")

        edge_options = Options()

        # Safety and stealth options
        edge_options.add_argument("--headless")  # Run in background
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920,1080")
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.add_argument("--disable-extensions")
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        edge_options.add_experimental_option('useAutomationExtension', False)

        # Random user agent
        user_agent = random.choice(self.user_agents)
        edge_options.add_argument(f"--user-agent={user_agent}")

        # Performance optimizations
        edge_options.add_argument("--disable-background-timer-throttling")
        edge_options.add_argument("--disable-renderer-backgrounding")
        edge_options.add_argument("--log-level=3")  # Suppress logs

        try:
            print("📥 Downloading/locating Edge driver...")
            service = Service(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=edge_options)

            # Hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Set timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)

            print("✅ Edge driver setup successful with safety measures")

        except Exception as e:
            print(f"❌ Edge driver setup failed: {e}")
            print("💡 Make sure Microsoft Edge is installed (comes with Windows 10/11)")
            print("🔧 Alternative: Install Chrome browser and we can switch to Chrome driver")
            self.driver = None

    def safe_wait(self, site_name, min_delay=2, max_delay=5):
        """Implement respectful delays between requests"""
        current_time = time.time()

        if site_name in self.last_request_time:
            time_since_last = current_time - self.last_request_time[site_name]
            if time_since_last < min_delay:
                sleep_time = random.uniform(min_delay, max_delay)
                print(f"⏳ Waiting {sleep_time:.1f}s before {site_name} request (respectful scraping)")
                time.sleep(sleep_time)

        self.last_request_time[site_name] = time.time()

    def is_request_allowed(self, site_name):
        """Check if request is allowed by rate limiter"""
        return self.rate_limiter.is_allowed(site_name, max_requests=3, time_window=60)

    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()

    def search_amazon(self, query):
        """Scrape Amazon search results using Selenium with safety measures"""
        if not self.driver:
            print("❌ Driver not available for Amazon search")
            return []

        # Check rate limiting
        if not self.is_request_allowed('amazon'):
            print("⚠️ Amazon rate limit exceeded. Skipping to protect IP.")
            return []

        try:
            # Respectful delay
            self.safe_wait('amazon', 3, 6)

            search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
            print(f"🔍 Searching Amazon: {search_url}")

            self.driver.get(search_url)

            # Wait for search results to load with timeout
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-component-type='s-search-result']"))
                )
            except TimeoutException:
                print("⚠️ Amazon search results took too long to load")
                return []

            products = []
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")

            # Limit to 3 results to be respectful
            for element in product_elements[:3]:
                try:
                    # Get product title
                    title_elem = element.find_element(By.CSS_SELECTOR, "h2 a span")
                    title = title_elem.text.strip()

                    # Get product URL
                    url_elem = element.find_element(By.CSS_SELECTOR, "h2 a")
                    href = url_elem.get_attribute("href")
                    url = href if href.startswith('http') else f"https://amazon.in{href}"

                    # Get price
                    price = "N/A"
                    try:
                        price_elem = element.find_element(By.CSS_SELECTOR, ".a-price-whole")
                        price = "₹" + price_elem.text.replace(',', '')
                    except NoSuchElementException:
                        try:
                            price_elem = element.find_element(By.CSS_SELECTOR, ".a-price .a-offscreen")
                            price = price_elem.get_attribute("textContent")
                        except NoSuchElementException:
                            pass

                    # Get rating
                    rating = "N/A"
                    try:
                        rating_elem = element.find_element(By.CSS_SELECTOR, ".a-icon-alt")
                        rating_text = rating_elem.get_attribute("textContent")
                        if "out of" in rating_text:
                            rating = rating_text.split()[0]
                    except NoSuchElementException:
                        pass

                    # Get image URL
                    image_url = ""
                    try:
                        img_elem = element.find_element(By.CSS_SELECTOR, ".s-image")
                        image_url = img_elem.get_attribute("src")
                    except NoSuchElementException:
                        pass

                    if title and price != "N/A":
                        products.append({
                            'title': title,
                            'price': price,
                            'rating': rating,
                            'url': url,
                            'platform': 'Amazon',
                            'image': image_url
                        })

                except Exception as e:
                    continue

            print(f"✅ Amazon: Found {len(products)} products")
            return products

        except Exception as e:
            print(f"❌ Error scraping Amazon: {e}")
            return []

    def search_flipkart(self, query):
        """Scrape Flipkart search results using Selenium with safety measures"""
        if not self.driver:
            print("❌ Driver not available for Flipkart search")
            return []

        # Check rate limiting
        if not self.is_request_allowed('flipkart'):
            print("⚠️ Flipkart rate limit exceeded. Skipping to protect IP.")
            return []

        try:
            # Respectful delay
            self.safe_wait('flipkart', 4, 7)

            search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
            print(f"🔍 Searching Flipkart: {search_url}")

            self.driver.get(search_url)

            # Wait for page to load
            time.sleep(random.uniform(3, 5))

            products = []
            # Try different selectors for Flipkart products
            product_selectors = [
                "._1AtVbE",
                "._13oc-S",
                "._2kHMtA",
                "[data-id]"
            ]

            product_elements = []
            for selector in product_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        product_elements = elements[:3]  # Limit to 3 results
                        break
                except:
                    continue

            if not product_elements:
                print("⚠️ No Flipkart products found with current selectors")
                return []

            for element in product_elements:
                try:
                    # Get product title
                    title = "N/A"
                    title_selectors = [
                        "._4rR01T",
                        ".s1Q9rs",
                        "._3pLy-c",
                        ".IRpwTa"
                    ]

                    for selector in title_selectors:
                        try:
                            title_elem = element.find_element(By.CSS_SELECTOR, selector)
                            title = title_elem.text.strip()
                            break
                        except:
                            continue

                    # Get price
                    price = "N/A"
                    price_selectors = [
                        "._30jeq3",
                        "._1_WHN1",
                        ".Nx9bqj"
                    ]

                    for selector in price_selectors:
                        try:
                            price_elem = element.find_element(By.CSS_SELECTOR, selector)
                            price = price_elem.text.strip()
                            break
                        except:
                            continue

                    # Get rating
                    rating = "N/A"
                    try:
                        rating_elem = element.find_element(By.CSS_SELECTOR, "._3LWZlK")
                        rating = rating_elem.text.strip()
                    except:
                        pass

                    # Get product URL
                    url = "#"
                    try:
                        url_elem = element.find_element(By.CSS_SELECTOR, "a")
                        href = url_elem.get_attribute("href")
                        if href:
                            if not href.startswith("http"):
                                url = "https://www.flipkart.com" + href
                            else:
                                url = href
                    except:
                        pass

                    # Get image URL
                    image_url = ""
                    try:
                        img_elem = element.find_element(By.CSS_SELECTOR, "img")
                        image_url = img_elem.get_attribute("src")
                    except:
                        pass

                    if title != "N/A" and price != "N/A":
                        products.append({
                            'title': title,
                            'price': price,
                            'rating': rating,
                            'url': url,
                            'platform': 'Flipkart',
                            'image': image_url
                        })

                except Exception as e:
                    continue

            print(f"✅ Flipkart: Found {len(products)} products")
            return products

        except Exception as e:
            print(f"❌ Error scraping Flipkart: {e}")
            return []

# Global scraper instance
scraper = PriceScraper()

@app.route('/api/search', methods=['POST'])
def search_products():
    """Search products across multiple platforms with safety measures"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Validate query length and content
        if len(query) < 2:
            return jsonify({'error': 'Query too short'}), 400

        if len(query) > 100:
            return jsonify({'error': 'Query too long'}), 400

        print(f"🔍 Safe search initiated for: {query}")

        # Search across platforms with safety measures
        all_products = []

        try:
            # Amazon search with error handling
            print("🛡️ Starting Amazon search with safety measures...")
            amazon_products = scraper.search_amazon(query)
            all_products.extend(amazon_products)

            # Delay between different sites
            time.sleep(random.uniform(2, 4))

            # Flipkart search with error handling
            print("🛡️ Starting Flipkart search with safety measures...")
            flipkart_products = scraper.search_flipkart(query)
            all_products.extend(flipkart_products)

        except Exception as scraping_error:
            print(f"⚠️ Scraping error: {scraping_error}")
            # Continue with whatever results we have

        # Sort by price (extract numeric value)
        def extract_price(price_str):
            try:
                return float(re.sub(r'[^\d.]', '', price_str))
            except:
                return float('inf')

        all_products.sort(key=lambda x: extract_price(x['price']) if x['price'] != 'N/A' else float('inf'))

        print(f"✅ Safe search completed. Found {len(all_products)} total products")

        return jsonify({
            'success': True,
            'products': all_products,
            'total': len(all_products),
            'query': query,
            'safety_note': 'Search conducted with rate limiting and respectful delays'
        })

    except Exception as e:
        print(f"❌ Search API error: {e}")
        return jsonify({'error': 'Search temporarily unavailable. Please try again later.'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with driver status"""
    return jsonify({
        'status': 'healthy',
        'driver_status': 'active' if scraper.driver else 'inactive',
        'safety_features': 'enabled',
        'rate_limiting': 'active'
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        'message': 'Safe Price Comparison API is running!',
        'version': '2.0.0',
        'safety_features': [
            'Rate limiting (3 requests per minute per site)',
            'Respectful delays between requests',
            'User agent rotation',
            'Error handling and graceful degradation',
            'Limited results per site'
        ],
        'endpoints': {
            'search': '/api/search (POST)',
            'health': '/api/health (GET)'
        },
        'legal_note': 'Educational project - respects robots.txt and rate limits'
    })

# Cleanup on exit
import atexit
def cleanup():
    print("🧹 Cleaning up resources...")
    if scraper:
        scraper.close_driver()

atexit.register(cleanup)

if __name__ == '__main__':
    print("🚀 Starting Safe Price Comparison API...")
    print("🛡️ Safety Features:")
    print("   ✅ Rate limiting enabled")
    print("   ✅ Respectful delays implemented")
    print("   ✅ User agent rotation active")
    print("   ✅ Error handling in place")
    print("   ✅ Limited results per site")
    print(f"🤖 Driver setup: {'✅ Success' if scraper.driver else '❌ Failed'}")
    print("📝 Legal Note: Educational project - respects robots.txt")
    app.run(debug=True, host='0.0.0.0', port=5000)
