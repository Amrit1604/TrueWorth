// JARVIS PRICE INTELLIGENCE - React Component
// Copy this to: frontend/src/App.jsx

import { useState, useRef } from 'react';
import './App.css';

const API_URL = 'http://localhost:5000/api/search';

function App() {
  const [query, setQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [metadata, setMetadata] = useState(null);
  const inputRef = useRef(null);

  const handleSearch = async (event) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) {
      setError('⚠️ Please enter a product name');
      return;
    }

    setLoading(true);
    setError('');
    setProducts([]);
    setAnalytics(null);
    setMetadata(null);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: trimmed, max_results: 5 })
      });

      const data = await response.json();
      if (!response.ok || !data.success) {
        setError(data.error || '❌ Search failed');
        return;
      }
      if (!data.products || data.products.length === 0) {
        setError(`❌ No products found for "${trimmed}"`);
        return;
      }

      setProducts(data.products);
      setAnalytics(data.analytics);
      setMetadata(data.metadata);
    } catch (err) {
      console.error(err);
      setError('❌ Backend not responding - Is JARVIS running?');
    } finally {
      setLoading(false);
    }
  };

  const bestDeal = analytics?.best_deal;
  const recommendation = analytics?.recommendation;

  return (
    <div className="jarvis-container">
      <div className="jarvis-bg">
        <div className="grid-lines"></div>
        <div className="glow-orb glow-orb-1"></div>
        <div className="glow-orb glow-orb-2"></div>
        <div className="glow-orb glow-orb-3"></div>
      </div>

      <header className="jarvis-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="arc-reactor">
              <div className="arc-core"></div>
              <div className="arc-ring"></div>
              <div className="arc-ring arc-ring-2"></div>
            </div>
            <h1 className="jarvis-title">
              <span className="title-main">JARVIS</span>
              <span className="title-sub">Price Intelligence</span>
            </h1>
          </div>
          <div className="status-indicator">
            <span className="status-dot"></span>
            <span className="status-text">SYSTEMS ONLINE</span>
          </div>
        </div>
      </header>

      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-wrapper">
            <div className="search-icon">🔍</div>
            <input
              ref={inputRef}
              type="text"
              className="search-input"
              placeholder="What can I help you find today, Sir?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="search-button" disabled={loading}>
              {loading ? '⚡ SCANNING...' : 'SEARCH'}
            </button>
          </div>
        </form>

        <div className="quick-actions">
          <button onClick={() => setQuery('macbook air m2')} className="quick-btn">MacBook Air M2</button>
          <button onClick={() => setQuery('iphone 15')} className="quick-btn">iPhone 15</button>
          <button onClick={() => setQuery('sony headphones')} className="quick-btn">Sony Headphones</button>
        </div>
      </div>

      {error && (
        <div className="error-panel fade-in">
          <div className="error-icon">⚠️</div>
          <div className="error-text">{error}</div>
        </div>
      )}

      {loading && (
        <div className="loading-panel fade-in">
          <div className="scanner-line"></div>
          <div className="loading-text">
            <div className="loading-spinner"></div>
            <p>Scanning {metadata?.platforms_searched || 4} platforms...</p>
            <p className="loading-sub">Analyzing market data...</p>
          </div>
        </div>
      )}

      {bestDeal && !loading && (
        <div className="best-deal-banner slide-in-top">
          <div className="banner-icon">🎯</div>
          <div className="banner-content">
            <h3>OPTIMAL SELECTION IDENTIFIED</h3>
            <p className="deal-text">
              {bestDeal.title} - <strong>{bestDeal.price}</strong> on {bestDeal.platform}
            </p>
            <p className="deal-savings">💰 Save {bestDeal.savings} ({bestDeal.savings_percent})</p>
          </div>
          <a href={bestDeal.url} target="_blank" rel="noopener noreferrer" className="view-deal-btn">
            VIEW DEAL →
          </a>
        </div>
      )}

      {recommendation && !loading && (
        <div className="recommendation-panel fade-in">
          <div className="rec-icon">💡</div>
          <p>{recommendation}</p>
        </div>
      )}

      {products.length > 0 && !loading && (
        <div className="products-section">
          <div className="section-header">
            <h2>Market Analysis Results</h2>
            <span className="results-count">{products.length} items found</span>
          </div>
          <div className="products-grid">
            {products.map((product, index) => (
              <div
                key={index}
                className="product-card"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="card-header">
                  <span className="platform-badge">{product.platform}</span>
                  {product.discount > 0 && (
                    <span className="discount-badge">-{product.discount}%</span>
                  )}
                </div>

                {product.image && (
                  <div className="card-image">
                    <img src={product.image} alt={product.title} />
                    <div className="image-overlay"></div>
                  </div>
                )}

                <div className="card-body">
                  <h3 className="product-title">{product.title}</h3>

                  <div className="product-meta">
                    {product.rating && (
                      <span className="rating">⭐ {product.rating}</span>
                    )}
                    {product.availability && (
                      <span className="availability">✓ {product.availability}</span>
                    )}
                  </div>

                  <div className="card-footer">
                    <div className="price-section">
                      <span className="price-label">PRICE</span>
                      <span className="price">{product.price}</span>
                    </div>
                    <a
                      href={product.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="view-btn"
                    >
                      VIEW →
                    </a>
                  </div>
                </div>

                <div className="card-glow"></div>
              </div>
            ))}
          </div>
        </div>
      )}

      {metadata && !loading && (
        <div className="metadata-panel fade-in">
          <div className="meta-grid">
            <div className="meta-item">
              <span className="meta-label">SCAN TIME</span>
              <span className="meta-value">{metadata.elapsed_time?.toFixed(2)}s</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">PLATFORMS</span>
              <span className="meta-value">{metadata.platforms_succeeded}/{metadata.platforms_searched}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">CACHE</span>
              <span className="meta-value">{metadata.from_cache ? '✓' : '✗'}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">TIMESTAMP</span>
              <span className="meta-value">{new Date(metadata.timestamp).toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      )}

      <footer className="jarvis-footer">
        <p>JARVIS Price Intelligence System v2.0 | Powered by TURBO MODE ⚡</p>
        <p className="footer-sub">Real-time market analysis across multiple platforms</p>
      </footer>
    </div>
  );
}

export default App;
