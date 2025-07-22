# Socaio - AI-Powered Audience Analysis Tool

An intelligent web application that analyzes news content and predicts audience reactions using OpenAI's GPT models.

## Features

- 🤖 **AI-Powered Analysis**: Automatically generates relevant audience characteristics based on news content
- 🎯 **Dynamic Characteristics**: Creates personalized demographic, psychographic, and interest-based audience profiles
- 📊 **Reaction Prediction**: Provides detailed analysis of how different audience segments will react
- 🔧 **Interactive Interface**: Clean, ChatGPT-style interface with real-time updates
- 🌐 **Static Hosting**: Optimized for deployment on GitHub Pages, Netlify, Vercel, etc.

## Quick Start

### Option 1: GitHub Pages Deployment (Recommended)

1. **Fork this repository** to your GitHub account

2. **Set up GitHub Secret**:
   - Go to your repository settings
   - Navigate to "Secrets and variables" → "Actions"
   - Create a new secret named `OPENAI_API_KEY`
   - Paste your OpenAI API key as the value

3. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `gh-pages` (will be created automatically)

4. **Push to main branch** - GitHub Actions will automatically build and deploy

### Option 2: Local Development/Testing

```bash
# Clone the repository
git clone [your-repo-url]
cd socaio

# Install dependencies
npm install

# Build for local testing (reads from .env file)
npm run build:local

# Serve the built files
# You can use any static server, like:
npx serve dist
# or
python -m http.server 8000 -d dist
```

### Option 3: Other Static Hosting Platforms

#### Netlify
1. Connect your GitHub repository
2. Set environment variable: `OPENAI_API_KEY` = your API key
3. Build command: `npm run build`
4. Publish directory: `dist`

#### Vercel
1. Import your GitHub repository
2. Add environment variable: `OPENAI_API_KEY` = your API key
3. Build command: `npm run build`
4. Output directory: `dist`

## Configuration

### API Key Setup

The application requires an OpenAI API key. The key is injected at build time and never exposed in the source code:

1. **Get an API key**: https://platform.openai.com/api-keys
2. **Set up environment variable**:
   - GitHub: Repository secrets
   - Netlify/Vercel: Environment variables in dashboard
   - Local: `.env` file with `OPENAI_API_KEY=your-key-here`

### Security Notes

- ✅ API key is injected at build time, not stored in code
- ✅ Safe for public repositories
- ✅ Works with static hosting
- ⚠️ Users with browser dev tools can still see the key in built files
- 💡 For maximum security, consider using a serverless function approach

## How It Works

1. **Content Analysis**: User enters news content
2. **AI Processing**: OpenAI analyzes content and identifies relevant audience characteristics
3. **Dynamic UI**: Interface updates with AI-generated characteristics (auto-selected in green)
4. **User Customization**: Users can modify selections as needed
5. **Reaction Analysis**: AI generates detailed audience reaction predictions

## File Structure

```
socaio/
├── chat/
│   └── index.html          # Main application (template)
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Actions deployment
├── build.js                # Build script for API key injection
├── package.json            # Dependencies and scripts
├── .env                    # Local API key (not committed)
└── README.md              # This file
```

## Development

### Local Server (Alternative)
If you prefer server-side development:

```bash
npm start  # Runs Express server on localhost:3000
```

### Building for Production

```bash
# For GitHub Actions (uses environment variable)
npm run build

# For local testing (reads from .env file)
npm run build:local
```

## Troubleshooting

### Common Issues

1. **"API key not configured" error**:
   - Ensure your environment variable is set correctly
   - Check that the build process completed successfully

2. **CORS errors**:
   - Make sure you're accessing the built files through a web server
   - Don't open `index.html` directly in browser

3. **API quota exceeded**:
   - Check your OpenAI account billing and usage
   - The app will fall back to static characteristics if API fails

### Browser Console

Check browser developer console for detailed error messages and debugging info.

## License

MIT License - feel free to use for personal or commercial projects.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

---

**Note**: This application makes direct API calls to OpenAI from the browser. While the API key is not stored in source code, it will be visible in the built application files. For production applications handling sensitive data, consider implementing a backend API proxy.