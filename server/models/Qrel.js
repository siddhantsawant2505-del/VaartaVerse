const mongoose = require('mongoose');

/**
 * Qrel — Relevance Judgement Document
 * Stores human-curated query relevance judgements for IR evaluation.
 * Grade scale:  0 = not relevant, 1 = marginally relevant, 2 = relevant, 3 = highly relevant
 */
const QrelSchema = new mongoose.Schema(
  {
    query_id: {
      type: String,
      required: true,
      index: true,
    },
    query_text: {
      type: String,
      required: true,
    },
    judgments: [
      {
        tale_id: { type: String, required: true },
        relevance_score: { type: Number, min: 0, max: 3, required: true },
        notes: { type: String },
      },
    ],
  },
  { timestamps: true }
);

module.exports = mongoose.model('Qrel', QrelSchema);
