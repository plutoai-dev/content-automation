import { google } from 'googleapis';
import { NextResponse } from 'next/server';
import path from 'path';

export const dynamic = 'force-dynamic';

export async function GET() {
    try {
        console.log('API called - checking env vars');
        console.log('GOOGLE_SERVICE_ACCOUNT_JSON present:', !!process.env.GOOGLE_SERVICE_ACCOUNT_JSON);
        console.log('GOOGLE_SHEET_ID:', process.env.GOOGLE_SHEET_ID);


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
                range: "'Backend Monitoring'!A:B",
            }).catch(() => ({ data: { values: [['Idle', 'System ready']] } })) // Fallback if sheet doesn't exist yet
        ]);

        const engineStatus = statusResponse.data.values?.[0]?.[0] || 'Idle';
        const statusMessage = statusResponse.data.values?.[0]?.[1] || 'System ready';

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
        const rawDataRows = rows.slice(1);
        const dataRows = rawDataRows.map((row, index) => {
            const obj: any = {};
            header.forEach((key, i) => {
                obj[key.toLowerCase()] = row[i];
            });

            // Extract title from content strategy (column G)
            if (obj['content strategy']) {
                const strategyText = obj['content strategy'];
                console.log('Processing content strategy:', strategyText.substring(0, 100) + '...');
                const titleMatch = strategyText.match(/TITLE:\s*(.*?)(?=\n\n|$)/);
                console.log('Title match:', titleMatch);
                obj.title = titleMatch ? titleMatch[1].trim() : `Video ${rawDataRows.length - index}`;
                console.log('Final title:', obj.title);
            } else {
                console.log('No content strategy found for row');
                obj.title = `Video ${rawDataRows.length - index}`;
            }

            // Map columns directly for links
            // Column B (index 1): original video link
            // Column C (index 2): final video link
            obj.originalLink = row[1] || '';
            obj.finalLink = row[2] || '';

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
            engineStatus,
            statusMessage
        });

    } catch (error: any) {
        console.error('Sheet fetch error:', error);
        console.error('Error stack:', error.stack);
        console.error('Error message:', error.message);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
