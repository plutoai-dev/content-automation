import { google } from 'googleapis';
import { NextResponse } from 'next/server';
import path from 'path';

export async function GET() {
    try {
        let authOptions: any = {
            scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
        };

        if (process.env.GOOGLE_SERVICE_ACCOUNT_JSON) {
            // Vercel / Production: Use environment variable
            const credentials = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_JSON);
            authOptions.credentials = credentials;
        } else {
            // Local Development: Use file
            authOptions.keyFile = path.join(process.cwd(), '..', 'service_account.json');
        }

        const auth = new google.auth.GoogleAuth(authOptions);

        const sheets = google.sheets({ version: 'v4', auth });
        const spreadsheetId = process.env.GOOGLE_SHEET_ID || '1JTJzRwHIFe25MFFmOxofVNbymWUEr9M7VCM3F1zWlfA';
        const range = "'Content Engine'!A:G";

        const response = await sheets.spreadsheets.values.get({
            spreadsheetId,
            range,
        });

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
        });

    } catch (error: any) {
        console.error('Sheet fetch error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
