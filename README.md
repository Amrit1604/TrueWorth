# 🛒 Safe Price Comparison Tool

A **educational** web application that safely compares prices across multiple e-commerce platforms using responsible scraping practices.

## ⚠️ Important Legal Notice
**This project is for educational purposes only.** Please read [SAFETY_GUIDELINES.md](SAFETY_GUIDELINES.md) before using.

## 🛡️ Safety Features
- ✅ **Rate limiting** (3 requests/minute per site)
- ✅ **Respectful delays** (3-7 seconds between requests)
- ✅ **User agent rotation** (5 different browsers)
- ✅ **Error handling** and graceful degradation
- ✅ **Limited results** (3 per site to be respectful)
- ✅ **Automatic cleanup** and resource management

## Project Structure
```
Scrapper/
├── frontend/          # React.js frontend
├── backend/           # Python Flask API
└── README.md
```

## Setup Instructions

### Backend Setup (Python)
1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask server:
   ```bash
   python app.py
   ```
   Server will run on http://localhost:5000

### Frontend Setup (React)
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```
   Frontend will run on http://localhost:5173

## How to Use
1. Start both backend and frontend servers
2. Open http://localhost:5173 in your browser
3. Search for any product (e.g., "iPhone 15", "laptop", "headphones")
4. View price comparisons from different platforms
5. Click "View Product" to go to the actual product page

## Features
- ✅ Search across multiple e-commerce platforms
- ✅ Price comparison and sorting
- ✅ Product ratings display
- ✅ Direct links to product pages
- ✅ Responsive design
- ✅ Real-time web scraping

## Technical Stack
- **Frontend**: React.js, Vite
- **Backend**: Python, Flask
- **Web Scraping**: Selenium WebDriver (modern, JavaScript-enabled scraping)
- **Safety**: Rate limiting, delays, user-agent rotation
- **Driver Management**: WebDriver Manager (automatic Chrome driver setup)
- **Styling**: CSS

## 🔒 Legal & Safety
- **Educational use only** - not for commercial purposes
- **Respects robots.txt** and website terms of service
- **Rate limited** to prevent IP bans
- **Respectful delays** between requests
- **Limited data collection** (essential info only)

## ⚖️ Disclaimer
This software is provided for educational purposes only. Users are responsible for compliance with all applicable laws and website terms of service. Always respect website policies and consider using official APIs when available.
