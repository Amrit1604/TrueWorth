"""
Scraper Manager - Orchestrates all platform scrapers with concurrent execution
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import time
from datetime import datetime, timedelta


class ScraperManager:
    """Manages multiple platform scrapers with concurrent execution"""

    def __init__(self):
        self.scrapers = {}
        self.cache = {}
        self.cache_ttl = 600  # 10 minutes cache
        self.max_workers = 5  # Concurrent scraper threads

    def register_scraper(self, name: str, scraper):
        """Register a platform scraper"""
        self.scrapers[name] = scraper
        print(f"✅ Registered scraper: {name}")

    def get_available_platforms(self) -> List[str]:
        """Get list of registered platforms"""
        return list(self.scrapers.keys())

    def _get_cache_key(self, query: str, platforms: List[str]) -> str:
        """Generate cache key"""
        return f"{query.lower()}:{'_'.join(sorted(platforms))}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid"""
        if cache_key not in self.cache:
            return False

        cached_data = self.cache[cache_key]
        cache_time = cached_data.get('timestamp')

        if not cache_time:
            return False

        age = datetime.now() - cache_time
        return age.total_seconds() < self.cache_ttl

    def _get_from_cache(self, cache_key: str) -> Dict:
        """Retrieve from cache"""
        if self._is_cache_valid(cache_key):
            print(f"✅ Cache hit for: {cache_key}")
            return self.cache[cache_key]['data']
        return None

    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save to cache"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }

    def clear_cache(self):
        """Clear all cached results"""
        self.cache = {}
        print("✅ Cache cleared")

    def search_platform(self, platform_name: str, query: str, max_results: int = 10) -> List[Dict]:
        """Search a single platform"""
        if platform_name not in self.scrapers:
            print(f"⚠️ Platform not found: {platform_name}")
            return []

        try:
            scraper = self.scrapers[platform_name]
            return scraper.search(query, max_results)
        except Exception as e:
            print(f"❌ Error scraping {platform_name}: {e}")
            return []

    def search_all(self, query: str, platforms: List[str] = None, max_results: int = 10, use_cache: bool = True) -> Dict:
        """
        Search all platforms concurrently

        Args:
            query: Search query
            platforms: List of platform names (None = all platforms)
            max_results: Max results per platform
            use_cache: Whether to use caching

        Returns:
            Dict with results, metadata, and performance stats
        """
        start_time = time.time()

        # Use all platforms if none specified
        if platforms is None:
            platforms = self.get_available_platforms()

        # Filter to only registered platforms
        platforms = [p for p in platforms if p in self.scrapers]

        if not platforms:
            return {
                'success': False,
                'error': 'No valid platforms specified',
                'products': [],
                'total': 0
            }

        # Check cache
        cache_key = self._get_cache_key(query, platforms)
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                cached['from_cache'] = True
                return cached

        print(f"🔍 Searching {len(platforms)} platforms concurrently for: {query}")

        all_products = []
        platform_stats = {}
        errors = {}

        # Execute scrapers concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scraper tasks
            future_to_platform = {
                executor.submit(self.search_platform, platform, query, max_results): platform
                for platform in platforms
            }

            # Collect results as they complete
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    products = future.result(timeout=30)  # 30 second timeout per platform
                    all_products.extend(products)
                    platform_stats[platform] = {
                        'count': len(products),
                        'status': 'success'
                    }
                    print(f"✅ {platform}: {len(products)} products")
                except Exception as e:
                    errors[platform] = str(e)
                    platform_stats[platform] = {
                        'count': 0,
                        'status': 'failed',
                        'error': str(e)
                    }
                    print(f"❌ {platform}: Failed - {e}")

        end_time = time.time()
        elapsed = end_time - start_time

        # Sort by price (numeric)
        all_products.sort(key=lambda x: x.get('price_numeric') or float('inf'))

        result = {
            'success': True,
            'query': query,
            'products': all_products,
            'total': len(all_products),
            'platforms_searched': len(platforms),
            'platforms_succeeded': sum(1 for s in platform_stats.values() if s['status'] == 'success'),
            'platform_stats': platform_stats,
            'errors': errors if errors else None,
            'elapsed_time': round(elapsed, 2),
            'from_cache': False,
            'timestamp': datetime.now().isoformat()
        }

        # Save to cache
        if use_cache and all_products:
            self._save_to_cache(cache_key, result)

        print(f"✅ Search completed in {elapsed:.2f}s - {len(all_products)} total products")

        return result

    def cleanup(self):
        """Cleanup all scrapers"""
        print("🧹 Cleaning up scrapers...")
        for name, scraper in self.scrapers.items():
            try:
                scraper.close_driver()
            except:
                pass
        print("✅ Cleanup complete")

    def get_stats(self) -> Dict:
        """Get scraper manager statistics"""
        return {
            'registered_platforms': len(self.scrapers),
            'platforms': self.get_available_platforms(),
            'cache_entries': len(self.cache),
            'cache_ttl_seconds': self.cache_ttl,
            'max_workers': self.max_workers
        }
