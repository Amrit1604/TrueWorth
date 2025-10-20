# JARVIS FRONTEND CODE - App.jsx

## Copy this entire code to: frontend/src/App.jsx

```jsx
import { useState, useRef, useEffect } from 'react'
import './App.css'

const API_URL = 'http://localhost:5000/api/search'

function App() {
  const [query, setQuery] = useState('')
  const [products, setProducts] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [platformBuckets, setPlatformBuckets] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [metadata, setMetadata] = useState(null)
  const [darkMode, setDarkMode] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState({
    minPrice: '',
    maxPrice: '',
    minRating: ''
  })
  const [sortBy, setSortBy] = useState('price_asc')
  const inputRef = useRef(null)

  useEffect(() => {
    document.body.className = darkMode ? 'dark-mode' : ''
  }, [darkMode])

  const focusInput = () => inputRef.current?.focus()

  const handleSample = (value) => {
    setQuery(value)
    requestAnimationFrame(() => focusInput())
  }

  const handleSearch = async (event) => {
    event.preventDefault()
    const trimmed = query.trim()
    if (!trimmed) {
      setError('Enter a product to search')
      return
    }

    setLoading(true)
    setError('')
    setProducts([])
    setAnalytics(null)
    setPlatformBuckets([])
    setMetadata(null)

    try {
      const requestBody = { query: trimmed, max_results: 10, use_cache: true, sort: sortBy }
      const apiFilters = {}
      if (filters.minPrice) apiFilters.min_price = parseFloat(filters.minPrice)
      if (filters.maxPrice) apiFilters.max_price = parseFloat(filters.maxPrice)
      if (filters.minRating) apiFilters.min_rating = parseFloat(filters.minRating)
      if (Object.keys(apiFilters).length > 0) requestBody.filters = apiFilters

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      })

      const data = await response.json()
      if (!response.ok || !data.success) {
        setError(data.error || 'Search failed')
        return
      }
      if (!data.products || data.products.length === 0) {
        setError(`No products found for "${trimmed}"`)
        return
      }

      setProducts(data.products)
      setAnalytics(data.analytics)
      setPlatformBuckets(data.platformBuckets || [])
      setMetadata(data.metadata)
    } catch (err) {
      console.error(err)
      setError('Backend not responding')
    } finally {
      setLoading(false)
    }
  }

  const bestDeal = analytics?.best_deal
  const priceRange = analytics?.price_range
  const platforms = analytics?.platforms || []
  const recommendation = analytics?.recommendation

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="jarvis-logo">⚡</span>
          JARVIS<span className="brand-suffix">PRICE</span>
        </div>
        <div className="nav-actions">
          <button type="button" className="btn btn--ghost" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? '☀️' : '🌙'}
          </button>
          <button type="button" className="btn btn--ghost" onClick={() => handleSample('macbook air m2')}>
            Sample
          </button>
          <button type="button" className="btn btn--primary" onClick={focusInput}>
            New Search
          </button>
        </div>
      </header>

      <main className="content">
        <section className="hero">
          <h1 className="hero-quote">"JARVIS, FIND ME THE BEST PRICE."</h1>
          <p className="hero-sub">AI-powered price intelligence across 4+ marketplaces</p>
        </section>

        <section className="search-card">
          <div className="search-card__header">
            <span className="tag tag--live">🔴 Live</span>
            {metadata && (
              <>
                <span className="tag">{products.length} in {metadata.elapsed_time}s</span>
                {metadata.from_cache && <span className="tag">📦 Cached</span>}
                <span className="tag">{metadata.platforms_succeeded}/{metadata.platforms_searched} platforms</span>
              </>
            )}
          </div>

          <form className="search-form" onSubmit={handleSearch}>
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="macbook air m2, iphone 15 pro..."
              disabled={loading}
            />
            <button type="submit" className="btn btn--primary" disabled={loading}>
              {loading ? '⏳ Scraping...' : '🔍 Search'}
            </button>
          </form>

          <div className="search-controls">
            <button type="button" className="btn btn--ghost btn--sm" onClick={() => setShowFilters(!showFilters)}>
              {showFilters ? '▼' : '▶'} Filters
            </button>
          </div>

          {showFilters && (
            <div className="filters-panel">
              <input type="number" placeholder="Min ₹" value={filters.minPrice}
                onChange={(e) => setFilters({...filters, minPrice: e.target.value})} />
              <input type="number" placeholder="Max ₹" value={filters.maxPrice}
                onChange={(e) => setFilters({...filters, maxPrice: e.target.value})} />
              <input type="number" placeholder="Min Rating" value={filters.minRating}
                onChange={(e) => setFilters({...filters, minRating: e.target.value})} />
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="rating_desc">Rating: High to Low</option>
              </select>
            </div>
          )}

          {loading && <div className="loading-strip"><div className="spinner"></div><p>Scraping...</p></div>}
          {error && <div className="error-banner">❌ {error}</div>}
        </section>

        {recommendation && (
          <section className="recommendation-banner">
            <p>{recommendation}</p>
          </section>
        )}

        {bestDeal && (
          <section className="best-deal">
            <h2>🏆 Best Deal</h2>
            {priceRange && <span className="range-chip">Range: {priceRange.min} – {priceRange.max}</span>}
            <div className="best-deal-card">
              <div>
                <span className="platform-pill">{bestDeal.platform}</span>
                {bestDeal.discount && <span className="discount-badge">{bestDeal.discount}% OFF</span>}
                <h3>{bestDeal.title}</h3>
                <div className="best-price">{bestDeal.price}</div>
                {bestDeal.savings && <div className="savings">💰 Save {bestDeal.savings}</div>}
              </div>
              <a className="btn btn--primary" href={bestDeal.url} target="_blank" rel="noopener noreferrer">
                View Offer →
              </a>
            </div>
          </section>
        )}

        {platforms.length > 0 && (
          <section className="platform-comparison">
            <h2>📊 Platform Comparison</h2>
            <div className="platform-grid">
              {platforms.map((platform) => (
                <article className="platform-card" key={platform.platform}>
                  <div className="platform-card__head">
                    <span>{platform.platform}</span>
                    <span className={platform.cheapest.is_best_overall ? 'best' : ''}>
                      {platform.cheapest.is_best_overall ? '🏆 Best' : `+${platform.cheapest.difference}`}
                    </span>
                  </div>
                  <div className="platform-price">{platform.cheapest.price}</div>
                  <p>{platform.cheapest.title}</p>
                  <div className="platform-meta">
                    {platform.cheapest.rating !== 'N/A' && <span>{platform.cheapest.rating}</span>}
                    <span>{platform.count} offers</span>
                  </div>
                  <a className="btn btn--ghost" href={platform.cheapest.url} target="_blank" rel="noopener noreferrer">
                    View
                  </a>
                </article>
              ))}
            </div>
          </section>
        )}

        {platformBuckets.length > 0 && (
          <section className="product-section">
            <h2>📦 All Offers ({products.length})</h2>
            <div className="bucket-grid">
              {platformBuckets.map((bucket) => (
                <div className="bucket" key={bucket.platform}>
                  <div className="bucket-header">
                    <span>{bucket.platform}</span>
                    <span>{bucket.products.length} offers</span>
                  </div>
                  {bucket.products.slice(0, 5).map((product, i) => (
                    <div className="bucket-item" key={i}>
                      <div>
                        <div>{product.title}</div>
                        <div>{product.rating !== 'N/A' && product.rating}</div>
                      </div>
                      <div>
                        <span>{product.price}</span>
                        <a href={product.url} target="_blank" rel="noopener noreferrer">Open</a>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </section>
        )}

        {!loading && !error && products.length === 0 && (
          <section className="empty-state">
            <h3>Ready to Compare Prices</h3>
            <button onClick={() => handleSample('iphone 15 pro')}>iPhone 15 Pro</button>
            <button onClick={() => handleSample('macbook air m2')}>MacBook Air M2</button>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
```

## Instructions:

1. Delete the current `frontend/src/App.jsx`
2. Create a new file with the code above
3. The code is compatible with your existing CSS
4. Run frontend: `cd frontend && npm run dev`
5. Backend should already be running on port 5000

## Features in this frontend:

✅ Uses new JARVIS backend API
✅ Displays analytics & best deals
✅ Shows platform comparison
✅ Filter by price & rating
✅ Sort options
✅ Dark mode toggle
✅ Cache status display
✅ Loading states
✅ Error handling
✅ Sample query buttons

