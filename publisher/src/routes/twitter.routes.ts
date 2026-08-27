import { Router } from 'express';
import crypto from 'crypto';
import path from 'path';
import { TwitterAdapter } from '../adapters/twitter.adapter';
import { dbGet, dbRun, dbAll } from '../db/schema';
import { encryptToken, decryptToken } from '../services/token.service';
import { upload } from '../services/storage.service';
import dotenv from 'dotenv';
import fs from 'fs';
import axios from 'axios';

dotenv.config();

const router = Router();
const adapter = new TwitterAdapter(
  process.env.TWITTER_CLIENT_ID!,
  process.env.TWITTER_CLIENT_SECRET!,
  process.env.REDIRECT_URI!
);

// In-memory store for PKCE code_verifier (in production, use Redis or session)
const pkceStore = new Map<string, string>();

// === 1. OAUTH FLOW ===

router.get('/auth/twitter/connect', (req, res) => {
  const state = crypto.randomBytes(16).toString('hex');
  const { codeVerifier, codeChallenge } = adapter.generatePkce();
  
  pkceStore.set(state, codeVerifier);
  
  const authUrl = adapter.getAuthUrl(state, codeChallenge);
  res.redirect(authUrl);
});

router.get('/auth/twitter/callback', async (req, res) => {
  const { code, state, error } = req.query;

  if (error) {
    return res.status(400).send(`Authentication failed: ${error}`);
  }

  if (!code || !state) {
    return res.status(400).send('Missing code or state');
  }

  const codeVerifier = pkceStore.get(state as string);
  if (!codeVerifier) {
    return res.status(400).send('Invalid state or expired session');
  }

  pkceStore.delete(state as string);

  try {
    // 1. Get Tokens
    const tokenData = await adapter.getAccessToken(code as string, codeVerifier);
    
    // 2. Get User Info
    const userInfo = await adapter.getUserInfo(tokenData.access_token);
    
    // 3. Encrypt Tokens
    const encAccess = encryptToken(tokenData.access_token);
    const encRefresh = tokenData.refresh_token ? encryptToken(tokenData.refresh_token) : null;
    const expiresAt = new Date(Date.now() + tokenData.expires_in * 1000).toISOString();

    // 4. Save to DB
    await dbRun(`
      INSERT INTO connected_accounts 
      (platform, access_token, refresh_token, token_expires_at, twitter_user_id, twitter_username)
      VALUES ('twitter', ?, ?, ?, ?, ?)
    `, [encAccess, encRefresh, expiresAt, userInfo.id, userInfo.username]);

    res.json({ success: true, message: `Twitter connected as @${userInfo.username}` });
  } catch (err: any) {
    console.error('OAuth Callback Error:', err.response?.data || err.message);
    res.status(500).send('Failed to connect Twitter account.');
  }
});

// === 2. MEDIA UPLOAD ===

router.post('/media/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  
  // Construct a public URL using the host (assuming ngrok forwards host correctly)
  const protocol = req.headers['x-forwarded-proto'] || req.protocol;
  const host = req.get('host');
  const publicUrl = `${protocol}://${host}/uploads/${req.file.filename}`;
  
  res.json({ success: true, mediaUrl: publicUrl });
});

// === 3. PUBLISHING ===

async function getValidAccessToken(accountId: number): Promise<string> {
  const account = await dbGet<any>('SELECT * FROM connected_accounts WHERE id = ?', [accountId]);
  if (!account) throw new Error('Account not found');

  const now = new Date();
  const expiresAt = new Date(account.token_expires_at);

  // If token expires in less than 5 minutes, refresh it
  if (expiresAt.getTime() - now.getTime() < 5 * 60 * 1000) {
    if (!account.refresh_token) throw new Error('No refresh token available');
    
    const plainRefresh = decryptToken(account.refresh_token);
    const tokenData = await adapter.refreshToken(plainRefresh);
    
    const encAccess = encryptToken(tokenData.access_token);
    const encRefresh = tokenData.refresh_token ? encryptToken(tokenData.refresh_token) : account.refresh_token;
    const newExpiresAt = new Date(Date.now() + tokenData.expires_in * 1000).toISOString();

    await dbRun(`
      UPDATE connected_accounts 
      SET access_token = ?, refresh_token = ?, token_expires_at = ?
      WHERE id = ?
    `, [encAccess, encRefresh, newExpiresAt, accountId]);

    return tokenData.access_token;
  }

  return decryptToken(account.access_token);
}

router.post('/posts/publish', async (req, res) => {
  const { connectedAccountId, text, mediaUrl } = req.body;

  if (!connectedAccountId || !text) {
    return res.status(400).json({ error: 'connectedAccountId and text are required' });
  }

  let account;
  try {
    account = await dbGet<any>('SELECT * FROM connected_accounts WHERE id = ?', [connectedAccountId]);
  } catch (e) {
    // Ignore error
  }
  
  if (!account) {
    return res.status(404).json({ error: 'Connected account not found' });
  }

  let accessToken: string;
  try {
    accessToken = await getValidAccessToken(connectedAccountId);
  } catch (err: any) {
    return res.status(401).json({ error: 'Token invalid or refresh failed, please reconnect account' });
  }

  // Insert pending post record
  const postId = await dbRun(`
    INSERT INTO posts (connected_account_id, content_text, media_url, status)
    VALUES (?, ?, ?, 'pending')
  `, [connectedAccountId, text, mediaUrl || null]);

  try {
    let mediaId: string | undefined;

    // Optional media processing
    if (mediaUrl) {
      // Download the media to a temp file because adapter expects a local file path
      // If it's a local URL (e.g. from our own /uploads), we can resolve it directly
      const filename = mediaUrl.split('/uploads/').pop();
      const localPath = path.join(__dirname, '../../uploads', filename || '');
      
      let filePathToUpload = localPath;
      
      // If the URL is external, download it first
      if (!fs.existsSync(localPath)) {
        const tempPath = path.join(__dirname, '../../uploads', `temp-${Date.now()}.tmp`);
        const writer = fs.createWriteStream(tempPath);
        const response = await axios({ url: mediaUrl, method: 'GET', responseType: 'stream' });
        response.data.pipe(writer);
        await new Promise((resolve, reject) => {
          writer.on('finish', resolve);
          writer.on('error', reject);
        });
        filePathToUpload = tempPath;
      }

      // Upload to Twitter
      mediaId = await adapter.uploadMedia(accessToken, filePathToUpload);

      // Clean up temp file if created
      if (filePathToUpload !== localPath) {
        fs.unlinkSync(filePathToUpload);
      }
    }

    // Publish tweet
    const tweet = await adapter.createTweet(accessToken, text, mediaId);
    const tweetUrl = `https://twitter.com/${account.twitter_username}/status/${tweet.id}`;

    // Update post to published
    await dbRun(`
      UPDATE posts 
      SET status = 'published', platform_post_id = ?, platform_post_url = ?
      WHERE id = ?
    `, [tweet.id, tweetUrl, postId]);

    res.json({ success: true, tweetUrl });

  } catch (err: any) {
    console.error('Publishing Error:', err.response?.data || err.message);
    let errorMsg = err.message;
    
    if (err.response?.status === 401) {
      errorMsg = "Token invalid, please reconnect account";
    } else if (err.response?.status === 429) {
      errorMsg = "Rate limited, retry after some time";
    }

    await dbRun(`
      UPDATE posts 
      SET status = 'failed', error_message = ?
      WHERE id = ?
    `, [errorMsg, postId]);

    res.status(500).json({ error: errorMsg, details: err.response?.data });
  }
});

// === 4. LIST POSTS ===

router.get('/posts', async (req, res) => {
  try {
    const posts = await dbAll('SELECT * FROM posts ORDER BY created_at DESC');
    res.json(posts);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
