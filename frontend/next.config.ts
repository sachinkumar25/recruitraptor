import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/api/parser/:path*',
        destination: 'http://localhost:8000/:path*', // Resume Parser Service
      },
      {
        source: '/api/discovery/:path*',
        destination: 'http://localhost:8001/:path*', // Profile Discovery Service
      },
      {
        source: '/api/enrichment/:path*',
        destination: 'http://localhost:8002/:path*', // Data Enrichment Service
      },
      {
        source: '/api/narrative/:path*',
        destination: 'http://localhost:8003/:path*', // Narrative Engine Service
      }
    ]
  }
};

export default nextConfig;
