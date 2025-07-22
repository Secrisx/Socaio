const fs = require('fs');
const path = require('path');

// Read the HTML template
const htmlPath = path.join(__dirname, 'chat', 'index.html');
const htmlContent = fs.readFileSync(htmlPath, 'utf8');

// Get API key from environment variable
const apiKey = process.env.OPENAI_API_KEY;

if (!apiKey) {
    console.error('Error: OPENAI_API_KEY environment variable is not set');
    process.exit(1);
}

// Replace the placeholder with actual API key
const processedContent = htmlContent.replace('{{OPENAI_API_KEY}}', apiKey);

// Create dist directory if it doesn't exist
const distDir = path.join(__dirname, 'dist');
if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
}

// Write the processed HTML to dist directory
fs.writeFileSync(path.join(distDir, 'index.html'), processedContent);

console.log('✅ Build completed successfully!');
console.log('📁 Output: dist/index.html');
console.log('🔑 API key injected securely');