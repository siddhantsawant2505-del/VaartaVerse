/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/ir/:path*',
        destination: 'http://localhost:8000/:path*',
      },
      {
        source: '/api/db/:path*',
        destination: 'http://localhost:5000/api/:path*',
      }
    ];
  },
};

module.exports = nextConfig;
