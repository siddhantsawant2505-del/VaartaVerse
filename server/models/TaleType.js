const mongoose = require('mongoose');

const TaleTypeSchema = new mongoose.Schema(
  {
    tale_type_id: {
      type: String,
      required: true,
      unique: true,
      index: true,
    },
    atu_code: {
      type: String,
      required: true,
    },
    canonical_title: {
      type: String,
      required: true,
    },
    description: {
      type: String,
    },
    key_motifs: [
      {
        type: String,
      },
    ],
  },
  { timestamps: true }
);

module.exports = mongoose.model('TaleType', TaleTypeSchema);
