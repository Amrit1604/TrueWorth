"""
JARVIS PRICE INTELLIGENCE PLATFORM
Production-grade price comparison API with advanced features

Features:
- Multi-platform concurrent scraping (Amazon, Flipkart, eBay, Snapdeal)
- Smart product matching and normalization
- Advanced price analytics and comparison
- Intelligent caching system
- Comprehensive filtering and sorting
- Real-time performance monitoring
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import atexit
import time
from datetime import datetime

# Import scrapers
from scrapers.amazon_scraper import AmazonScraper
from scrapers.flipkart_scraper import FlipkartScraper
from scrapers.ebay_scraper import EbayScraper
from scrapers.snapdeal_scraper import SnapdealScraper

# Import utilities
from utils.scraper_manager import ScraperManager
from utils.product_matcher import ProductMatcher, PriceNormalizer
from analytics.price_analytics import PriceAnalytics

app = Flask(__name__)
CORS(app)

# Initialize components
scraper_manager = ScraperManager()
product_matcher = ProductMatcher()
price_normalizer = PriceNormalizer()
analytics_engine = PriceAnalytics()

# Register scrapers
print("🚀 JARVIS INITIALIZING - Price Intelligence Platform")
print("=" * 60)

try:
    scraper_manager.register_scraper("Amazon", AmazonScraper())
    scraper_manager.register_scraper("Flipkart", FlipkartScraper())
    scraper_manager.register_scraper("eBay", EbayScraper())
    scraper_manager.register_scraper("Snapdeal", SnapdealScraper())
except Exception as e:
    print(f"⚠️ Warning during scraper registration: {e}")

print("=" * 60)
print(f"✅ Platform ready with {len(scraper_manager.get_available_platforms())} scrapers")


@app.route('/', methods=['GET'])
def home():
    """API documentation and welcome"""
    return jsonify({
        'name': 'JARVIS Price Intelligence Platform',
        'version': '2.0.0',
        'status': 'online',
        'tagline': 'Tony Stark-approved price comparison engine',
        'features': [
            'Multi-platform concurrent scraping',
            'Smart product matching with fuzzy logic',
            'Advanced price analytics',
            'Intelligent caching (10min TTL)',
            'Real-time comparison across 4+ platforms',
            'Comprehensive filtering and sorting',
            'Price history tracking (coming soon)',
            'Price drop alerts (coming soon)'
        ],
        'platforms': scraper_manager.get_available_platforms(),
        'endpoints': {
            '/': 'API documentation',
            '/api/search': 'Search products across platforms (POST)',
            '/api/health': 'System health check (GET)',
            '/api/platforms': 'List available platforms (GET)',
            '/api/stats': 'Platform statistics (GET)',
            '/api/cache/clear': 'Clear cache (POST)',
            '/api/compare': 'Advanced product comparison (POST)'
        },
        'safety_features': [
            'Rate limiting per platform',
            'Respectful delays between requests',
            'User agent rotation',
            'Graceful error handling',
            'Resource cleanup on exit'
        ]
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Comprehensive health check"""
    stats = scraper_manager.get_stats()

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'active',
        'scrapers': {
            'registered': stats['registered_platforms'],
            'platforms': stats['platforms']
        },
        'cache': {
            'entries': stats['cache_entries'],
            'ttl_seconds': stats['cache_ttl_seconds']
        },
        'performance': {
            'max_concurrent_workers': stats['max_workers']
        }
    })


@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """Get available platforms"""
    platforms = scraper_manager.get_available_platforms()

    return jsonify({
        'success': True,
        'platforms': platforms,
        'count': len(platforms)
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get detailed statistics"""
    return jsonify({
        'success': True,
        'stats': scraper_manager.get_stats()
    })


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all cached results"""
    scraper_manager.clear_cache()
    return jsonify({
        'success': True,
        'message': 'Cache cleared successfully'
    })


@app.route('/api/search', methods=['POST'])
def search_products():
    """
    Advanced product search across multiple platforms

    Request body:
    {
        "query": "macbook air m2",
        "platforms": ["Amazon", "Flipkart"],  // Optional, defaults to all
        "max_results": 10,  // Optional, default 10 per platform
        "use_cache": true,  // Optional, default true
        "filters": {  // Optional
            "min_price": 50000,
            "max_price": 150000,
            "min_rating": 4.0,
            "platforms": ["Amazon", "Flipkart"]
        },
        "sort": "price_asc"  // Options: price_asc, price_desc, rating_desc, discount_desc
    }
    """
    try:
        data = request.get_json()

        # Validate input
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400

        if len(query) < 2:
            return jsonify({'success': False, 'error': 'Query too short (min 2 characters)'}), 400

        if len(query) > 200:
            return jsonify({'success': False, 'error': 'Query too long (max 200 characters)'}), 400

        # Extract parameters
        platforms = data.get('platforms')
        max_results = min(data.get('max_results', 10), 20)  # Cap at 20
        use_cache = data.get('use_cache', True)
        filters = data.get('filters', {})
        sort_by = data.get('sort', 'price_asc')

        print(f"🔍 Search request: '{query}' | Platforms: {platforms or 'all'} | Max: {max_results}")

        # Execute search
        search_start = time.time()
        result = scraper_manager.search_all(
            query=query,
            platforms=platforms,
            max_results=max_results,
            use_cache=use_cache
        )

        if not result['success']:
            return jsonify(result), 500

        products = result['products']

        # Apply filters
        if filters:
            products = apply_filters(products, filters)

        # Apply sorting
        products = apply_sorting(products, sort_by)

        # Generate analytics
        analytics = analytics_engine.analyze_products(products)

        # Group by platform for frontend
        platform_buckets = group_by_platform(products)

        # Prepare response
        response = {
            'success': True,
            'query': query,
            'products': products,
            'total': len(products),
            'filtered_total': len(products),
            'analytics': analytics,
            'platformBuckets': platform_buckets,
            'comparison': analytics,  # For backward compatibility
            'metadata': {
                'platforms_searched': result['platforms_searched'],
                'platforms_succeeded': result['platforms_succeeded'],
                'platform_stats': result['platform_stats'],
                'elapsed_time': result['elapsed_time'],
                'from_cache': result['from_cache'],
                'timestamp': result['timestamp']
            }
        }

        search_elapsed = time.time() - search_start
        print(f"✅ Search completed in {search_elapsed:.2f}s | {len(products)} products | Cache: {result['from_cache']}")

        return jsonify(response)

    except Exception as e:
        print(f"❌ Search error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'An error occurred during search',
            'details': str(e)
        }), 500


@app.route('/api/compare', methods=['POST'])
def compare_products():
    """
    Advanced comparison between specific products

    Request body:
    {
        "products": [
            {"title": "Product 1", "platform": "Amazon", ...},
            {"title": "Product 2", "platform": "Flipkart", ...}
        ]
    }
    """
    try:
        data = request.get_json()
        products = data.get('products', [])

        if len(products) < 2:
            return jsonify({'success': False, 'error': 'At least 2 products required'}), 400

        # Generate comparison analytics
        analytics = analytics_engine.analyze_products(products)

        # Find similar products
        similar_groups = product_matcher.group_similar_products(products)

        return jsonify({
            'success': True,
            'analytics': analytics,
            'similar_groups': len(similar_groups),
            'recommendations': analytics.get('recommendation')
        })

    except Exception as e:
        print(f"❌ Compare error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def apply_filters(products: list, filters: dict) -> list:
    """Apply filters to product list"""
    filtered = products

    # Price range filter
    if 'min_price' in filters:
        min_price = filters['min_price']
        filtered = [p for p in filtered if p.get('price_numeric') and p['price_numeric'] >= min_price]

    if 'max_price' in filters:
        max_price = filters['max_price']
        filtered = [p for p in filtered if p.get('price_numeric') and p['price_numeric'] <= max_price]

    # Rating filter
    if 'min_rating' in filters:
        min_rating = filters['min_rating']
        def has_min_rating(product):
            rating = product.get('rating', 'N/A')
            if rating == 'N/A':
                return False
            try:
                numeric = float(rating.replace('⭐', '').strip())
                return numeric >= min_rating
            except:
                return False
        filtered = [p for p in filtered if has_min_rating(p)]

    # Platform filter
    if 'platforms' in filters:
        allowed_platforms = filters['platforms']
        filtered = [p for p in filtered if p['platform'] in allowed_platforms]

    # Availability filter
    if 'in_stock_only' in filters and filters['in_stock_only']:
        filtered = [p for p in filtered if p.get('availability') != 'Out of Stock']

    return filtered


def apply_sorting(products: list, sort_by: str) -> list:
    """Apply sorting to product list"""
    if sort_by == 'price_asc':
        return sorted(products, key=lambda x: x.get('price_numeric') or float('inf'))

    elif sort_by == 'price_desc':
        return sorted(products, key=lambda x: x.get('price_numeric') or 0, reverse=True)

    elif sort_by == 'rating_desc':
        def get_rating(product):
            rating = product.get('rating', 'N/A')
            if rating == 'N/A':
                return 0
            try:
                return float(rating.replace('⭐', '').strip())
            except:
                return 0
        return sorted(products, key=get_rating, reverse=True)

    elif sort_by == 'discount_desc':
        return sorted(products, key=lambda x: x.get('discount') or 0, reverse=True)

    return products


def group_by_platform(products: list) -> list:
    """Group products by platform"""
    platforms = {}

    for product in products:
        platform = product['platform']
        if platform not in platforms:
            platforms[platform] = []
        platforms[platform].append(product)

    return [
        {'platform': platform, 'products': prods}
        for platform, prods in platforms.items()
    ]


# Cleanup on exit
def cleanup():
    print("\n🧹 JARVIS shutting down...")
    scraper_manager.cleanup()
    print("✅ Cleanup complete. JARVIS offline.")

atexit.register(cleanup)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 JARVIS PRICE INTELLIGENCE PLATFORM - ONLINE")
    print("=" * 60)
    print(f"📊 Platforms: {', '.join(scraper_manager.get_available_platforms())}")
    print(f"⚡ Max Workers: {scraper_manager.max_workers}")
    print(f"💾 Cache TTL: {scraper_manager.cache_ttl}s")
    print("🛡️  Safety: Rate limiting, delays, UA rotation enabled")
    print("=" * 60)
    print("🌐 Server starting on http://localhost:5000")
    print("💡 API Docs: http://localhost:5000")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
