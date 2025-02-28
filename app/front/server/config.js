import { config } from 'dotenv';
config();

export const DB_DEV_NAME = process.env.DB_DEV_NAME;
export const DB_PASSWORD = process.env.DB_PASSWORD;
export const DB_USER = process.env.DB_USER;
export const PORT = process.env.PORT || 3000;
export const MYSQL_PORT = process.env.MYSQL_PORT || 3306;  // Añade esta línea
export const NODE_ENV = process.env.NODE_ENV;
export const TK_SECRET = process.env.TK_SECRET;
export const DB_TEST_NAME = process.env.DB_TEST_NAME;