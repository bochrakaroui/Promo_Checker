/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'www.mytek.tn',
      },
      {
        protocol: 'https',
        hostname: 'mytek.tn',
      },
      {
        protocol: 'https',
        hostname: 'www.tunisianet.com.tn',
      },
      {
        protocol: 'https',
        hostname: 'tunisianet.com.tn',
      },
      {
        protocol: 'https',
        hostname: 'spacenet.tn',
      },
      {
        protocol: 'https',
        hostname: 'www.spacenet.tn',
      },
    ],
    // Allow any domain (for development/testing)
    dangerouslyAllowSVG: true,
    unoptimized: true, // Disable optimization to avoid CORS issues
  },
};

module.exports = nextConfig;