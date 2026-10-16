import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    // Extra dev hosts (comma-separated), e.g. a preview proxy domain.
    allowedDevOrigins: process.env.NEXT_ALLOWED_DEV_ORIGINS?.split(",") ?? [],
    // Performance optimizations
    experimental: {
        optimizePackageImports: [
            "@radix-ui/*",
            "@tabler/icons-react",
            "recharts",
            "echarts",
            "framer-motion",
            "three",
        ],
    },
    logging: {
        fetches: {
            fullUrl: true,
        },
    },
    images: {
        formats: ["image/webp", "image/avif"],
        minimumCacheTTL: 60,
    },
    reactStrictMode: true,
};

export default nextConfig;

