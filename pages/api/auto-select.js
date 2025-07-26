export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { newsContent } = req.body;

  if (!newsContent) {
    return res.status(400).json({ error: 'News content is required' });
  }

  if (!process.env.OPENAI_API_KEY) {
    return res.status(500).json({ error: 'OpenAI API key not configured' });
  }

  const fixedOptions = {
    ages: ['18-', '18-24', '24-30', '30-36', '36-42', '42-48', '48-54', '54-60', '60-66', '66-72', '72+'],
    genders: ['male', 'female', 'non-binary'],
    personality_traits: ['analytical', 'empathetic', 'adventurous', 'conscientious', 'spontaneous', 'pragmatic', 'idealistic', 'assertive', 'diplomatic', 'introspective'],
    interests: ['technology', 'music', 'visual arts', 'sports', 'literature', 'finance', 'gaming', 'travel', 'culinary', 'environment']
  };

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [{
          role: 'user',
          content: `Analyze this news content and select the most relevant audience characteristics from the following fixed options. Return your selections in JSON format:

Available options:
- Ages: [${fixedOptions.ages.join(', ')}]
- Genders: [${fixedOptions.genders.join(', ')}]
- Personality Traits: [${fixedOptions.personality_traits.join(', ')}]
- Interests: [${fixedOptions.interests.join(', ')}]

Return format:
{
  "ages": ["24-30", "30-36"],
  "genders": ["male", "female"],
  "personality_traits": ["analytical", "pragmatic"],
  "interests": ["technology", "finance"]
}

News content to analyze: "${newsContent}"`
        }],
        max_tokens: 500,
        temperature: 0.3
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('OpenAI API error:', errorText);
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    const analysisText = data.choices[0].message.content;
    
    try {
      const selections = JSON.parse(analysisText);
      res.status(200).json(selections);
    } catch (parseError) {
      // Fallback selections if JSON parsing fails
      res.status(200).json({
        ages: ['24-30', '30-36'],
        genders: ['male', 'female'],
        personality_traits: ['analytical', 'pragmatic'],
        interests: ['technology']
      });
    }
  } catch (error) {
    console.error('Error in auto-select API:', error);
    res.status(500).json({ error: 'Failed to analyze content' });
  }
}