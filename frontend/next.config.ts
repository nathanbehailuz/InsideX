import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true, // Temporarily ignore ESLint during builds for demo
  },
  typescript: {
    ignoreBuildErrors: false, // Keep TypeScript errors
  },
  images: {
    unoptimized: true, // Disable image optimization to avoid favicon issues
  },
  // Disable favicon processing
  experimental: {
    optimizePackageImports: [],
  },
};

export default nextConfig;
