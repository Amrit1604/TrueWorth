"""
🔥 PROFESSIONAL PRICE COMPARISON API - GOD MODE 🔥
Real scraping with Playwright - No BS, No demos!
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import json
import re
import random
from datetime import datetime, timedelta
import threading
app = Flask(__name__)
CORS(app)


def parse_price(raw_price: str) -> float:
    """Convert price strings like '₹54,999.00' to a numeric value."""
    if not raw_price:
        return float('inf')

    cleaned = re.sub(r'[^0-9.]', '', raw_price)
    if not cleaned:
        return float('inf')

    try:
        return float(cleaned)
    except ValueError:
        return float('inf')


def format_price(value: float) -> str:
    """Format numeric price back to a Rupee string."""
    if value == float('inf'):
        return 'N/A'

    if value >= 100:
        return f"₹{value:,.0f}"

    return f"₹{value:,.2f}"


def normalize_rating(raw_rating: str) -> str:
    """Standardise rating strings to '4.5/5' format."""
    if not raw_rating or raw_rating in {'N/A', '—'}:
        return '—'

    match = re.search(r'(\d+(?:\.\d+)?)', raw_rating)
    if not match:
        return raw_rating.strip()

    value = match.group(1)
    return f"{value}/5"


def build_summary(products):
    """Create comparison metadata and grouped platform buckets."""
    if not products:
        return {
            'bestDeal': None,
            'platforms': [],
            'priceRange': None
        }, []

    by_platform = {}
    for product in products:
        platform = product.get('platform', 'Marketplace')
        by_platform.setdefault(platform, []).append(product)

    # Ensure each platform list is sorted by price
    for platform_products in by_platform.values():
        platform_products.sort(key=lambda item: item['priceValue'])

    best_deal = min(products, key=lambda item: item['priceValue'])
    all_prices = [item['priceValue'] for item in products]

    platform_cards = []
    for platform, platform_products in by_platform.items():
        price_values = [item['priceValue'] for item in platform_products]
        cheapest_product = platform_products[0]
        average_price = sum(price_values) / len(price_values)
        price_min = min(price_values)
        price_max = max(price_values)
        difference_value = max(0.0, round(cheapest_product['priceValue'] - best_deal['priceValue'], 2))

        platform_cards.append({
            'platform': platform,
            'count': len(platform_products),
            'cheapest': cheapest_product,
            'averagePrice': format_price(average_price),
            'priceRange': {
                'min': format_price(price_min),
                'max': format_price(price_max)
            },
            'differenceValue': difference_value,
            'differenceLabel': 'Best price' if difference_value < 1 else format_price(difference_value)
        })

    platform_cards.sort(key=lambda card: card['cheapest']['priceValue'])

    platform_buckets = [
        {
            'platform': platform,
            'products': items
        }
        for platform, items in by_platform.items()
    ]
    platform_buckets.sort(key=lambda bucket: bucket['products'][0]['priceValue'])

    comparison = {
        'bestDeal': best_deal,
        'platforms': platform_cards,
        'priceRange': {
            'min': format_price(min(all_prices)),
            'max': format_price(max(all_prices))
        }
    }

    return comparison, platform_buckets

class RateLimiter:
    """Rate limiter to prevent IP bans"""
    def __init__(self):
        self.requests = {}
        self.lock = threading.Lock()

    def is_allowed(self, identifier, max_requests=3, time_window=60):
        with self.lock:
            current_time = datetime.now()

            if identifier not in self.requests:
                self.requests[identifier] = []

            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if current_time - req_time < timedelta(seconds=time_window)
            ]

            if len(self.requests[identifier]) >= max_requests:
                return False

            self.requests[identifier].append(current_time)
            return True

class ProScraper:
    """Professional scraper using Playwright"""

    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.last_request = {}
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        print("✅ Professional Scraper initialized with Playwright")

    def safe_wait(self, site_name, min_delay=3, max_delay=6):
        """Respectful delays between requests"""
        current_time = time.time()

        if site_name in self.last_request:
            elapsed = current_time - self.last_request[site_name]
            if elapsed < min_delay:
                sleep_time = random.uniform(min_delay, max_delay)
                print(f"⏳ Waiting {sleep_time:.1f}s before {site_name} request")
                time.sleep(sleep_time)

        self.last_request[site_name] = time.time()

    def scrape_amazon(self, query):
        """Scrape Amazon with Playwright - REAL DATA"""
        if not self.rate_limiter.is_allowed('amazon'):
            print("⚠️ Rate limit for Amazon - skipping")
            return []

        self.safe_wait('amazon', 3, 6)

        try:
            print(f"🔍 Scraping Amazon for: {query}")

            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                context = browser.new_context(
                    user_agent=random.choice(self.user_agents),
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-IN'
                )
                context.set_default_navigation_timeout(45000)

                page = context.new_page()
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => false });
                    Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                    Object.defineProperty(navigator, 'language', { get: () => 'en-US' });
                    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                """)
                page.set_extra_http_headers({
                    "Accept-Language": "en-IN,en;q=0.9",
                    "Upgrade-Insecure-Requests": "1"
                })

                url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
                try:
                    page.goto(url, wait_until='domcontentloaded')
                    page.wait_for_load_state('networkidle', timeout=15000)
                except PlaywrightTimeout:
                    print("  ⚠️ Amazon navigation hit timeout, trying lighter wait")
                    page.wait_for_load_state('domcontentloaded', timeout=10000)

                time.sleep(1.5)

                # Extract products using multiple selector strategies
                products = []

                # Try to get all product containers
                page.wait_for_selector('div[data-component-type="s-search-result"], div.s-result-item[data-asin]', timeout=10000)
                items = page.query_selector_all('div.s-result-item[data-asin]:not([data-asin=""])')

                print(f"📦 Found {len(items)} items on page")

                for item in items[:8]:  # Top 8 results
                    try:
                        # Title - multiple selectors
                        title = None
                        for selector in ['h2 span', 'h2 a span', '.a-text-normal']:
                            title_elem = item.query_selector(selector)
                            if title_elem:
                                title = title_elem.inner_text().strip()
                                if title:
                                    break

                        # Price - multiple selectors
                        price = None
                        for selector in ['.a-price-whole', '.a-price .a-offscreen']:
                            price_elem = item.query_selector(selector)
                            if price_elem:
                                price_text = price_elem.inner_text() if 'offscreen' not in selector else price_elem.text_content()
                                if price_text and '₹' in price_text:
                                    price = price_text.strip()
                                    break

                        price_value = parse_price(price)
                        if price_value == float('inf'):
                            continue
                        formatted_price = format_price(price_value)

                        # Rating
                        rating = "—"
                        rating_elem = item.query_selector('.a-icon-star-small span, .a-icon-alt')
                        if rating_elem:
                            rating_text = rating_elem.get_attribute('textContent') or rating_elem.inner_text()
                            rating = normalize_rating(rating_text)

                        # URL
                        product_url = "#"
                        url_elem = item.query_selector('h2 a, .a-link-normal')
                        if url_elem:
                            href = url_elem.get_attribute('href')
                            if href:
                                product_url = f"https://www.amazon.in{href}" if not href.startswith('http') else href

                        # Image
                        image = ""
                        img_elem = item.query_selector('img.s-image, img')
                        if img_elem:
                            image = img_elem.get_attribute('src') or ""

                        if title and len(title) > 5:
                            products.append({
                                'title': title[:100],  # Limit title length
                                'price': formatted_price,
                                'priceValue': price_value,
                                'rating': rating,
                                'url': product_url,
                                'platform': 'Amazon',
                                'image': image
                            })
                            print(f"  ✓ Added: {title[:50]}...")
                    except Exception as e:
                        print(f"  ⚠️ Item parse error: {e}")
                        continue

                browser.close()
                print(f"✅ Amazon: Successfully extracted {len(products)} products")
                return products

        except Exception as e:
            print(f"❌ Amazon error: {e}")
            return []

    def scrape_flipkart(self, query):
        """Scrape Flipkart with Playwright - REAL DATA"""
        if not self.rate_limiter.is_allowed('flipkart'):
            print("⚠️ Rate limit for Flipkart - skipping")
            return []

        self.safe_wait('flipkart', 4, 7)

        try:
            print(f"🔍 Scraping Flipkart for: {query}")

            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                context = browser.new_context(
                    user_agent=random.choice(self.user_agents),
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-IN'
                )
                context.set_default_navigation_timeout(45000)

                page = context.new_page()
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => false });
                    Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                """)

                url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
                try:
                    page.goto(url, wait_until='domcontentloaded')
                    page.wait_for_load_state('networkidle', timeout=15000)
                except PlaywrightTimeout:
                    print("  ⚠️ Flipkart navigation hit timeout, falling back to domcontentloaded")
                    page.wait_for_load_state('domcontentloaded', timeout=10000)

                time.sleep(2)

                products = []

                # Flipkart now renders product cards with data-id attribute
                try:
                    page.wait_for_selector('div[data-id]', timeout=10000)
                    items = page.query_selector_all('div[data-id]')
                except PlaywrightTimeout:
                    print("  ⚠️ Could not find data-id containers, trying legacy classes")
                    items = page.query_selector_all('div[class*="_1AtVbE"], div[class*="_13oc-S"], div[class*="_2kHMtA"]')

                print(f"📦 Found {len(items)} potential items on page")

                for item in items[:8]:
                    try:
                        # Title - try multiple selectors
                        title = None
                        for selector in ['._4rR01T', '.s1Q9rs', '._3pLy-c', 'a[class*="IRpwTa"]', 'div[class*="KzDlHZ"]']:
                            title_elem = item.query_selector(selector)
                            if title_elem:
                                title = title_elem.inner_text().strip()
                                if title and len(title) > 5:
                                    break

                        # Price - try multiple selectors
                        price = None
                        for selector in ['._30jeq3', '._1_WHN1', '.Nx9bqj', 'div[class*="Nx9bqj"]', 'div[class*="_30jeq3"]']:
                            price_elem = item.query_selector(selector)
                            if price_elem:
                                price = price_elem.inner_text().strip()
                                if price and '₹' in price:
                                    break

                        price_value = parse_price(price)
                        if price_value == float('inf'):
                            continue
                        formatted_price = format_price(price_value)

                        # Rating
                        rating = "—"
                        for selector in ['._3LWZlK', 'div[class*="_3LWZlK"]', '.XQDdHH']:
                            rating_elem = item.query_selector(selector)
                            if rating_elem:
                                rating = normalize_rating(rating_elem.inner_text())
                                if rating:
                                    break

                        # URL
                        product_url = "#"
                        url_elem = item.query_selector('a')
                        if url_elem:
                            href = url_elem.get_attribute('href')
                            if href:
                                product_url = f"https://www.flipkart.com{href}" if not href.startswith('http') else href

                        # Image
                        image = ""
                        img_elem = item.query_selector('img')
                        if img_elem:
                            image = img_elem.get_attribute('src') or ""

                        if title and len(title) > 5:
                            products.append({
                                'title': title[:100],
                                'price': formatted_price,
                                'priceValue': price_value,
                                'rating': rating,
                                'url': product_url,
                                'platform': 'Flipkart',
                                'image': image
                            })
                            print(f"  ✓ Added: {title[:50]}...")
                    except Exception as e:
                        print(f"  ⚠️ Item parse error: {e}")
                        continue

                browser.close()
                print(f"✅ Flipkart: Successfully extracted {len(products)} products")
                return products

        except Exception as e:
            print(f"❌ Flipkart error: {e}")
            return []

# Global scraper
scraper = ProScraper()

@app.route('/api/search', methods=['POST'])
def search_products():
    """🔥 REAL SEARCH - NO DEMO BS"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        if len(query) < 2 or len(query) > 100:
            return jsonify({'error': 'Query must be 2-100 characters'}), 400

        print(f"\n{'='*60}")
        print(f"🔥 PROFESSIONAL SEARCH: {query}")
        print(f"{'='*60}\n")

        all_products = []

        # Scrape Amazon
        try:
            amazon_products = scraper.scrape_amazon(query)
            all_products.extend(amazon_products)
        except Exception as e:
            print(f"Amazon failed: {e}")

        # Small delay between sites
        time.sleep(random.uniform(2, 4))

        # Scrape Flipkart
        try:
            flipkart_products = scraper.scrape_flipkart(query)
            all_products.extend(flipkart_products)
        except Exception as e:
            print(f"Flipkart failed: {e}")

        all_products = [product for product in all_products if product.get('priceValue') is not None]
        all_products.sort(key=lambda x: x['priceValue'])

        comparison, platform_buckets = build_summary(all_products)

        print(f"\n✅ TOTAL: {len(all_products)} products found\n")

        return jsonify({
            'success': True,
            'products': all_products,
            'total': len(all_products),
            'query': query,
            'comparison': comparison,
            'platformBuckets': platform_buckets,
            'mode': 'PROFESSIONAL - REAL SCRAPING',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': 'Search failed. Please try again.'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'PROFESSIONAL',
        'mode': 'REAL SCRAPING WITH PLAYWRIGHT',
        'features': [
            '✅ Real-time scraping',
            '✅ Rate limiting',
            '✅ Respectful delays',
            '✅ User agent rotation',
            '✅ Error handling'
        ]
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': '🔥 PROFESSIONAL Price Comparison API',
        'status': 'LIVE - REAL SCRAPING',
        'version': '2.0 PRO',
        'endpoints': {
            'search': '/api/search (POST)',
            'health': '/api/health (GET)'
        }
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔥" * 35)
    print("  PROFESSIONAL PRICE COMPARISON API - GOD MODE ACTIVATED  ")
    print("🔥" * 35)
    print("="*70)
    print("\n✅ Real scraping with Playwright")
    print("✅ Safety features active")
    print("✅ Rate limiting enabled")
    print("✅ Ready to destroy the competition!\n")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
