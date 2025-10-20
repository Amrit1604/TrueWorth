import { useState, useRef } from 'react'
import './App.css'

const API_URL = 'http://localhost:5000/api/search'

function App() {
  const [query, setQuery] = useState('')
  const [products, setProducts] = useState([])
  const [comparison, setComparison] = useState(null)
  const [platformBuckets, setPlatformBuckets] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searchTime, setSearchTime] = useState(null)
  const inputRef = useRef(null)

  const focusInput = () => {
    inputRef.current?.focus()
  }

  const handleSample = (value) => {
    setQuery(value)
    requestAnimationFrame(() => focusInput())
  }

  const handleSearch = async (event) => {
    event.preventDefault()
    const trimmed = query.trim()

    if (!trimmed) {
      setError('Describe what you want to compare.')
      return
    }

    setLoading(true)
    setError('')
    setProducts([])
    setComparison(null)
    setPlatformBuckets([])
    setSearchTime(null)

    const start = performance.now()

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: trimmed })
      })

      const data = await response.json()
      const elapsed = ((performance.now() - start) / 1000).toFixed(1)
      setSearchTime(elapsed)

      if (!response.ok || !data.success) {
        setError(data.error || 'Search failed. Try again.')
        return
      }

      if (!data.products || data.products.length === 0) {
        setError(`No live offers found for "${trimmed}".`)
        return
      }

      setProducts(data.products)
      setComparison(data.comparison || null)
      setPlatformBuckets(data.platformBuckets || [])
    } catch (err) {
      console.error(err)
      setError('Backend not responding.')
    } finally {
      setLoading(false)
    }
  }

  const bestDeal = comparison?.bestDeal
  const priceRange = comparison?.priceRange

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">PRICE<span>GRID</span></div>
        <div className="nav-actions">
          <button type="button" className="btn btn--ghost" disabled>
            Docs
          </button>
          <button type="button" className="btn btn--ghost" onClick={() => handleSample('macbook air m2')}>
            Sample Query
          </button>
          <button type="button" className="btn btn--primary" onClick={focusInput}>
            New Comparison
          </button>
        </div>
      </header>

      <main className="content">
        <section className="hero">
          <h1 className="hero-quote">“STOP GUESSING PRICES — OWN THE COMPARISON.”</h1>
          <p className="hero-sub">
            Run a single query and watch the scraper audit every marketplace in real-time. No cached data. No guesswork.
          </p>
        </section>

        <section className="search-card">
          <div className="search-card__header">
            <span className="tag">Live Scraper</span>
            {searchTime && products.length > 0 && (
              <span className="tag tag--metric">{products.length} results in {searchTime}s</span>
            )}
          </div>

          <form className="search-form" onSubmit={handleSearch}>
            <input
              id="search-input"
              ref={inputRef}
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="macbook air m2 16gb 512gb"
              disabled={loading}
            />
            <button type="submit" className="btn btn--primary" disabled={loading}>
              {loading ? 'Scanning…' : 'Compare' }
            </button>
          </form>

          <p className="search-hint">Tip: mention storage / year / colour to narrow the comparison instantly.</p>

          {loading && (
            <div className="loading-strip">
              <span className="loading-dot" /><span className="loading-dot" /><span className="loading-dot" />
              <p>Scraping live marketplaces…</p>
            </div>
          )}

          {error && <div className="error-banner">{error}</div>}
        </section>

        {bestDeal && (
          <section className="best-deal">
            <div className="section-header">
              <h2>Best Offer Right Now</h2>
              {priceRange && (
                <span className="range-chip">Range {priceRange.min} – {priceRange.max}</span>
              )}
            </div>

            <div className="best-deal-card">
              <div className="best-deal-content">
                <span className="platform-pill">{bestDeal.platform}</span>
                <h3>{bestDeal.title}</h3>
                <div className="best-price">{bestDeal.price}</div>
                <div className="best-meta">
                  {bestDeal.rating && bestDeal.rating !== '—' && <span>{bestDeal.rating}</span>}
                  <span>Direct retailer link</span>
                </div>
              </div>
              <a className="btn btn--primary" href={bestDeal.url} target="_blank" rel="noopener noreferrer">
                View Offer
              </a>
            </div>
          </section>
        )}

        {comparison?.platforms?.length > 0 && (
          <section className="platform-comparison">
            <div className="section-header">
              <h2>Marketplace Breakdown</h2>
              <p className="section-sub">Cheapest validated offer from each platform plus price spread & rating.</p>
            </div>

            <div className="platform-grid">
              {comparison.platforms.map((platform) => (
                <article className="platform-card" key={platform.platform}>
                  <div className="platform-card__head">
                    <span className="platform-name">{platform.platform}</span>
                    <span className={`platform-delta ${platform.differenceValue < 1 ? 'platform-delta--best' : ''}`}>
                      {platform.differenceValue < 1 ? 'Best price' : `+${platform.differenceLabel}`}
                    </span>
                  </div>
                  <div className="platform-price">{platform.cheapest.price}</div>
                  <p className="platform-title">{platform.cheapest.title}</p>
                  <div className="platform-meta">
                    {platform.cheapest.rating && platform.cheapest.rating !== '—' && <span>{platform.cheapest.rating}</span>}
                    <span>{platform.count} offers</span>
                    <span>Avg {platform.averagePrice}</span>
                  </div>
                  <a className="btn btn--ghost" href={platform.cheapest.url} target="_blank" rel="noopener noreferrer">
                    View on {platform.platform}
                  </a>
                </article>
              ))}
            </div>
          </section>
        )}

        {platformBuckets.length > 0 && (
          <section className="product-section">
            <div className="section-header">
              <h2>All Validated Offers</h2>
              <p className="section-sub">Top listings from each marketplace, ordered by live price.</p>
            </div>

            <div className="bucket-grid">
              {platformBuckets.map((bucket) => (
                <div className="bucket" key={bucket.platform}>
                  <div className="bucket-header">
                    <span className="bucket-platform">{bucket.platform}</span>
                    <span className="bucket-count">{bucket.products.length} offers</span>
                  </div>
                  <div className="bucket-list">
                    {bucket.products.slice(0, 5).map((product, index) => (
                      <div className="bucket-item" key={`${bucket.platform}-${index}`}>
                        <div className="bucket-item__info">
                          <span className="item-rank">{index + 1}</span>
                          <div className="item-title">{product.title}</div>
                          <div className="item-meta">
                            {product.rating && product.rating !== '—' && <span>{product.rating}</span>}
                            <span>{product.platform}</span>
                          </div>
                        </div>
                        <div className="bucket-item__actions">
                          <span className="item-price">{product.price}</span>
                          <a className="link" href={product.url} target="_blank" rel="noopener noreferrer">
                            Open
                          </a>
                        </div>
                      </div>
                    ))}
                    {bucket.products.length > 5 && (
                      <div className="bucket-more">+{bucket.products.length - 5} more offers available</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {!loading && !error && products.length === 0 && (
          <section className="empty-state">
            <p>Start a comparison to see live marketplace results.</p>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
