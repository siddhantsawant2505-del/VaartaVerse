const mongoose = require('mongoose');

/**
 * QueryLog — Search Session Log
 * Stores query execution records, feedback applied, and latency metrics.
 */
const QueryLogSchema = new mongoose.Schema(
  {
    session_id: { type: String, index: true },
    query_text: { type: String, required: true },
    query_mode: {
      type: String,
      enum: ['boolean', 'vsm', 'nl_query', 'feedback'],
      required: true,
    },
    parsed_tokens: [{ type: String }],
    result_ids: [{ type: String }],
    feedback_applied: {
      relevant_ids: [{ type: String }],
      non_relevant_ids: [{ type: String }],
    },
    execution_time_ms: { type: Number },
    result_count: { type: Number },
  },
  { timestamps: true }
);

module.exports = mongoose.model('QueryLog', QueryLogSchema);
