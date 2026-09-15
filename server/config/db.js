const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/vaartaverse');
    console.log(`[VaartaVerse Server] MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error(`[VaartaVerse Server] MongoDB Connection Error: ${error.message}`);
    // Non-blocking fallback for development mode when local Mongo is offline
  }
};

module.exports = connectDB;
