const express = require('express');
const router = express.Router();
const TaleVariant = require('../models/TaleVariant');

// GET /api/tales — list all tale variants with optional filters
router.get('/', async (req, res) => {
  try {
    const { tradition, region, tale_type, limit = 20, skip = 0 } = req.query;
    const filter = {};
    if (tradition) filter.tradition = { $regex: tradition, $options: 'i' };
    if (region) filter.region = { $regex: region, $options: 'i' };
    if (tale_type) filter.tale_type = tale_type;

    const tales = await TaleVariant.find(filter)
      .select('-raw_text -processed_tokens') // exclude large text fields in list view
      .limit(Number(limit))
      .skip(Number(skip))
      .sort({ createdAt: -1 });

    const total = await TaleVariant.countDocuments(filter);
    res.json({ tales, total, limit: Number(limit), skip: Number(skip) });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/tales/:tale_id — get a single tale variant by ID (with full text)
router.get('/:tale_id', async (req, res) => {
  try {
    const tale = await TaleVariant.findOne({ tale_id: req.params.tale_id });
    if (!tale) return res.status(404).json({ error: 'Tale not found' });
    res.json(tale);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/tales — ingest a new tale variant
router.post('/', async (req, res) => {
  try {
    const tale = new TaleVariant(req.body);
    await tale.save();
    res.status(201).json(tale);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// PUT /api/tales/:tale_id — update processed_tokens or metadata
router.put('/:tale_id', async (req, res) => {
  try {
    const tale = await TaleVariant.findOneAndUpdate(
      { tale_id: req.params.tale_id },
      req.body,
      { new: true, runValidators: true }
    );
    if (!tale) return res.status(404).json({ error: 'Tale not found' });
    res.json(tale);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

module.exports = router;
