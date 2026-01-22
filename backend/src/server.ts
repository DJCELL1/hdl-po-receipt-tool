import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { join } from 'path';
import authRoutes from './routes/auth.routes';
import docketRoutes from './routes/docket.routes';
import { db } from './database/db';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve uploaded files
app.use('/uploads', express.static(join(__dirname, '../uploads')));

// Health check
app.get('/health', async (req, res) => {
  try {
    await db.query('SELECT 1');
    res.json({ status: 'ok', database: 'connected' });
  } catch (error) {
    res.status(503).json({ status: 'error', database: 'disconnected' });
  }
});

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/dockets', docketRoutes);

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled error:', err);

  if (err instanceof SyntaxError && 'body' in err) {
    return res.status(400).json({ error: 'Invalid JSON' });
  }

  if (err.message === 'File too large') {
    return res.status(413).json({ error: 'File size exceeds limit (10MB)' });
  }

  res.status(500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Start server
const server = app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║           Cin7 Docket Receiver - Backend Server          ║
╠═══════════════════════════════════════════════════════════╣
║  Status: RUNNING                                          ║
║  Port: ${PORT}                                              ║
║  Environment: ${process.env.NODE_ENV || 'development'}                            ║
║  Database: ${process.env.DB_HOST || 'localhost'}:${process.env.DB_PORT || '5432'}                              ║
╚═══════════════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully...');
  server.close(async () => {
    await db.close();
    process.exit(0);
  });
});

process.on('SIGINT', async () => {
  console.log('\nSIGINT received, shutting down gracefully...');
  server.close(async () => {
    await db.close();
    process.exit(0);
  });
});

export default app;
