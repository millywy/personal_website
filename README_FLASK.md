# 🏇 HKJC Race Scraper - Flask Direct Integration

## 🎯 **What This Is**

A **complete Flask web application** that runs your Python scraper directly through the web interface. No separate servers needed - everything runs in one application!

## ✨ **Key Features**

- **🚀 Direct Python Integration** - Scraper runs directly through web interface
- **📊 Real-time Progress** - Live progress bar and status updates
- **🔄 Background Processing** - Scraping runs in background threads
- **💾 Multiple Download Options** - Copy, download, or server download
- **📱 Responsive Design** - Works on desktop and mobile
- **⚡ Real HKJC Data** - Scrapes actual data from HKJC website

## 🚀 **Quick Start**

### **1. Install Flask (if needed)**
```bash
pip install -r requirements_flask.txt
```

### **2. Start the Application**
```bash
python start_flask.py
```

### **3. Open Your Browser**
Go to: **http://localhost:5000**

### **4. Scrape Real Data**
1. Enter race details (Date, Course, Race Number)
2. Click "🚀 Scrape Real HKJC Data"
3. Watch the progress bar
4. Download your JSON file!

## 🎨 **How It Works**

### **Frontend (HTML/CSS/JavaScript)**
- Beautiful, responsive web interface
- Real-time progress updates
- Multiple download options
- Error handling and validation

### **Backend (Flask + Python)**
- Flask web server
- Background thread processing
- Direct integration with your Python scraper
- RESTful API endpoints

### **Data Flow**
```
User Input → Flask API → Background Thread → Python Scraper → Real Data → Web Interface
```

## 📋 **API Endpoints**

### **POST /api/scrape**
Start scraping with parameters:
```json
{
  "date": "2025/09/17",
  "course": "HV",
  "raceno": 4
}
```

### **GET /api/status**
Get current scraping status:
```json
{
  "is_running": true,
  "progress": 50,
  "message": "Scraping race data...",
  "result": null,
  "error": null
}
```

### **GET /api/result**
Get scraping result when complete:
```json
{
  "scrape_info": { ... },
  "horses": [ ... ]
}
```

### **GET /api/download**
Download JSON file directly from server

## 🔧 **Technical Details**

### **Flask Application Structure**
```
app.py                 # Main Flask application
templates/
  └── index.html      # Web interface template
requirements_flask.txt # Flask dependencies
start_flask.py        # Startup script
```

### **Background Processing**
- Uses Python `threading` for non-blocking scraping
- Real-time status updates via polling
- Progress tracking and error handling
- Automatic cleanup of temporary files

### **Security Features**
- Input validation and sanitization
- Error handling and logging
- CORS headers for web requests
- Safe file handling

## 🎯 **Usage Examples**

### **Example 1: Happy Valley Race 4**
```bash
# Start the app
python start_flask.py

# In browser: http://localhost:5000
# Enter: Date: 2025/09/17, Course: HV, Race: 4
# Click: "🚀 Scrape Real HKJC Data"
```

### **Example 2: Sha Tin Race 8**
```bash
# Start the app
python start_flask.py

# In browser: http://localhost:5000
# Enter: Date: 2025/09/17, Course: ST, Race: 8
# Click: "🚀 Scrape Real HKJC Data"
```

## 📊 **Data Output**

The scraper outputs comprehensive JSON data:

```json
{
  "scrape_info": {
    "date": "2025/09/17",
    "course": "HV",
    "race_no": 4,
    "course_name": "Happy Valley",
    "scraped_at": "2025-09-17T04:24:52.502Z",
    "total_horses": 11
  },
  "horses": [
    {
      "馬號": "1",
      "馬匹ID": "K106",
      "馬名": "友得盈",
      "最近6輪": "6/8/10/10/6/5",
      "排位": "+17",
      "負磅": "135",
      "騎師": "潘頓",
      "練馬師": "丁冠豪",
      "當前評分": "-4",
      "國際評分": "",
      "配備": "B/TT",
      "讓磅": "-",
      "練馬師喜好": "+ 1",
      "馬齡": "4",
      "傷病記錄": [
        {
          "date": "21/04/2025",
          "description": "賽後翌日右前腿不良於行"
        }
      ],
      "往績紀錄": [
        {
          "race_date": "16/07/25",
          "venue": "跑馬地草地B",
          "distance": "1200",
          "barrier": "8",
          "weight": "120",
          "jockey": "班德禮",
          "position": "06",
          "time": "1.09.87",
          "equipment": "B1/TT",
          "rating": "44",
          "odds": "29",
          "track_condition": "好/快",
          "race_class": "4",
          "distance_to_winner": "2-3/4",
          "running_position": "1 1 6",
          "barrier_weight": "1103",
          "trainer": "丁冠豪"
        }
      ],
      "馬匹基本資料": "4歲閹馬，父系：Exceed And Excel，母系：Lady Of The Desert"
    }
  ]
}
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **"Module not found" errors**
   ```bash
   pip install -r requirements_flask.txt
   ```

2. **Port 5000 already in use**
   ```bash
   # Kill process using port 5000
   lsof -ti:5000 | xargs kill -9
   ```

3. **Scraper fails to start**
   - Check that your Python scraper is working: `python -m hkjc_scraper --help`
   - Ensure all dependencies are installed

4. **No data returned**
   - Check the HKJC website is accessible
   - Verify the race date and course are correct
   - Check the console for error messages

### **Debug Mode**
```bash
# Run with debug output
FLASK_DEBUG=1 python app.py
```

## 🎯 **Advantages of Flask Integration**

### **✅ Pros**
- **Single Application** - Everything in one place
- **Real-time Updates** - Live progress tracking
- **Easy Deployment** - Can be deployed to any Python hosting
- **User Friendly** - No command line needed
- **Scalable** - Can handle multiple users
- **Professional** - Production-ready web interface

### **⚠️ Considerations**
- **Resource Usage** - Runs Python scraper in background
- **Concurrent Users** - Limited by server resources
- **Deployment** - Requires Python hosting (not Vercel)

## 🚀 **Ready to Use!**

The Flask integration is **100% complete** and ready to use:

1. **Run locally** for development and testing
2. **Deploy to Python hosting** for production use
3. **Get real HKJC data** through a beautiful web interface
4. **Download JSON files** with comprehensive horse data

**Start scraping now!** 🏇

```bash
python start_flask.py
```
