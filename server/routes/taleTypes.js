const express = require('express');
const router = express.Router();
const TaleType = require('../models/TaleType');
const TaleVariant = require('../models/TaleVariant');

// GET /api/tale-types — list all tale types
router.get('/', async (req, res) => {
  try {
    const taleTypes = await TaleType.find().sort({ atu_code: 1 });
    res.json(taleTypes);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/tale-types/:id — get a single tale type
router.get('/:id', async (req, res) => {
  try {
    const taleType = await TaleType.findOne({ tale_type_id: req.params.id });
    if (!taleType) return res.status(404).json({ error: 'Tale type not found' });
    res.json(taleType);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/tale-types/:id/variants — get all variants within a tale type
router.get('/:id/variants', async (req, res) => {
  try {
    const variants = await TaleVariant.find({ tale_type: req.params.id })
      .select('-processed_tokens')
      .sort({ tradition: 1 });
    res.json({ tale_type_id: req.params.id, variants, count: variants.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/tale-types — create a new tale type
router.post('/', async (req, res) => {
  try {
    const taleType = new TaleType(req.body);
    await taleType.save();
    res.status(201).json(taleType);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

module.exports = router;
