const express = require('express');
const router = express.Router();
const TaleVariant = require('../models/TaleVariant');

/**
 * Bulk Ingestion Routes
 * Handles loading the seed corpus into MongoDB and triggering
 * the FastAPI IR engine index rebuild.
 */

const IR_ENGINE_URL = process.env.IR_ENGINE_URL || 'http://localhost:8000';

// POST /api/ingest/bulk — ingest an array of tale records into MongoDB
router.post('/bulk', async (req, res) => {
  try {
    const tales = req.body;
    if (!Array.isArray(tales) || tales.length === 0) {
      return res.status(400).json({ error: 'Body must be a non-empty array of tale objects.' });
    }

    const ops = tales.map((tale) => ({
      updateOne: {
        filter: { tale_id: tale.tale_id },
        update: { $set: tale },
        upsert: true,
      },
    }));

    const result = await TaleVariant.bulkWrite(ops);
    res.json({
      status: 'ok',
      upserted: result.upsertedCount,
      modified: result.modifiedCount,
      total: tales.length,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/ingest/rebuild — trigger FastAPI IR engine to rebuild index from MongoDB
router.post('/rebuild', async (req, res) => {
  try {
    const fetch = (await import('node-fetch')).default;
    const source = req.body.source || 'json';
    const response = await fetch(`${IR_ENGINE_URL}/ingest/rebuild`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source }),
    });
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (err) {
    res.status(502).json({ error: `IR Engine unreachable: ${err.message}` });
  }
});

// GET /api/ingest/status — get current index statistics from FastAPI
router.get('/status', async (req, res) => {
  try {
    const fetch = (await import('node-fetch')).default;
    const response = await fetch(`${IR_ENGINE_URL}/ingest/status`);
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (err) {
    res.status(502).json({ error: `IR Engine unreachable: ${err.message}` });
  }
});

// POST /api/ingest/seed-from-file — load the server-side seed JSON and push to MongoDB + IR engine
router.post('/seed-from-file', async (req, res) => {
  try {
    const path = require('path');
    const fs = require('fs');

    // This path is relative to the server directory — adjust if needed
    const seedPath = path.resolve(__dirname, '../../ir_engine/data/corpus/tales.json');
    if (!fs.existsSync(seedPath)) {
      return res.status(404).json({ error: `Seed file not found at ${seedPath}` });
    }

    const tales = JSON.parse(fs.readFileSync(seedPath, 'utf-8'));

    // 1. Upsert into MongoDB
    const ops = tales.map((tale) => ({
      updateOne: {
        filter: { tale_id: tale.tale_id },
        update: { $set: tale },
        upsert: true,
      },
    }));
    const result = await TaleVariant.bulkWrite(ops);

    // 2. Trigger IR engine rebuild
    const fetch = (await import('node-fetch')).default;
    let irResult = { status: 'skipped' };
    try {
      const irResponse = await fetch(`${IR_ENGINE_URL}/ingest/rebuild`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: 'json' }),
      });
      irResult = await irResponse.json();
    } catch (irErr) {
      irResult = { status: 'ir_engine_offline', error: irErr.message };
    }

    res.json({
      mongodb: {
        upserted: result.upsertedCount,
        modified: result.modifiedCount,
        total: tales.length,
      },
      ir_engine: irResult,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
