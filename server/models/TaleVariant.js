const mongoose = require('mongoose');

const TaleVariantSchema = new mongoose.Schema(
  {
    tale_id: {
      type: String,
      required: true,
      unique: true,
      index: true,
    },
    tale_type: {
      type: String,
      required: true,
      index: true,
    },
    title: {
      type: String,
      required: true,
    },
    region: {
      type: String,
      required: true,
    },
    tradition: {
      type: String,
      required: true,
    },
    source_collection: {
      type: String,
      required: true,
    },
    translator: {
      type: String,
      default: 'Unknown / Public Domain',
    },
    collection_era: {
      type: String,
    },
    raw_text: {
      type: String,
      required: true,
    },
    processed_tokens: [
      {
        type: String,
      },
    ],
  },
  { timestamps: true }
);

module.exports = mongoose.model('TaleVariant', TaleVariantSchema);
