import { google } from 'googleapis';
import { NextResponse } from 'next/server';
import path from 'path';

export const dynamic = 'force-dynamic';

export async function GET() {
    try {
        console.log('API called - checking env vars');
        console.log('GOOGLE_SERVICE_ACCOUNT_JSON present:', !!process.env.GOOGLE_SERVICE_ACCOUNT_JSON);
        console.log('GOOGLE_SHEET_ID:', process.env.GOOGLE_SHEET_ID);

        // Check if we should use mock data
        const useMockData = !process.env.GOOGLE_SERVICE_ACCOUNT_JSON && !process.env.GOOGLE_SHEET_ID;

        if (useMockData) {
            console.log('Using mock data for testing');
            return NextResponse.json({
                stats: { total: 5, success: 100, processing: 0, lastActivity: '2024-01-22' },
                activity: [
                    {
                        timestamp: '2024-01-22T10:30:00Z',
                        'original video link': 'https://drive.google.com/file/d/mock1',
                        'final video link': 'https://drive.google.com/file/d/mock1_final',
                        platform: 'TikTok, Instagram Reels',
                        title: 'Sample Video 1',
                        caption: 'This is a sample caption',
                        hashtags: '#sample #video',
                        status: 'Completed'
                    },
                    {
                        timestamp: '2024-01-22T09:15:00Z',
                        'original video link': 'https://drive.google.com/file/d/mock2',
                        'final video link': 'https://drive.google.com/file/d/mock2_final',
                        platform: 'YouTube Shorts',
                        title: 'Sample Video 2',
                        caption: 'Another sample caption',
                        hashtags: '#demo #content',
                        status: 'Completed'
                    }
                ],
                platformDistribution: [
                    { name: 'TikTok', value: 2 },
                    { name: 'Instagram Reels', value: 1 },
                    { name: 'YouTube Shorts', value: 1 }
                ],
                spreadsheetId: 'mock-sheet-id',
                engineStatus: 'Idle'
            });
        }

        let authOptions: any = {
            scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
        };

        if (process.env.GOOGLE_SERVICE_ACCOUNT_JSON) {
            console.log('Using env var for credentials');
            // Vercel / Production: Use environment variable
            const credentials = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_JSON);
            authOptions.credentials = credentials;
        } else {
            console.log('Using local service_account.json file');
            // Local Development: Use file
            authOptions.keyFile = path.join(process.cwd(), '..', 'service_account.json');
        }

        const auth = new google.auth.GoogleAuth(authOptions);

        const sheets = google.sheets({ version: 'v4', auth });
        const spreadsheetId = process.env.GOOGLE_SHEET_ID || '1JTJzRwHIFe25MFFmOxofVNbymWUEr9M7VCM3F1zWlfA';

        // Fetch Data and Status in parallel
        const [response, statusResponse] = await Promise.all([
            sheets.spreadsheets.values.get({
                spreadsheetId,
                range: "'Content Engine'!A:G",
            }),
            sheets.spreadsheets.values.get({
                spreadsheetId,
                range: "'Backend Monitoring'!A1",
            }).catch(() => ({ data: { values: [['Idle']] } })) // Fallback if sheet doesn't exist yet
        ]);

        const engineStatus = statusResponse.data.values?.[0]?.[0] || 'Idle';

        const rows = response.data.values;
        if (!rows || rows.length <= 1) {
            return NextResponse.json({
                stats: { total: 0, success: 100, processing: 0, lastActivity: 'Never' },
                activity: [],
                platformDistribution: [],
            });
        }

        // Process rows (skip header)
        const header = rows[0];
        const dataRows = rows.slice(1).map(row => {
            const obj: any = {};
            header.forEach((key, i) => {
                obj[key.toLowerCase()] = row[i];
            });
            return obj;
        });

        // Calculate Stats
        const total = dataRows.length;
        const success = dataRows.length > 0 ? 100 : 0; // Simple logic for now
        const processing = 0; // Logic for this depends on how we track status in sheet

        const lastRow = dataRows[0]; // Assuming descending order or we sort it
        const lastActivity = lastRow ? lastRow.timestamp : 'None';

        // Platform Distribution
        const platforms: any = {};
        dataRows.forEach(row => {
            const pList = row.platform ? row.platform.split(',') : [];
            pList.forEach((p: string) => {
                const name = p.trim();
                platforms[name] = (platforms[name] || 0) + 1;
            });
        });

        const platformDistribution = Object.keys(platforms).map(name => ({
            name,
            value: platforms[name],
        }));

        return NextResponse.json({
            stats: { total, success, processing, lastActivity },
            activity: dataRows.slice(0, 10), // Last 10
            platformDistribution,
            spreadsheetId,
            engineStatus
        });

    } catch (error: any) {
        console.error('Sheet fetch error:', error);
        console.error('Error stack:', error.stack);
        console.error('Error message:', error.message);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
