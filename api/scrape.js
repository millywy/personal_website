// Vercel serverless function for HKJC scraping
export default async function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader(
        'Access-Control-Allow-Headers',
        'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
    );

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { date, course, raceno } = req.body;

        // Validate input
        if (!date || !course || !raceno) {
            return res.status(400).json({ 
                error: 'Missing required parameters: date, course, raceno' 
            });
        }

        if (!['HV', 'ST'].includes(course)) {
            return res.status(400).json({ 
                error: 'Invalid course. Must be HV or ST' 
            });
        }

        if (raceno < 1 || raceno > 12) {
            return res.status(400).json({ 
                error: 'Invalid race number. Must be between 1 and 12' 
            });
        }

        // For now, return a demo response since we need to set up the Python scraper
        // In production, you would call your Python scraper here
        const demoResponse = {
            message: "Demo response - Python scraper integration needed",
            parameters: {
                date,
                course,
                raceno
            },
            horses: [
                {
                    "馬號": "1",
                    "馬匹ID": "K106",
                    "馬名": "友得盈",
                    "馬匹編號": "",
                    "最近6輪": "6/8/10/10/6/5",
                    "排位": "+17",
                    "負磅": "135",
                    "騎師": "潘頓",
                    "練馬師": "丁冠豪",
                    "獨贏": "",
                    "位置": "",
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
        };

        res.status(200).json(demoResponse);

    } catch (error) {
        console.error('Scraping error:', error);
        res.status(500).json({ 
            error: 'Internal server error',
            details: error.message 
        });
    }
}
