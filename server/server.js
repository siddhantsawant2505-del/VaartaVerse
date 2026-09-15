require('dotenv').config();
const express = require('express');
const cors = require('cors');
const connectDB = require('./config/db');

const app = express();
const PORT = process.env.PORT || 5000;

// Connect to MongoDB
connectDB();

// Middleware
app.use(cors({ origin: process.env.CLIENT_ORIGIN || 'http://localhost:3000' }));
app.use(express.json({ limit: '10mb' })); // Generous limit for bulk tale ingestion

// Routes
app.use('/api/tales', require('./routes/tales'));
app.use('/api/tale-types', require('./routes/taleTypes'));
app.use('/api/qrels', require('./routes/qrels'));
app.use('/api/ir', require('./routes/irProxy'));
app.use('/api/ingest', require('./routes/ingest'));


// Health check
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', service: 'VaartaVerse Metadata Server', timestamp: new Date().toISOString() });
});

// 404 handler
app.use((_req, res) => {
  res.status(404).json({ error: 'Route not found on VaartaVerse metadata server' });
});

app.listen(PORT, () => {
  console.log(`[VaartaVerse Server] Listening on http://localhost:${PORT}`);
});
