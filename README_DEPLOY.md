# HKJC Race Scraper - Quick Deploy to Vercel

## 🚀 Quick Deploy Instructions

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**:
   ```bash
   cd /Users/millywong/personal_website
   vercel
   ```

3. **Follow the prompts**:
   - Link to existing project or create new one
   - Choose your team/account
   - Deploy!

### Option 2: Deploy via Vercel Dashboard

1. **Go to [vercel.com](https://vercel.com)**
2. **Click "New Project"**
3. **Import your Git repository** or drag & drop the project folder
4. **Deploy!**

## 📁 Project Structure

```
/
├── index.html          # Main web interface
├── api/
│   └── scrape.js       # Vercel serverless function
├── vercel.json         # Vercel configuration
├── package.json        # Project metadata
└── hkjc_scraper/       # Python scraper (for future integration)
```

## 🎯 Features

- **Clean, modern UI** with responsive design
- **Input validation** for race parameters
- **Loading states** and error handling
- **JSON output** with copy-to-clipboard functionality
- **Demo mode** (shows sample data when API not connected)

## 🔧 Current Status

- ✅ **Frontend**: Complete and ready
- ✅ **API Endpoint**: Basic structure ready
- ⚠️ **Python Integration**: Needs to be connected

## 🔗 Next Steps

1. **Deploy the current version** to see the UI
2. **Integrate Python scraper** by:
   - Adding Python runtime to Vercel
   - Calling the scraper from the API endpoint
   - Or using a separate Python service

## 🎨 UI Preview

The interface includes:
- **Header**: HKJC Race Scraper branding
- **Form**: Date picker, course selector, race number input
- **Help text**: Instructions from lines 79-81
- **Loading spinner**: During scraping
- **Results**: Formatted JSON output with copy button
- **Error handling**: User-friendly error messages

## 📱 Responsive Design

- Works on desktop, tablet, and mobile
- Clean gradient backgrounds
- Smooth animations and transitions
- Accessible form controls

## 🚀 Ready to Deploy!

Your website is ready to deploy to Vercel. The current version shows demo data, and you can integrate the actual Python scraper later.
