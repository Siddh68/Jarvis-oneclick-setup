import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const CONFIG_FILE_PATH = path.join(process.cwd(), '..', 'user_config.json');

export async function POST(request: Request) {
    try {
        const data = await request.json();

        // Validating basic structure
        if (!data.user_name || !data.api_keys) {
            return NextResponse.json({ error: 'Invalid configuration data' }, { status: 400 });
        }

        // Write to file
        fs.writeFileSync(CONFIG_FILE_PATH, JSON.stringify(data, null, 2), 'utf-8');

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error('Failed to save config:', error);
        return NextResponse.json({ error: 'Failed to save configuration' }, { status: 500 });
    }
}

export async function GET() {
    try {
        if (fs.existsSync(CONFIG_FILE_PATH)) {
            const fileContent = fs.readFileSync(CONFIG_FILE_PATH, 'utf-8');
            const config = JSON.parse(fileContent);

            // Return full config for settings page
            return NextResponse.json({
                exists: true,
                ...config
            });
        }
        return NextResponse.json({ exists: false });
    } catch (error) {
        console.error('Failed to read config:', error);
        return NextResponse.json({ exists: false });
    }
}
export async function DELETE() {
    try {
        if (fs.existsSync(CONFIG_FILE_PATH)) {
            fs.unlinkSync(CONFIG_FILE_PATH);
            return NextResponse.json({ success: true });
        }
        return NextResponse.json({ error: 'Config file not found' }, { status: 404 });
    } catch (error) {
        console.error('Failed to delete config:', error);
        return NextResponse.json({ error: 'Failed to delete configuration' }, { status: 500 });
    }
}
