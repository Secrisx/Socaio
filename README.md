# Socaio - AI-Powered Audience Analysis Tool

Understand how your audience will react to news content with AI-powered insights. Built with Next.js for dynamic, server-side functionality.

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
- **Modern Tech Stack**: Built with Next.js, React, and serverless API routes
- **Fallback Mode**: Works even when AI is temporarily unavailable

## 🚀 Getting Started

### Step 1: Get Your OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key
4. Keep this key safe - you'll need it for setup

### Step 2: Development Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd socaio

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Add your OpenAI API key to .env
OPENAI_API_KEY=your_api_key_here

# Start development server
npm run dev
```

Your app will be available at `http://localhost:3000`

### Step 3: Deploy to Production

#### Vercel (Recommended)
1. Import your GitHub repository to Vercel
2. Add environment variable: `OPENAI_API_KEY` = your API key
3. Deploy automatically with `git push`

#### Netlify
1. Connect your GitHub repository to Netlify
2. Add environment variable: `OPENAI_API_KEY` = your API key
3. Build command: `npm run build`
4. Publish directory: `.next`

#### Other Platforms
Any platform supporting Next.js applications will work.

### Step 4: Using the Application

1. **Enter your content**: Type or paste your news content in the input box
2. **AI analysis**: The system automatically analyzes your content and suggests relevant audience characteristics
3. **Customize selection**: Modify the AI-suggested characteristics or add your own
4. **Generate report**: Click "Generate Analysis Report" to get detailed insights
5. **Start over**: Click the "Socaio" logo anytime to analyze new content

## 💡 How to Use

1. **Fresh Start**: Each new analysis automatically clears previous conversations
2. **Visual Feedback**: AI-selected characteristics are marked in green with an "AI" badge
3. **Easy Navigation**: Click the logo in the top-left to return to the main page anytime
4. **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🔧 Technical Details

### Tech Stack

- **Frontend**: Next.js 15, React 19
- **API Routes**: Next.js serverless functions
- **AI Integration**: OpenAI GPT-3.5-turbo
- **Styling**: CSS-in-JS with styled-jsx
- **Deployment**: Vercel (recommended)

### Project Structure

```
socaio/
├── pages/
│   ├── _app.js              # App wrapper
│   ├── index.js             # Main application page
│   └── api/
│       ├── auto-select.js   # AI characteristic detection
│       └── generate-report.js # Report generation
├── styles/
│   └── globals.css          # Global styles
├── next.config.js           # Next.js configuration
├── package.json             # Dependencies and scripts
├── .env.example             # Environment variables template
└── README.md               # This file
```

### How It Works Behind the Scenes

1. **Content Analysis**: Your news content is sent to OpenAI's GPT model via API routes
2. **Smart Detection**: AI identifies relevant demographics, interests, and personality traits
3. **Dynamic Interface**: React components update in real-time with AI suggestions
4. **Custom Analysis**: Generate detailed reaction reports based on selected audience traits

### Security & Privacy

- ✅ **Server-Side Security**: API keys are stored securely on the server
- ✅ **Environment Variables**: Sensitive data never exposed to client-side
- ✅ **Serverless Functions**: API routes run securely on Vercel/Netlify infrastructure
- 🛡️ **Production Ready**: Designed for secure deployment with proper environment management

## 📜 Available Scripts

```bash
npm run dev     # Start development server
npm run build   # Build for production
npm start       # Start production server
npm run lint    # Run Next.js linter
```

## 🛠️ Troubleshooting

### Common Issues & Solutions

**"API key not configured" error:**
- Check your `.env` file contains `OPENAI_API_KEY=your_key`
- Restart the development server after adding environment variables
- Verify your deployment platform has the environment variable configured

**No AI analysis, only fallback mode:**
- Check your OpenAI account has available credits
- Verify your API key is valid and not expired
- Check browser console or server logs for detailed error messages

**Build or deployment issues:**
- Ensure all dependencies are installed (`npm install`)
- Check that Next.js version is compatible
- Verify your deployment platform supports Next.js

### Need Help?

Check your browser's developer console (F12) and server logs for detailed error messages and debugging information.

---

## 📄 License

MIT License - You're free to use this for personal or commercial projects!

## 🤝 Contributing

Found a bug or have an idea? Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test locally with `npm run dev`
5. Submit a pull request

---

**💡 Pro Tip**: This tool works great for analyzing press releases, blog posts, social media content, or any text where understanding audience reaction matters. The Next.js architecture makes it fast, scalable, and easy to extend with additional features!