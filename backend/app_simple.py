"""
Simple offline scraper using system Edge browser
No driver download required!
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import re
import time

app = Flask(__name__)
CORS(app)

class SimpleScraper:
    """Simple scraper using requests as fallback when Selenium fails"""

    def search_amazon(self, query):
        """Mock Amazon results for testing"""
        print(f"🔍 Searching Amazon for: {query}")
        return [
            {
                'title': f'{query} - Sample Product 1',
                'price': '₹25,999',
                'rating': '4.5',
                'url': f'https://www.amazon.in/s?k={query}',
                'platform': 'Amazon',
                'image': ''
            },
            {
                'title': f'{query} - Sample Product 2',
                'price': '₹22,499',
                'rating': '4.3',
                'url': f'https://www.amazon.in/s?k={query}',
                'platform': 'Amazon',
                'image': ''
            }
        ]

    def search_flipkart(self, query):
        """Mock Flipkart results for testing"""
        print(f"🔍 Searching Flipkart for: {query}")
        return [
            {
                'title': f'{query} - Flipkart Special',
                'price': '₹24,999',
                'rating': '4.4',
                'url': f'https://www.flipkart.com/search?q={query}',
                'platform': 'Flipkart',
                'image': ''
            }
        ]

scraper = SimpleScraper()

@app.route('/api/search', methods=['POST'])
def search_products():
    """Search products - using simple fallback"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        print(f"🔍 Search request for: {query}")

        # Get results from both platforms
        all_products = []
        all_products.extend(scraper.search_amazon(query))
        all_products.extend(scraper.search_flipkart(query))

        return jsonify({
            'success': True,
            'products': all_products,
            'total': len(all_products),
            'note': 'Using demo mode - driver setup needed for real scraping'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'mode': 'demo',
        'message': 'Running in demo mode - showing sample products'
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Price Comparison API (Demo Mode)',
        'status': 'Driver setup needed for real scraping',
        'endpoints': {
            'search': '/api/search (POST)',
            'health': '/api/health (GET)'
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Price Comparison API (Demo Mode)...")
    print("⚠️  Showing sample data until driver is fixed")
    print("📝 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
