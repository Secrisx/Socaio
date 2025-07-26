import { useState, useEffect } from 'react';
import Head from 'next/head';

export default function Home() {
  const [currentQuery, setCurrentQuery] = useState('');
  const [selectedCharacteristics, setSelectedCharacteristics] = useState(new Set());
  const [showChat, setShowChat] = useState(false);
  const [showCharacteristics, setShowCharacteristics] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [messages, setMessages] = useState([]);
  const [reportContent, setReportContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const addMessage = (sender, content) => {
    setMessages(prev => [...prev, { sender, content }]);
  };

  const handleQuerySubmit = async () => {
    if (!currentQuery.trim()) return;

    setIsLoading(true);
    setMessages([]);
    setSelectedCharacteristics(new Set());
    setShowChat(true);
    setShowCharacteristics(true);
    setShowReport(false);

    addMessage('user', currentQuery);
    addMessage('assistant', "Analyzing your content to identify the most relevant audience characteristics...");

    try {
      const response = await fetch('/api/auto-select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ newsContent: currentQuery })
      });

      if (response.ok) {
        const autoSelections = await response.json();
        applyAutoSelections(autoSelections);
        updateLastMessage("I've analyzed your content and auto-selected the most relevant audience characteristics (marked in green). You can modify these selections and click 'Generate Analysis Report' when ready.");
      } else {
        updateLastMessage("Please select the audience characteristics you'd like to focus on and click 'Generate Analysis Report'. AI auto-selection is currently unavailable.");
      }
    } catch (error) {
      console.error('Error during AI auto-selection:', error);
      updateLastMessage("Please select the audience characteristics you'd like to focus on and click 'Generate Analysis Report'. AI auto-selection is currently unavailable.");
    }

    setIsLoading(false);
  };

  const updateLastMessage = (content) => {
    setMessages(prev => {
      const newMessages = [...prev];
      if (newMessages.length > 0 && newMessages[newMessages.length - 1].sender === 'assistant') {
        newMessages[newMessages.length - 1].content = content;
      }
      return newMessages;
    });
  };

  const applyAutoSelections = (autoSelections) => {
    const allSelections = [
      ...(autoSelections.ages || []),
      ...(autoSelections.genders || []),
      ...(autoSelections.personality_traits || []),
      ...(autoSelections.interests || [])
    ];
    setSelectedCharacteristics(new Set(allSelections));
  };

  const toggleCharacteristic = (value) => {
    const newSelected = new Set(selectedCharacteristics);
    if (newSelected.has(value)) {
      newSelected.delete(value);
    } else {
      newSelected.add(value);
    }
    setSelectedCharacteristics(newSelected);
  };

  const generateReport = async () => {
    if (selectedCharacteristics.size === 0) return;

    setIsLoading(true);
    const traits = Array.from(selectedCharacteristics);

    try {
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          newsContent: currentQuery,
          selectedTraits: traits
        })
      });

      if (response.ok) {
        const data = await response.json();
        setReportContent(data.report);
      } else {
        setReportContent(fallbackReport());
      }
    } catch (error) {
      console.error('Error generating report:', error);
      setReportContent(fallbackReport());
    }

    setShowReport(true);
    setIsLoading(false);
  };

  const fallbackReport = () => `
    <h4>Overall Analysis</h4>
    <p>This content would likely resonate with the selected demographic based on their characteristics.</p>
    
    <h4>Engagement Patterns</h4>
    <p>Audience engagement patterns suggest varying levels of interest and emotional response based on the selected traits.</p>
    
    <h4>Recommendations</h4>
    <ul>
        <li>Tailor messaging to address specific concerns of this demographic</li>
        <li>Consider cultural and generational factors when crafting communication strategy</li>
        <li>Monitor engagement metrics to validate assumptions</li>
        <li>Test different messaging approaches with this audience segment</li>
    </ul>
    
    <p><em>Note: Full AI analysis temporarily unavailable. Using general recommendations.</em></p>
  `;

  const goBackToMain = () => {
    setShowChat(false);
    setShowCharacteristics(false);
    setShowReport(false);
    setCurrentQuery('');
    setMessages([]);
    setSelectedCharacteristics(new Set());
  };

  const characteristics = {
    ages: ['18-', '18-24', '24-30', '30-36', '36-42', '42-48', '48-54', '54-60', '60-66', '66-72', '72+'],
    genders: ['male', 'female', 'non-binary'],
    personality: ['analytical', 'empathetic', 'adventurous', 'conscientious', 'spontaneous', 'pragmatic', 'idealistic', 'assertive', 'diplomatic', 'introspective'],
    interests: ['technology', 'music', 'visual arts', 'sports', 'literature', 'finance', 'gaming', 'travel', 'culinary', 'environment']
  };

  return (
    <>
      <Head>
        <title>Socaio - AI-Powered Audience Analysis Tool</title>
        <meta name="description" content="AI-powered audience analysis tool" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>

      <div className="header-logo" onClick={goBackToMain}>Socaio</div>
      
      <div className="container">
        <div className={`main-content ${showCharacteristics ? 'split' : ''}`}>
          {!showChat && (
            <div className="welcome-screen">
              <div className="logo">Socaio</div>
              <div className="greeting">How can I help you understand your audience today?</div>
              <div className="query-container">
                <input 
                  type="text" 
                  className="query-input" 
                  placeholder="Enter your test message here..."
                  value={currentQuery}
                  onChange={(e) => setCurrentQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleQuerySubmit()}
                />
                <button 
                  className="submit-btn" 
                  onClick={handleQuerySubmit}
                  disabled={isLoading}
                >
                  {isLoading ? <div className="loading"></div> : '→'}
                </button>
              </div>
            </div>
          )}

          {showChat && (
            <div className="chat-interface active">
              <div className="chat-messages">
                {messages.map((message, index) => (
                  <div key={index} className={`message ${message.sender}`}>
                    <div className="message-content">{message.content}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {showCharacteristics && (
          <div className="characteristics-panel active">
            <div className="panel-header">Audience Characteristics</div>
            
            {showReport ? (
              <div className="report-display">
                <div className="report-header">
                  <h3>📊 Analysis Report</h3>
                  <button 
                    className="back-to-characteristics"
                    onClick={() => setShowReport(false)}
                  >
                    ← Back to Characteristics
                  </button>
                </div>
                <div className="report-content">
                  <div className="report-meta">
                    <div className="meta-item">
                      <strong>News Content:</strong> {currentQuery.length > 100 ? currentQuery.substring(0, 100) + '...' : currentQuery}
                    </div>
                    <div className="meta-item">
                      <strong>Selected Traits:</strong> {Array.from(selectedCharacteristics).join(', ')}
                    </div>
                    <div className="meta-item">
                      <strong>Generated:</strong> {new Date().toLocaleString()}
                    </div>
                  </div>
                  <div dangerouslySetInnerHTML={{ __html: reportContent }} />
                </div>
              </div>
            ) : (
              <div className="characteristics-content">
                {Object.entries(characteristics).map(([category, items]) => (
                  <div key={category} className="characteristics-section">
                    <div className="section-title">
                      {category === 'ages' ? 'Age Groups' : 
                       category === 'genders' ? 'Gender' :
                       category === 'personality' ? 'Personality Traits' : 'Interests'}
                    </div>
                    <div className="characteristic-grid">
                      {items.map(item => (
                        <div
                          key={item}
                          className={`characteristic-item ${selectedCharacteristics.has(item) ? 'selected' : ''}`}
                          onClick={() => toggleCharacteristic(item)}
                        >
                          <div className="characteristic-checkbox"></div>
                          <div className="characteristic-label">
                            {item.charAt(0).toUpperCase() + item.slice(1)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
                
                <button 
                  className="generate-btn"
                  onClick={generateReport}
                  disabled={selectedCharacteristics.size === 0 || isLoading}
                >
                  {isLoading ? 'Generating Report...' : 
                   selectedCharacteristics.size > 0 ? 
                   `Generate Analysis Report (${selectedCharacteristics.size} traits selected)` : 
                   'Generate Analysis Report'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      <style jsx>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: white;
          color: #1f2937;
          overflow-x: hidden;
        }

        .container {
          display: flex;
          height: 100vh;
          transition: all 0.3s ease;
        }

        .header-logo {
          position: fixed;
          top: 20px;
          left: 20px;
          z-index: 100;
          font-size: 24px;
          font-weight: bold;
          color: #6366f1;
          cursor: pointer;
          transition: color 0.2s ease;
          text-decoration: none;
        }

        .header-logo:hover {
          color: #5855eb;
        }

        .main-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          position: relative;
        }

        .main-content.split {
          flex: 1;
        }

        .welcome-screen {
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          height: 100%;
          padding: 40px;
          text-align: center;
        }

        .logo {
          font-size: 32px;
          font-weight: bold;
          color: #6366f1;
          margin-bottom: 20px;
        }

        .greeting {
          font-size: 48px;
          font-weight: 300;
          margin-bottom: 40px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .query-container {
          width: 100%;
          max-width: 600px;
          position: relative;
        }

        .query-input {
          width: 100%;
          padding: 20px 60px 20px 20px;
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 12px;
          color: #1f2937;
          font-size: 16px;
          outline: none;
          transition: all 0.3s ease;
        }

        .query-input:focus {
          border-color: #6366f1;
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .submit-btn {
          position: absolute;
          right: 8px;
          top: 50%;
          transform: translateY(-50%);
          background: #6366f1;
          border: none;
          border-radius: 8px;
          width: 44px;
          height: 44px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
          color: white;
          font-size: 18px;
        }

        .submit-btn:hover {
          background: #5855eb;
        }

        .submit-btn:disabled {
          background: #4b5563;
          cursor: not-allowed;
        }

        .chat-interface {
          display: flex;
          flex-direction: column;
          height: 100%;
          padding: 20px;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 20px 0;
        }

        .message {
          margin-bottom: 24px;
          display: flex;
          align-items: flex-start;
        }

        .message.user {
          justify-content: flex-end;
        }

        .message-content {
          max-width: 70%;
          padding: 16px 20px;
          border-radius: 16px;
          line-height: 1.5;
        }

        .message.user .message-content {
          background: #f3f4f6;
          border: 1px solid #e5e7eb;
          color: #1f2937;
          border-bottom-right-radius: 4px;
        }

        .message.assistant .message-content {
          background: transparent;
          border: none;
          border-bottom-left-radius: 4px;
          padding: 16px 0;
        }

        .characteristics-panel {
          width: 400px;
          background: white;
          border-left: 1px solid #e5e7eb;
          padding: 20px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
        }

        .panel-header {
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 20px;
          color: #1f2937;
        }

        .characteristics-section {
          margin-bottom: 24px;
        }

        .section-title {
          font-size: 14px;
          font-weight: 500;
          color: #6b7280;
          margin-bottom: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .characteristic-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
        }

        .characteristic-item {
          display: flex;
          align-items: center;
          padding: 8px 12px;
          background: #f9fafb;
          border-radius: 8px;
          border: 1px solid #e5e7eb;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .characteristic-item:hover {
          background: #f3f4f6;
          border-color: #6366f1;
        }

        .characteristic-item.selected {
          background: #6366f1;
          border-color: #6366f1;
          color: white;
        }

        .characteristic-checkbox {
          width: 16px;
          height: 16px;
          border: 2px solid #9ca3af;
          border-radius: 3px;
          margin-right: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
        }

        .characteristic-item.selected .characteristic-checkbox {
          background: white;
          border-color: white;
        }

        .characteristic-checkbox::after {
          content: '✓';
          color: #6366f1;
          font-size: 10px;
          font-weight: bold;
          opacity: 0;
          transition: opacity 0.2s ease;
        }

        .characteristic-item.selected .characteristic-checkbox::after {
          opacity: 1;
        }

        .characteristic-label {
          font-size: 13px;
          flex: 1;
        }

        .generate-btn {
          background: #10b981;
          border: none;
          color: white;
          padding: 16px 24px;
          border-radius: 12px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          margin-top: 20px;
          transition: all 0.2s ease;
          width: 100%;
        }

        .generate-btn:hover {
          background: #059669;
        }

        .generate-btn:disabled {
          background: #4b5563;
          cursor: not-allowed;
        }

        .report-display {
          height: 100%;
          overflow-y: auto;
        }

        .report-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          padding-bottom: 15px;
          border-bottom: 2px solid #e5e7eb;
        }

        .report-header h3 {
          font-size: 18px;
          font-weight: 600;
          color: #1f2937;
          margin: 0;
        }

        .back-to-characteristics {
          background: #6b7280;
          color: white;
          border: none;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 12px;
          cursor: pointer;
          transition: background 0.2s ease;
        }

        .back-to-characteristics:hover {
          background: #4b5563;
        }

        .report-content {
          font-size: 14px;
          line-height: 1.6;
          color: #374151;
        }

        .report-meta {
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 15px;
          margin-bottom: 20px;
          font-size: 13px;
        }

        .meta-item {
          margin-bottom: 8px;
        }

        .meta-item:last-child {
          margin-bottom: 0;
        }

        .meta-item strong {
          color: #6b7280;
        }

        .loading {
          display: inline-block;
          width: 12px;
          height: 12px;
          border: 2px solid #4b5563;
          border-radius: 50%;
          border-top-color: #6366f1;
          animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .characteristics-panel {
            width: 100%;
            position: absolute;
            z-index: 15;
            height: 100%;
          }
        }
      `}</style>
    </>
  );
}