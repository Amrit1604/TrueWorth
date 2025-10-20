"""
Product matching and normalization utilities
Uses fuzzy matching and NLP techniques to match similar products across platforms
"""
from difflib import SequenceMatcher
import re
from typing import List, Dict, Set


class ProductMatcher:
    """Smart product matching across platforms"""

    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during'
        }

        self.brand_keywords = [
            'apple', 'samsung', 'oneplus', 'xiaomi', 'realme', 'oppo', 'vivo',
            'nokia', 'motorola', 'asus', 'dell', 'hp', 'lenovo', 'acer',
            'sony', 'lg', 'panasonic', 'philips', 'bosch', 'nike', 'adidas',
            'puma', 'reebok', 'boat', 'jbl', 'bose', 'macbook', 'iphone', 'ipad'
        ]

    def normalize_title(self, title: str) -> str:
        """Normalize product title for comparison"""
        if not title:
            return ""

        # Convert to lowercase
        normalized = title.lower()

        # Remove special characters but keep spaces and alphanumeric
        normalized = re.sub(r'[^\w\s]', ' ', normalized)

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        return normalized

    def extract_brand(self, title: str) -> str:
        """Extract brand name from title"""
        normalized = self.normalize_title(title)

        for brand in self.brand_keywords:
            if brand in normalized:
                return brand.capitalize()

        return "Unknown"

    def extract_specs(self, title: str) -> Dict[str, str]:
        """Extract specifications from title"""
        specs = {}

        # Storage (GB, TB)
        storage_match = re.search(r'(\d+)\s*(gb|tb)', title, re.IGNORECASE)
        if storage_match:
            specs['storage'] = storage_match.group(0).upper()

        # RAM
        ram_match = re.search(r'(\d+)\s*gb\s*ram', title, re.IGNORECASE)
        if ram_match:
            specs['ram'] = ram_match.group(0).upper()

        # Size (inches)
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(inch|"|cm)', title, re.IGNORECASE)
        if size_match:
            specs['size'] = size_match.group(0)

        # Color
        colors = ['black', 'white', 'blue', 'red', 'green', 'silver', 'gold', 'grey', 'pink']
        for color in colors:
            if color in title.lower():
                specs['color'] = color.capitalize()
                break

        return specs

    def calculate_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity score between two product titles"""
        norm1 = self.normalize_title(title1)
        norm2 = self.normalize_title(title2)

        # Basic sequence matching
        basic_score = SequenceMatcher(None, norm1, norm2).ratio()

        # Extract words
        words1 = set(norm1.split()) - self.stop_words
        words2 = set(norm2.split()) - self.stop_words

        # Jaccard similarity (word overlap)
        if not words1 or not words2:
            return basic_score

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        jaccard_score = intersection / union if union > 0 else 0

        # Weighted combination
        final_score = (basic_score * 0.4) + (jaccard_score * 0.6)

        return final_score

    def are_same_product(self, product1: Dict, product2: Dict, threshold: float = 0.6) -> bool:
        """Determine if two products are the same"""
        similarity = self.calculate_similarity(product1['title'], product2['title'])

        # Check brand match
        brand1 = self.extract_brand(product1['title'])
        brand2 = self.extract_brand(product2['title'])

        if brand1 != brand2 and brand1 != "Unknown" and brand2 != "Unknown":
            return False

        # Check specs match
        specs1 = self.extract_specs(product1['title'])
        specs2 = self.extract_specs(product2['title'])

        # If both have storage specs, they must match
        if 'storage' in specs1 and 'storage' in specs2:
            if specs1['storage'] != specs2['storage']:
                return False

        return similarity >= threshold

    def group_similar_products(self, products: List[Dict], threshold: float = 0.6) -> List[List[Dict]]:
        """Group similar products together"""
        groups = []
        used = set()

        for i, product1 in enumerate(products):
            if i in used:
                continue

            group = [product1]
            used.add(i)

            for j, product2 in enumerate(products[i+1:], i+1):
                if j in used:
                    continue

                if self.are_same_product(product1, product2, threshold):
                    group.append(product2)
                    used.add(j)

            groups.append(group)

        return groups

    def find_best_match(self, query_product: Dict, candidates: List[Dict], threshold: float = 0.5) -> Dict:
        """Find the best matching product from candidates"""
        best_match = None
        best_score = 0

        for candidate in candidates:
            score = self.calculate_similarity(query_product['title'], candidate['title'])
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate

        return best_match


class PriceNormalizer:
    """Normalize prices across different currencies and formats"""

    def __init__(self):
        self.currency_symbols = {
            '₹': 'INR',
            '$': 'USD',
            '€': 'EUR',
            '£': 'GBP'
        }

        # Approximate conversion rates (should be fetched from API in production)
        self.conversion_rates = {
            'INR': 1.0,
            'USD': 83.0,
            'EUR': 90.0,
            'GBP': 105.0
        }

    def extract_price(self, price_str: str) -> tuple:
        """Extract numeric price and currency"""
        if not price_str or price_str == "N/A":
            return None, None

        # Detect currency
        currency = 'INR'  # Default
        for symbol, code in self.currency_symbols.items():
            if symbol in price_str:
                currency = code
                break

        # Extract numeric value
        cleaned = re.sub(r'[^\d.]', '', price_str)
        try:
            price = float(cleaned)
            return price, currency
        except:
            return None, None

    def convert_to_inr(self, price: float, currency: str) -> float:
        """Convert price to INR"""
        if currency == 'INR':
            return price

        if currency in self.conversion_rates:
            return price * self.conversion_rates[currency]

        return price

    def normalize(self, price_str: str) -> Dict:
        """Normalize price string to standard format with metadata"""
        price, currency = self.extract_price(price_str)

        if price is None:
            return {
                'original': price_str,
                'numeric': None,
                'currency': None,
                'inr': None,
                'formatted': 'N/A'
            }

        inr_price = self.convert_to_inr(price, currency)

        return {
            'original': price_str,
            'numeric': price,
            'currency': currency,
            'inr': inr_price,
            'formatted': f"₹{inr_price:,.2f}"
        }
