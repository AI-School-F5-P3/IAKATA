import { config } from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Solo llamar a config una vez
config({ path: path.resolve(__dirname, '.env') });

console.log('Environment variables loaded:', {
  DB_USER: process.env.DB_USER,
  DB_DEV_NAME: process.env.DB_DEV_NAME,
  DB_PASSWORD_SET: !!process.env.DB_PASSWORD
});

export const DB_DEV_NAME = process.env.DB_DEV_NAME;
export const DB_PASSWORD = process.env.DB_PASSWORD;
export const DB_USER = process.env.DB_USER;
export const PORT = process.env.PORT || 5001;
export const NODE_ENV = process.env.NODE_ENV;
export const TK_SECRET = process.env.TK_SECRET;
export const DB_TEST_NAME = process.env.DB_TEST_NAME;