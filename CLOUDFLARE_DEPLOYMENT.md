# Cloudflare Pages deployment configuration

This project can be deployed to Cloudflare Pages with the following settings:

## Build Settings

- **Framework preset**: None
- **Build command**: `cd machi-vue && npm install && npm run build`
- **Build output directory**: `machi-vue/dist`
- **Root directory**: `/`

## Environment Variables

No environment variables required for the Vue.js frontend.

## Alternative: Direct dist deployment

You can also manually deploy the `machi-vue/dist` directory to Cloudflare Pages:

1. Run `npm run build` in the `machi-vue` directory
2. Upload the contents of `machi-vue/dist` to Cloudflare Pages
3. Configure the site as a Single Page Application (SPA)

## PWA Support

The built application includes:
- Service Worker for offline support
- Web App Manifest for PWA installation
- App icons in multiple sizes
- Full-screen display mode for mobile

## API Integration

The Vue app is configured to work with the FastAPI backend. Update the API URLs in the Vue app configuration to point to your deployed FastAPI instance.