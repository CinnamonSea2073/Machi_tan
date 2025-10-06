import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sizes = [
  { size: 192, name: 'pwa-192x192.png' },
  { size: 512, name: 'pwa-512x512.png' },
  { size: 180, name: 'apple-touch-icon.png' },
  { size: 48, name: 'favicon.ico' }
];

const svgBuffer = fs.readFileSync(path.join(__dirname, 'public', 'icon.svg'));

async function generateIcons() {
  console.log('Generating PWA icons...');
  
  for (const { size, name } of sizes) {
    try {
      const outputPath = path.join(__dirname, 'public', name);
      
      if (name.endsWith('.ico')) {
        // Generate ICO file
        await sharp(svgBuffer)
          .resize(size, size)
          .png()
          .toFile(outputPath.replace('.ico', '.png'));
        console.log(`Generated ${name.replace('.ico', '.png')}`);
      } else {
        // Generate PNG files
        await sharp(svgBuffer)
          .resize(size, size)
          .png()
          .toFile(outputPath);
        console.log(`Generated ${name}`);
      }
    } catch (error) {
      console.error(`Error generating ${name}:`, error);
    }
  }
  
  // Copy for favicon
  try {
    const faviconPath = path.join(__dirname, 'public', 'favicon.ico');
    const favicon48Path = path.join(__dirname, 'public', 'favicon.png');
    fs.copyFileSync(favicon48Path, faviconPath.replace('.ico', '.png'));
    console.log('Generated favicon files');
  } catch (error) {
    console.error('Error generating favicon:', error);
  }
  
  console.log('Icon generation complete!');
}

generateIcons();