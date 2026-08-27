import axios from 'axios';
import crypto from 'crypto';
import FormData from 'form-data';
import fs from 'fs';

const TWITTER_API_V2 = 'https://api.twitter.com/2';
const TWITTER_API_V1 = 'https://upload.twitter.com/1.1'; // For media uploads

export class TwitterAdapter {
  private clientId: string;
  private clientSecret: string;
  private redirectUri: string;

  constructor(clientId: string, clientSecret: string, redirectUri: string) {
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.redirectUri = redirectUri;
  }

  // --- OAuth 2.0 PKCE Helpers ---
  
  generatePkce() {
    const codeVerifier = crypto.randomBytes(32).toString('base64url');
    const codeChallenge = crypto.createHash('sha256').update(codeVerifier).digest('base64url');
    return { codeVerifier, codeChallenge };
  }

  getAuthUrl(state: string, codeChallenge: string) {
    const scopes = ['tweet.read', 'tweet.write', 'users.read', 'offline.access'];
    const params = new URLSearchParams({
      response_type: 'code',
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      scope: scopes.join(' '),
      state: state,
      code_challenge: codeChallenge,
      code_challenge_method: 'S256'
    });
    return `https://twitter.com/i/oauth2/authorize?${params.toString()}`;
  }

  async getAccessToken(code: string, codeVerifier: string) {
    const params = new URLSearchParams({
      code,
      grant_type: 'authorization_code',
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      code_verifier: codeVerifier,
    });

    const authHeader = Buffer.from(`${this.clientId}:${this.clientSecret}`).toString('base64');

    const response = await axios.post(`${TWITTER_API_V2}/oauth2/token`, params.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': `Basic ${authHeader}`
      }
    });

    return response.data; // { access_token, refresh_token, expires_in }
  }

  async refreshToken(refreshToken: string) {
    const params = new URLSearchParams({
      refresh_token: refreshToken,
      grant_type: 'refresh_token',
      client_id: this.clientId,
    });

    const authHeader = Buffer.from(`${this.clientId}:${this.clientSecret}`).toString('base64');

    const response = await axios.post(`${TWITTER_API_V2}/oauth2/token`, params.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': `Basic ${authHeader}`
      }
    });

    return response.data; // { access_token, refresh_token, expires_in }
  }

  async getUserInfo(accessToken: string) {
    const response = await axios.get(`${TWITTER_API_V2}/users/me`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    return response.data.data; // { id, name, username }
  }

  // --- Publishing Helpers ---

  async uploadMedia(accessToken: string, filePath: string) {
    // Media upload must use OAuth 1.0a usually, but OAuth 2.0 user context works for API v2.
    // Wait, Twitter API v2 media upload is tricky. v1.1 accepts Bearer token for User Context if created via OAuth 2.0 PKCE?
    // Actually, as of 2023, Twitter allows Bearer tokens (OAuth 2.0) on the v1.1 media upload endpoint.
    
    const form = new FormData();
    form.append('media', fs.createReadStream(filePath));

    const response = await axios.post(`${TWITTER_API_V1}/media/upload.json`, form, {
      headers: {
        ...form.getHeaders(),
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    return response.data.media_id_string;
  }

  async createTweet(accessToken: string, text: string, mediaId?: string) {
    const payload: any = { text };
    if (mediaId) {
      payload.media = { media_ids: [mediaId] };
    }

    const response = await axios.post(`${TWITTER_API_V2}/tweets`, payload, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    return response.data.data; // { id, text }
  }
}
