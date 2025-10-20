"""
Advanced analytics for price comparison
"""
from typing import List, Dict
import statistics


class PriceAnalytics:
    """Advanced price analysis and comparison"""

    def __init__(self):
        pass

    def analyze_products(self, products: List[Dict]) -> Dict:
        """Comprehensive product analysis"""
        if not products:
            return {}

        # Extract valid prices
        prices = [p['price_numeric'] for p in products if p.get('price_numeric')]

        if not prices:
            return {}

        # Basic statistics
        min_price = min(prices)
        max_price = max(prices)
        avg_price = statistics.mean(prices)
        median_price = statistics.median(prices)

        # Price spread
        price_spread = max_price - min_price
        price_spread_percent = (price_spread / min_price * 100) if min_price > 0 else 0

        # Standard deviation (price volatility)
        std_dev = statistics.stdev(prices) if len(prices) > 1 else 0

        # Find best deal
        best_deal = min(products, key=lambda x: x.get('price_numeric') or float('inf'))
        worst_deal = max(products, key=lambda x: x.get('price_numeric') or float('-inf'))

        # Platform-wise analysis
        platform_stats = self._analyze_by_platform(products)

        # Discount analysis
        discount_stats = self._analyze_discounts(products)

        # Rating analysis
        rating_stats = self._analyze_ratings(products)

        return {
            'price_range': {
                'min': f"₹{min_price:,.2f}",
                'max': f"₹{max_price:,.2f}",
                'avg': f"₹{avg_price:,.2f}",
                'median': f"₹{median_price:,.2f}",
                'spread': f"₹{price_spread:,.2f}",
                'spread_percent': f"{price_spread_percent:.1f}%"
            },
            'volatility': {
                'std_dev': f"₹{std_dev:,.2f}",
                'coefficient_variation': f"{(std_dev/avg_price*100):.1f}%" if avg_price > 0 else "0%"
            },
            'best_deal': {
                'title': best_deal['title'],
                'price': best_deal['price'],
                'platform': best_deal['platform'],
                'url': best_deal['url'],
                'rating': best_deal.get('rating', 'N/A'),
                'discount': best_deal.get('discount'),
                'savings': f"₹{max_price - best_deal['price_numeric']:,.2f}",
                'savings_percent': f"{((max_price - best_deal['price_numeric'])/max_price*100):.1f}%"
            },
            'worst_deal': {
                'title': worst_deal['title'],
                'price': worst_deal['price'],
                'platform': worst_deal['platform'],
                'extra_cost': f"₹{worst_deal['price_numeric'] - min_price:,.2f}",
                'extra_cost_percent': f"{((worst_deal['price_numeric'] - min_price)/min_price*100):.1f}%"
            },
            'platforms': platform_stats,
            'discounts': discount_stats,
            'ratings': rating_stats,
            'recommendation': self._generate_recommendation(products, platform_stats)
        }

    def _analyze_by_platform(self, products: List[Dict]) -> Dict:
        """Analyze products grouped by platform"""
        platforms = {}

        for product in products:
            platform = product['platform']
            if platform not in platforms:
                platforms[platform] = {
                    'products': [],
                    'count': 0,
                    'prices': []
                }

            platforms[platform]['products'].append(product)
            platforms[platform]['count'] += 1
            if product.get('price_numeric'):
                platforms[platform]['prices'].append(product['price_numeric'])

        # Calculate stats for each platform
        platform_stats = []
        for platform, data in platforms.items():
            if not data['prices']:
                continue

            cheapest = min(data['products'], key=lambda x: x.get('price_numeric') or float('inf'))

            platform_stats.append({
                'platform': platform,
                'count': data['count'],
                'cheapest': {
                    'title': cheapest['title'],
                    'price': cheapest['price'],
                    'url': cheapest['url'],
                    'rating': cheapest.get('rating', 'N/A')
                },
                'avg_price': f"₹{statistics.mean(data['prices']):,.2f}",
                'price_range': {
                    'min': f"₹{min(data['prices']):,.2f}",
                    'max': f"₹{max(data['prices']):,.2f}"
                }
            })

        # Sort by cheapest price
        platform_stats.sort(key=lambda x: min(platforms[x['platform']]['prices']))

        # Add price difference from cheapest overall
        if platform_stats:
            overall_min = min(p['price_numeric'] for p in products if p.get('price_numeric'))
            for stat in platform_stats:
                cheapest_price = min(platforms[stat['platform']]['prices'])
                difference = cheapest_price - overall_min
                stat['cheapest']['difference'] = f"₹{difference:,.2f}"
                stat['cheapest']['difference_percent'] = f"{(difference/overall_min*100):.1f}%" if overall_min > 0 else "0%"
                stat['cheapest']['is_best_overall'] = (difference == 0)

        return platform_stats

    def _analyze_discounts(self, products: List[Dict]) -> Dict:
        """Analyze discount information"""
        discounts = [p['discount'] for p in products if p.get('discount')]

        if not discounts:
            return {
                'available': False,
                'message': 'No discount information available'
            }

        return {
            'available': True,
            'count': len(discounts),
            'avg_discount': f"{statistics.mean(discounts):.1f}%",
            'max_discount': f"{max(discounts)}%",
            'products_with_discounts': len(discounts),
            'total_products': len(products),
            'discount_ratio': f"{(len(discounts)/len(products)*100):.1f}%"
        }

    def _analyze_ratings(self, products: List[Dict]) -> Dict:
        """Analyze product ratings"""
        ratings = []
        for p in products:
            rating = p.get('rating', 'N/A')
            if rating != 'N/A':
                # Extract numeric rating (e.g., "4.5⭐" -> 4.5)
                try:
                    numeric = float(rating.replace('⭐', '').strip())
                    ratings.append(numeric)
                except:
                    pass

        if not ratings:
            return {
                'available': False,
                'message': 'No rating information available'
            }

        return {
            'available': True,
            'avg_rating': f"{statistics.mean(ratings):.2f}⭐",
            'highest_rating': f"{max(ratings):.1f}⭐",
            'lowest_rating': f"{min(ratings):.1f}⭐",
            'products_with_ratings': len(ratings),
            'total_products': len(products)
        }

    def _generate_recommendation(self, products: List[Dict], platform_stats: List[Dict]) -> str:
        """Generate smart recommendation"""
        if not products:
            return "No products found to analyze"

        best_deal = min(products, key=lambda x: x.get('price_numeric') or float('inf'))

        # Check if best deal has good rating
        rating = best_deal.get('rating', 'N/A')
        has_good_rating = False
        if rating != 'N/A':
            try:
                numeric_rating = float(rating.replace('⭐', '').strip())
                has_good_rating = numeric_rating >= 4.0
            except:
                pass

        # Check discount
        discount = best_deal.get('discount')

        recommendation = f"🎯 Best deal: {best_deal['price']} on {best_deal['platform']}"

        if has_good_rating:
            recommendation += f" with {rating} rating"

        if discount:
            recommendation += f" ({discount}% off)"

        # Price spread analysis
        prices = [p['price_numeric'] for p in products if p.get('price_numeric')]
        if len(prices) > 1:
            min_price = min(prices)
            max_price = max(prices)
            spread_percent = ((max_price - min_price) / min_price * 100)

            if spread_percent > 20:
                recommendation += f". ⚠️ Large price variation ({spread_percent:.0f}%) - compare carefully!"
            elif spread_percent < 5:
                recommendation += ". ✅ Prices are consistent across platforms."

        return recommendation

    def calculate_savings(self, target_price: float, comparison_price: float) -> Dict:
        """Calculate savings between two prices"""
        if not target_price or not comparison_price:
            return {}

        savings = comparison_price - target_price
        savings_percent = (savings / comparison_price * 100) if comparison_price > 0 else 0

        return {
            'amount': f"₹{savings:,.2f}",
            'percent': f"{savings_percent:.1f}%",
            'is_cheaper': savings > 0
        }
