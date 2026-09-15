const express = require('express');
const router = express.Router();
const Qrel = require('../models/Qrel');

// GET /api/qrels — list all qrels (evaluation ground truth)
router.get('/', async (req, res) => {
  try {
    const qrels = await Qrel.find().sort({ query_id: 1 });
    res.json(qrels);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/qrels/:query_id — get judgments for a specific query
router.get('/:query_id', async (req, res) => {
  try {
    const qrel = await Qrel.findOne({ query_id: req.params.query_id });
    if (!qrel) return res.status(404).json({ error: 'Qrel not found for this query_id' });
    res.json(qrel);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/qrels — create or replace a qrel judgment set
router.post('/', async (req, res) => {
  try {
    const existing = await Qrel.findOneAndUpdate(
      { query_id: req.body.query_id },
      req.body,
      { upsert: true, new: true, runValidators: true }
    );
    res.status(201).json(existing);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

module.exports = router;
