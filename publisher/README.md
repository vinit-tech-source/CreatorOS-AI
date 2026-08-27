# CreatorOS Twitter/X Publishing Integration

This is a standalone Node.js, Express, and TypeScript service for testing Twitter/X OAuth 2.0 PKCE flow and publishing tweets with media.

## Local Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure Environment Variables:**
   - Copy `.env.example` to `.env`.
   - Start ngrok to expose port 3000: `ngrok http 3000`
   - Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) and create an App.
   - Enable **OAuth 2.0**. Set the App permissions to "Read and write and Direct Messages".
   - Set the callback URL to `https://<your-ngrok-url>.ngrok.app/auth/twitter/callback`.
   - Copy the Client ID and Client Secret into your `.env` file.
   - Set `REDIRECT_URI` in `.env` to the ngrok callback URL.
   - Set `ENCRYPTION_KEY` to a random 32-character string.

3. **Run the server:**
   ```bash
   npm run dev
   ```

## Testing Flow

1. **Connect Account:** Visit `http://localhost:3000/auth/twitter/connect` in your browser. This redirects to Twitter for authentication.
2. **Verify Connection:** After redirect, you should see a success message with your username.
3. **Publish a Tweet (No Media):**
   ```bash
   curl -X POST http://localhost:3000/posts/publish \
        -H "Content-Type: application/json" \
        -d '{"connectedAccountId": 1, "text": "Test post from CreatorOS!"}'
   ```
4. **Upload Media:**
   ```bash
   curl -X POST http://localhost:3000/media/upload \
        -F "file=@/path/to/image.jpg"
   ```
   (This returns a `mediaUrl` that you can pass to the publish endpoint)
5. **Publish a Tweet (With Media):**
   ```bash
   curl -X POST http://localhost:3000/posts/publish \
        -H "Content-Type: application/json" \
        -d '{"connectedAccountId": 1, "text": "Testing media!", "mediaUrl": "https://<your-ngrok-url>.ngrok.app/uploads/file.jpg"}'
   ```
6. **Verify Posts:** Visit `http://localhost:3000/posts` in your browser to see the DB records.
