/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Static for Vercel free (fast load)
  trailingSlash: true,
  images: { unoptimized: true }  // No image opt for simple
};

module.exports = nextConfig;
