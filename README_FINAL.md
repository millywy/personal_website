# 🏇 HKJC Race Scraper - Complete Solution

## 🎯 **What This Does**

This is a complete web application that scrapes real horse racing data from the Hong Kong Jockey Club (HKJC) website and provides it in a downloadable JSON format.

**Real Data Sources:**
- **Race Card**: [https://racing.hkjc.com/racing/information/Chinese/racing/RaceCard.aspx](https://racing.hkjc.com/racing/information/Chinese/racing/RaceCard.aspx)
- **Horse Details**: Individual horse pages with comprehensive past performance data
- **Injury Records**: Veterinary database with injury history

## 🚀 **Two Ways to Use**

### **Option 1: Quick Demo (Mock Data)**
1. Deploy to Vercel (see instructions below)
2. Use the website - it will show realistic demo data
3. Download JSON files with sample data

### **Option 2: Real Data (Python Integration)**
1. Run the Python scraper locally
2. Get real data from HKJC website
3. Download actual race data

## 📋 **How to Get Real Data**

### **Step 1: Run the Local Scraper**
```bash
# For Race 4 on 2025/09/17 at Happy Valley
python run_scraper.py 2025/09/17 HV 4
```

This will:
- ✅ Scrape real data from HKJC website
- ✅ Start a local web server on port 8080
- ✅ Automatically open your browser
- ✅ Show real horse data in the web interface

### **Step 2: Use the Website**
1. The website will automatically detect the local scraper
2. Enter the same parameters (2025/09/17, HV, 4)
3. Get real data instead of demo data
4. Download the actual JSON file

## 🌐 **Deploy to Vercel (Demo Mode)**

### **Quick Deploy:**
1. **Go to [vercel.com](https://vercel.com)**
2. **Click "New Project"**
3. **Import your repository** or drag & drop the folder
4. **Settings**:
   - Framework Preset: **Other**
   - Root Directory: **./**
   - Build Command: **OFF**
   - Output Directory: **OFF**
   - Install Command: **OFF**
5. **Click Deploy!**

### **Result:**
- ✅ Website works immediately
- ✅ Shows demo data for any race
- ✅ Download functionality works
- ✅ Professional UI with all features

## 📊 **Data Output Format**

The scraper outputs comprehensive JSON data for each horse:

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

## 🎨 **Website Features**

### **Input Form**
- **Race Date**: Date picker with validation
- **Course**: Dropdown (HV for Happy Valley, ST for Sha Tin)
- **Race Number**: Number input (1-12)
- **Real-time validation** with helpful error messages

### **Output Features**
- **📋 Copy JSON**: Copy to clipboard
- **💾 Download JSON**: Download as .json file
- **Auto-generated filename**: `hkjc_race_YYYYMMDD_COURSE_RACENO.json`
- **Syntax-highlighted JSON** display
- **Loading animations** during processing

### **Data Quality**
- **Real HKJC data** when using Python scraper
- **Comprehensive past performance** (last 6 races)
- **Injury records** from veterinary database
- **All required fields** as specified

## 🔧 **Technical Details**

### **Python Scraper**
- **Playwright** for browser automation
- **Pydantic** for data validation
- **Robust error handling** with retries
- **Respectful throttling** (400-1200ms delays)
- **Dynamic table parsing** for Chinese headers

### **Web Interface**
- **Pure HTML/CSS/JavaScript** (no frameworks)
- **Responsive design** for all devices
- **CORS-enabled API** for data fetching
- **Fallback to demo data** if scraper unavailable

## 🚨 **Important Notes**

1. **Real Data**: Only available when running the Python scraper locally
2. **Demo Data**: Always available for testing the interface
3. **HKJC Website**: The scraper respects the website's structure and rate limits
4. **Data Accuracy**: Real data comes directly from HKJC official website

## 🎯 **Perfect for**

- **Horse racing enthusiasts** who want structured data
- **Data analysts** working with racing statistics  
- **Developers** building racing applications
- **Researchers** studying horse performance patterns

## ✅ **Ready to Use**

The website is **100% functional** and ready to deploy. You can:
1. **Deploy immediately** for demo mode
2. **Run locally** for real data
3. **Download JSON files** with comprehensive horse data
4. **Use the professional UI** for easy data access

**Get started now!** 🏇
