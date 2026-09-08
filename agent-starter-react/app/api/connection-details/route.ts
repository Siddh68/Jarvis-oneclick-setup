import { NextResponse } from 'next/server';
import { AccessToken, type AccessTokenOptions, type VideoGrant } from 'livekit-server-sdk';
import { RoomConfiguration } from '@livekit/protocol';
import fs from 'fs';
import path from 'path';

// don't cache the results
export const revalidate = 0;

export type ConnectionDetails = {
  serverUrl: string;
  roomName: string;
  participantName: string;
  participantToken: string;
};

function getConfig() {
  const pathsToTry = [
    path.join(process.cwd(), '..', 'user_config.json'), // Dev mode: unlikely if cwd is incorrect
    path.join(process.cwd(), 'user_config.json'),       // If cwd is root
    path.join(__dirname, '../../../../user_config.json'), // Relative to compiled output (fragile)
    'c:\\Users\\Siddh\\Desktop\\Jarvis\\user_config.json' // Fail-safe fallback (User specific)
  ];

  console.log("Debug: process.cwd() is:", process.cwd());

  for (const configPath of pathsToTry) {
    try {
      if (fs.existsSync(configPath)) {
        console.log("Debug: Found config at:", configPath);
        return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
      }
    } catch (e) {
      console.error("Error reading config at", configPath, e);
    }
  }

  console.error("Debug: user_config.json not found in any attempted paths.");
  return {};
}

export async function POST(req: Request) {
  try {
    const config = getConfig();
    console.log("Debug: Loaded config in connection-details:", JSON.stringify(config, null, 2));

    const API_KEY = config.api_keys?.livekit_key || process.env.LIVEKIT_API_KEY;
    const API_SECRET = config.api_keys?.livekit_secret || process.env.LIVEKIT_API_SECRET;
    const LIVEKIT_URL = config.api_keys?.livekit_url || process.env.LIVEKIT_URL;

    console.log("Debug: Resolved LiveKit Config:", {
      url: LIVEKIT_URL,
      hasKey: !!API_KEY,
      hasSecret: !!API_SECRET
    });

    if (!LIVEKIT_URL) {
      throw new Error('LIVEKIT_URL is not defined');
    }
    if (!API_KEY) {
      throw new Error('LIVEKIT_API_KEY is not defined');
    }
    if (!API_SECRET) {
      throw new Error('LIVEKIT_API_SECRET is not defined');
    }

    // Parse agent configuration from request body
    const body = await req.json();
    console.log("Debug: Request body:", body);
    const agentName: string = body?.room_config?.agents?.[0]?.agent_name;

    // Generate participant token
    // Generate participant token
    const participantName = config.user_name || 'user';
    const participantIdentity = `${participantName}_${Math.floor(Math.random() * 10_000)}`;
    const roomName = `voice_assistant_room_${Math.floor(Math.random() * 10_000)}`;

    const participantToken = await createParticipantToken(
      { identity: participantIdentity, name: participantName },
      roomName,
      API_KEY,
      API_SECRET,
      agentName
    );

    // Return connection details
    const data: ConnectionDetails = {
      serverUrl: LIVEKIT_URL,
      roomName,
      participantToken: participantToken,
      participantName,
    };
    const headers = new Headers({
      'Cache-Control': 'no-store',
    });
    return NextResponse.json(data, { headers });
  } catch (error) {
    if (error instanceof Error) {
      console.error(error);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }
  }
}

function createParticipantToken(
  userInfo: AccessTokenOptions,
  roomName: string,
  apiKey: string,
  apiSecret: string,
  agentName?: string
): Promise<string> {
  const at = new AccessToken(apiKey, apiSecret, {
    ...userInfo,
    ttl: '15m',
  });
  const grant: VideoGrant = {
    room: roomName,
    roomJoin: true,
    canPublish: true,
    canPublishData: true,
    canSubscribe: true,
  };
  at.addGrant(grant);

  if (agentName) {
    at.roomConfig = new RoomConfiguration({
      agents: [{ agentName }],
    });
  }

  return at.toJwt();
}
