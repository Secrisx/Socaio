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

  const { newsContent, selectedTraits } = req.body;

  if (!newsContent || !selectedTraits) {
    return res.status(400).json({ error: 'News content and selected traits are required' });
  }

  if (!process.env.OPENAI_API_KEY) {
    return res.status(500).json({ error: 'OpenAI API key not configured' });
  }

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
          content: `Provide a detailed analysis of how an audience with these characteristics would likely react to this news:

Audience Characteristics: ${selectedTraits.join(', ')}

News Content: "${newsContent}"

Please provide:
1. Overall emotional reaction (positive/negative/mixed/neutral)
2. Key concerns or interests this audience would have
3. Likely engagement behavior (share, comment, ignore, etc.)
4. Potential misconceptions or areas of confusion
5. Recommended messaging adjustments for this audience
6. Cultural or demographic-specific considerations

Format your response as a comprehensive analysis report.`
        }],
        max_tokens: 2000,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('OpenAI API error:', errorText);
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    const analysisReport = data.choices[0].message.content;
    
    res.status(200).json({ report: analysisReport });
  } catch (error) {
    console.error('Error in generate-report API:', error);
    res.status(500).json({ error: 'Failed to generate analysis report' });
  }
}