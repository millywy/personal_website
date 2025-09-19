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

        // For now, return a message indicating Python integration is needed
        // In production, you would integrate with your Python scraper here
        const response = {
            message: "Python scraper integration needed",
            instructions: "To get real data, run the Python scraper locally:",
            command: `python -m hkjc_scraper --date ${date} --course ${course} --raceno ${raceno} --out output.json`,
            parameters: {
                date,
                course,
                raceno
            },
            note: "The website will show demo data until the Python scraper is integrated with the API."
        };

        res.status(200).json(response);

    } catch (error) {
        console.error('Scraping error:', error);
        res.status(500).json({ 
            error: 'Internal server error',
            details: error.message 
        });
    }
}
