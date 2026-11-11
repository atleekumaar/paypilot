/** @type {import('next').NextConfig} */

// Detect missing NEXT_PUBLIC_API_URL during deployment builds
const isProd = process.env.NODE_ENV === "production";
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

if (isProd && process.env.REQUIRE_API_URL === "true" && !apiUrl) {
  throw new Error(
    "CRITICAL BUILD ERROR: NEXT_PUBLIC_API_URL is required for production builds but is not set. " +
    "Provide NEXT_PUBLIC_API_URL before compiling."
  );
} else if (!apiUrl) {
  console.warn(
    "\x1b[33m%s\x1b[0m",
    "[BUILD NOTICE] NEXT_PUBLIC_API_URL is unset. Client builds will default to http://127.0.0.1:8000. " +
    "For production deployment on Render/Vercel, set NEXT_PUBLIC_API_URL at build time."
  );
}

const nextConfig = {
  reactStrictMode: true,
  eslint: {
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
