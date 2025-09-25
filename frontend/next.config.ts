import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true, // Temporarily ignore ESLint during builds for demo
  },
  typescript: {
    ignoreBuildErrors: false, // Keep TypeScript errors
  },
};

export default nextConfig;