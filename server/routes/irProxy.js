const express = require('express');
const router = express.Router();
const QueryLog = require('../models/QueryLog');

/**
 * IR Proxy Routes
 * The Express server acts as a transparent proxy/logger for IR engine calls.
 * The Next.js client hits these endpoints; they log to MongoDB then forward to FastAPI.
 * In production you may want to use a dedicated reverse proxy (nginx/caddy) instead.
 */

const IR_ENGINE_URL = process.env.IR_ENGINE_URL || 'http://localhost:8000';

const getFetch = async () => {
  if (typeof globalThis.fetch === 'function') return globalThis.fetch;
  const module = await import('node-fetch');
  return module.default;
};

const proxyToIR = async (path, body, res) => {
  try {
    const fetchFn = await getFetch();
    const response = await fetchFn(`${IR_ENGINE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (err) {
    console.error(`[IR Proxy Error] ${path}:`, err);
    res.status(502).json({ error: `IR Engine unreachable: ${err.message}` });
  }
};

// POST /api/ir/search/boolean
router.post('/search/boolean', async (req, res) => {
  const start = Date.now();
  await proxyToIR('/search/boolean', req.body, res);
  // Fire-and-forget query log
  QueryLog.create({
    query_text: req.body.query,
    query_mode: 'boolean',
    execution_time_ms: Date.now() - start,
  }).catch(() => {});
});

// POST /api/ir/search/vsm
router.post('/search/vsm', async (req, res) => {
  const start = Date.now();
  await proxyToIR('/search/vsm', req.body, res);
  QueryLog.create({
    query_text: req.body.query,
    query_mode: 'vsm',
    execution_time_ms: Date.now() - start,
  }).catch(() => {});
});

// POST /api/ir/search/nl-query
router.post('/search/nl-query', async (req, res) => {
  const start = Date.now();
  await proxyToIR('/search/nl-query', req.body, res);
  QueryLog.create({
    query_text: req.body.query,
    query_mode: 'nl_query',
    execution_time_ms: Date.now() - start,
  }).catch(() => {});
});

// POST /api/ir/search/feedback (Rocchio re-ranking)
router.post('/search/feedback', async (req, res) => {
  const start = Date.now();
  await proxyToIR('/search/feedback', req.body, res);
  QueryLog.create({
    query_text: req.body.query,
    query_mode: 'feedback',
    feedback_applied: {
      relevant_ids: req.body.relevant_ids || [],
      non_relevant_ids: req.body.non_relevant_ids || [],
    },
    execution_time_ms: Date.now() - start,
  }).catch(() => {});
});

// POST /api/ir/evaluate
router.post('/evaluate', async (req, res) => {
  await proxyToIR('/evaluate', req.body, res);
});

// GET /api/ir/tale-type/:id/divergence
router.get('/tale-type/:id/divergence', async (req, res) => {
  try {
    const fetchFn = await getFetch();
    const response = await fetchFn(`${IR_ENGINE_URL}/tale-type/${req.params.id}/divergence`);
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (err) {
    res.status(502).json({ error: `IR Engine unreachable: ${err.message}` });
  }
});

// GET /api/ir/logs — last N query logs
router.get('/logs', async (req, res) => {
  try {
    const logs = await QueryLog.find()
      .sort({ createdAt: -1 })
      .limit(Number(req.query.limit) || 50);
    res.json(logs);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
