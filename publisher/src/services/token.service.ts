import crypto from 'crypto';
import dotenv from 'dotenv';

dotenv.config();

// AES-256-CBC requires a 32-byte key and a 16-byte IV.
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || 'default_32_byte_key_123456789012'; // Must be 256 bytes (32 characters)
const IV_LENGTH = 16; // For AES, this is always 16

if (ENCRYPTION_KEY.length !== 32) {
  console.warn("WARNING: ENCRYPTION_KEY is not exactly 32 characters long. This may cause encryption to fail.");
}

export function encryptToken(text: string): string {
  if (!text) return text;
  try {
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(ENCRYPTION_KEY), iv);
    let encrypted = cipher.update(text);
    encrypted = Buffer.concat([encrypted, cipher.final()]);
    return iv.toString('hex') + ':' + encrypted.toString('hex');
  } catch (e) {
    console.error("Encryption failed:", e);
    return text; // Fallback or handle error appropriately in production
  }
}

export function decryptToken(text: string): string {
  if (!text) return text;
  try {
    const textParts = text.split(':');
    const iv = Buffer.from(textParts.shift()!, 'hex');
    const encryptedText = Buffer.from(textParts.join(':'), 'hex');
    const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(ENCRYPTION_KEY), iv);
    let decrypted = decipher.update(encryptedText);
    decrypted = Buffer.concat([decrypted, decipher.final()]);
    return decrypted.toString();
  } catch (e) {
    console.error("Decryption failed:", e);
    return text;
  }
}
