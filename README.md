# Socaio - AI-Powered Audience Analysis Tool

Understand how your audience will react to news content with AI-powered insights. Simply enter your news content and get detailed audience analysis and reaction predictions.

## ✨ What You Can Do

- 📝 **Analyze Any News Content**: Paste your article, press release, or news story
- 🤖 **Get AI-Generated Insights**: Automatically discover relevant audience characteristics
- 🎯 **Customize Your Analysis**: Select specific demographics, interests, and personality traits
- 📊 **Predict Reactions**: Get detailed reports on how different audience segments will respond
- 🔄 **Start Fresh Anytime**: Click the logo to return to the main page and analyze new content

## Key Features

- **Smart Characteristic Detection**: AI automatically identifies and pre-selects the most relevant audience traits
- **Interactive Selection**: Easily modify AI suggestions or choose your own characteristics
- **Comprehensive Reports**: Get detailed analysis including emotional reactions, engagement patterns, and recommendations
- **Clean Interface**: Intuitive design with easy navigation and scrollable panels
- **Fallback Mode**: Works even when AI is temporarily unavailable

## 🚀 Getting Started

### Step 1: Get Your OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key
4. Keep this key safe - you'll need it for setup

### Step 2: Deploy Your Own Copy

#### Option A: GitHub Pages (Recommended)

1. **Fork this repository** to your GitHub account
2. **Add your API key**:
   - Go to your forked repository settings
   - Click "Secrets and variables" → "Actions"
   - Create a new secret named `OPENAI_API_KEY`
   - Paste your API key as the value
3. **Enable GitHub Pages**:
   - Go to Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `gh-pages` (created automatically)
4. **Deploy**: Push any change to main branch - your site deploys automatically!

#### Option B: Other Hosting Platforms

**Netlify:**
1. Connect your GitHub repository to Netlify
2. Add environment variable: `OPENAI_API_KEY` = your API key
3. Build command: `npm run build`
4. Publish directory: `dist`

**Vercel:**
1. Import your GitHub repository to Vercel
2. Add environment variable: `OPENAI_API_KEY` = your API key
3. Build command: `npm run build`
4. Output directory: `dist`

### Step 3: Using the Application

1. **Enter your content**: Type or paste your news content in the input box
2. **AI analysis**: The system automatically analyzes your content and suggests relevant audience characteristics
3. **Customize selection**: Modify the AI-suggested characteristics or add your own
4. **Generate report**: Click "Generate Analysis Report" to get detailed insights
5. **Start over**: Click the "Socaio" logo anytime to analyze new content

## 💡 How to Use

1. **Fresh Start**: Each new analysis automatically clears previous conversations
2. **Scrollable Panel**: If many characteristics are generated, scroll within the right panel to access all options
3. **Visual Feedback**: AI-selected characteristics are marked in green with an "AI" badge
4. **Easy Navigation**: Click the logo in the top-left to return to the main page anytime

## 🔧 Technical Details

### How It Works Behind the Scenes

1. **Content Analysis**: Your news content is sent to OpenAI's GPT model
2. **Smart Detection**: AI identifies relevant demographics, interests, and personality traits
3. **Dynamic Interface**: The app automatically updates with AI-suggested characteristics
4. **Custom Analysis**: Generate detailed reaction reports based on your selected audience traits

### Security & Privacy

- ✅ **Safe Setup**: API key is injected at build time, not stored in source code
- ✅ **Public Repository Safe**: No sensitive information in your code
- ⚠️ **Browser Visibility**: Users with developer tools can see the API key in built files
- 🛡️ **Recommendation**: For production apps with sensitive data, consider a backend API

### What Happens If AI Is Unavailable?

- **Fallback Mode**: App continues working with preset characteristics
- **No Data Loss**: You can still generate reports using default audience segments
- **Transparent Communication**: Clear messages when AI features are temporarily unavailable

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

## 🛠️ Troubleshooting

### Common Issues & Solutions

**"API key not configured" error:**
- Double-check your environment variable is named exactly `OPENAI_API_KEY`
- Verify the build process completed successfully
- Make sure you're not opening the HTML file directly (use a web server)

**No AI analysis, only fallback mode:**
- Check your OpenAI account has available credits
- Verify your API key is valid and not expired
- Look in browser console for detailed error messages

**Interface issues:**
- Try refreshing the page
- Clear browser cache
- Make sure JavaScript is enabled

**Can't scroll to see all characteristics:**
- The right panel should scroll automatically - try using mouse wheel or scrollbar
- On mobile, use touch scrolling within the characteristics panel

### Need Help?

Check your browser's developer console (F12) for detailed error messages and debugging information.

---

## 📄 License

MIT License - You're free to use this for personal or commercial projects!

## 🤝 Contributing

Found a bug or have an idea? Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test locally
5. Submit a pull request

---

**💡 Pro Tip**: This tool works great for analyzing press releases, blog posts, social media content, or any text where understanding audience reaction matters. Try it with different types of content to see how audience characteristics change!