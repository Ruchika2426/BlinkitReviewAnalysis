"use client";

import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { Database, FileText, BarChart2, Play, AlertCircle, ShoppingBag, RefreshCw } from 'lucide-react';

export default function Dashboard() {
  const [themes, setThemes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasRunAnalysis, setHasRunAnalysis] = useState(false);
  const [analysisResult, setAnalysisResult] = useState("");
  const [loadingStep, setLoadingStep] = useState(0);
  const [executionTime, setExecutionTime] = useState("");
  const [executionTimestamp, setExecutionTimestamp] = useState("");
  const [aiModel, setAiModel] = useState("Groq Llama 3.3");
  const [stats, setStats] = useState({ total_reviews: 0, sources_count: 0, sources_list: [] as string[] });
  const [selectedQuestionFilter, setSelectedQuestionFilter] = useState("All");
  const [isDashboardLoading, setIsDashboardLoading] = useState(false);
  const [showDashboardView, setShowDashboardView] = useState(false);
  const [initialLoadError, setInitialLoadError] = useState("");

  const [customQuestion, setCustomQuestion] = useState("");
  const [isAskingCustom, setIsAskingCustom] = useState(false);
  const [customResult, setCustomResult] = useState<any>(null);
  const [customError, setCustomError] = useState("");

  const loadingSteps = [
    "Fetching App Store Reviews",
    "Loading Google Play Reviews",
    "Processing Reddit Discussions",
    "Reading Community Forums",
    "Combining Social Media Sources",
    "Combining Research Sources"
  ];

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isAnalyzing) {
      interval = setInterval(() => {
        setLoadingStep(prev => (prev < 6 ? prev + 1 : prev));
      }, 1000);
    } else {
      setLoadingStep(0);
    }
    return () => clearInterval(interval);
  }, [isAnalyzing]);

  const handleAskCustomQuestion = async () => {
    if (!customQuestion.trim()) return;
    setIsAskingCustom(true);
    setCustomError("");
    setCustomResult(null);

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE}/api/ask-custom-question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: customQuestion })
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "API Error");
      }

      let parsedResult;
      try {
        const jsonMatch = data.response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          parsedResult = JSON.parse(jsonMatch[0]);
        } else {
          parsedResult = JSON.parse(data.response);
        }
      } catch (e) {
        console.error("Custom JSON parse failed", e);
        throw new Error("Received an invalid response format from the AI.");
      }

      setCustomResult(parsedResult);
      if (data.model) {
        setAiModel(data.model);
      }

      // Auto-scroll after a short delay
      setTimeout(() => {
        const el = document.getElementById("custom-result-panel");
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);

    } catch (err: any) {
      setCustomError(err.message || "Failed to analyze the custom question.");
    } finally {
      setIsAskingCustom(false);
    }
  };

  const researchQuestions = [
    "Why do users repeatedly buy from the same categories?",
    "What prevents users from exploring new categories?",
    "How do users discover products today?",
    "What role do habits play in shopping behavior?",
    "What information do users need before trying a new category?",
    "What frustrations emerge repeatedly?",
    "Which user segments are more likely to experiment?",
    "What unmet needs emerge consistently across discussions?"
  ];

  const handleRunAnalysis = async () => {
    setHasRunAnalysis(true);
    setIsAnalyzing(true);
    setAnalysisResult("");
    setSelectedQuestionFilter("All");

    const prompt = `You are a Senior Product Researcher at Blinkit, a quick-commerce platform in India.
    
    ## GOAL
    Blinkit's north-star metric is: **Increase the % of Monthly Active Customers who purchase from ≥1 new category every month.**
    
    You have a dataset (the review themes context) containing real user reviews with fields like id, channel, text, themes, discovery_role, interview_validation, etc.
    
    ## TASK
    Answer the 8 research questions below. For each question, produce exactly 2 to 3 highly impactful findings.
    
    ## RESEARCH QUESTIONS & THEME MAPPING
    Answer the 8 research questions below. You MUST strictly use the assigned Theme for each question.
    Question 1: Why do users repeatedly buy from the same categories? -> Map to Theme: "Delivery & Reliability"
    Question 2: What prevents users from exploring new categories? -> Map to Theme: "Category Friction"
    Question 3: How do users discover products today? -> Map to Theme: "Reorder Loop & Discovery Friction"
    Question 4: What role do habits play in shopping behavior? -> Map to Theme: "Reorder Loop & Discovery Friction"
    Question 5: What information do users need before trying a new category? -> Map to Theme: "Non-Grocery Trust Gaps"
    Question 6: What frustrations emerge repeatedly? -> Map to Theme: "Non-Grocery Trust Gaps"
    Question 7: Which user segments are more likely to experiment? -> Map to Theme: "Category Friction"
    Question 8: What unmet needs emerge consistently across discussions? -> Map to Theme: "Delivery & Reliability"
    
    ## RULES
    1. Only cite real reviews from the dataset. Use the 'id' field.
    2. Tag single-review findings with "(Single-review finding)".
    3. Tag interview-validated findings with "(Interview-confirmed)", "(Interview-challenged)", or "(New from interviews)".
    4. Prioritize Survey responses as primary evidence.
    5. Exactly 2 to 3 findings per question. No more, no less. Each finding must be distinct.
    6. Write "Why it matters" in terms of the north-star metric.
    
    CRITICAL INSTRUCTION: You MUST output ONLY a valid JSON array of objects. Do not include any markdown formatting or explanations outside the JSON array.
    
    The JSON array must follow this exact structure:
    [
      {
        "emoji": "🛒",
        "category": "[Theme Title from the data]",
        "questionNumber": "Question 1",
        "questionText": "Why do users repeatedly buy from the same categories?",
        "insightHeadline": "[One-line headline summary]",
        "findings": [
          {
            "findingNumber": "Finding 1",
            "observation": "[Clear statement.]",
            "evidence": "Review [id] [[channel]]: \\"[Exact quote]\\"",
            "impact": "[1-2 sentences impact]"
          }
        ]
      }
    ]
    
    CRITICAL JSON ESCAPING RULES:
    1. Escape any internal double quotes with a backslash (e.g., \\").
    2. Do NOT include unescaped newlines inside strings.
    3. Ensure there are no trailing commas.
    
    Ensure the output is strictly parseable JSON.`;

    const start = Date.now();
    try {
      // Artificial delay for UX: Let the 6-step loading animation play out
      await new Promise(resolve => setTimeout(resolve, 6500));

      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE}/api/ask-groq`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "API Error");
      }

      let parsedResult = [];
      try {
        const jsonMatch = data.response.match(/\[[\s\S]*\]/);
        if (jsonMatch) {
          try {
            parsedResult = JSON.parse(jsonMatch[0]);
          } catch (e) {
            throw new Error("Truncated within brackets");
          }
        } else {
          throw new Error("No closing bracket found");
        }
      } catch (e) {
        console.warn("JSON parse failed. Attempting progressive truncation repair...");
        let validStr = data.response;
        const startIdx = validStr.indexOf('[');

        if (startIdx !== -1) {
          validStr = validStr.substring(startIdx);
          let endIdx = validStr.lastIndexOf('}');
          let repaired = false;

          while (endIdx !== -1) {
            let testStr = validStr.substring(0, endIdx + 1) + ']';
            try {
              parsedResult = JSON.parse(testStr);
              console.log("Successfully repaired truncated JSON array!");
              repaired = true;
              break;
            } catch (err) {
              endIdx = validStr.lastIndexOf('}', endIdx - 1);
            }
          }

          if (!repaired) {
            console.error("Could not repair JSON", e);
            throw new Error("Data was too heavily truncated to repair.");
          }
        } else {
          throw new Error("No JSON array start found.");
        }
      }

      setAnalysisResult(parsedResult);
      if (data.model) {
        setAiModel(data.model);
      }

      const end = Date.now();
      setExecutionTime(((end - start) / 1000).toFixed(1) + "s");
      setExecutionTimestamp(new Date().toLocaleString());
    } catch (error: any) {
      console.error('Analysis failed:', error);
      setAnalysisResult(`Analysis failed: ${error.message}`);
    } finally {
      setIsAnalyzing(false);
      setTimeout(() => {
        const resultsHeader = document.getElementById('results-header');
        if (resultsHeader) {
          const y = resultsHeader.getBoundingClientRect().top + window.scrollY - 30;
          window.scrollTo({ top: y, behavior: 'smooth' });
        }
      }, 150);
    }
  };

  const handleExportPDF = () => {
    // We use window.print() here because some browsers (like Chrome) with Adobe extensions 
    // will violently intercept ANY downloaded .pdf blob and open it in a restricted viewer.
    // window.print() opens the native OS/browser print dialog, which perfectly formats 
    // the page using our @media print CSS and offers a native "Save as PDF" button 
    // that Adobe cannot block.
    window.print();
  };

  const handleExportMarkdown = () => {
    if (!analysisResult) return;
    const blob = new Blob([analysisResult], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Blinkit-Review-Analysis.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const [themesRes, statsRes] = await Promise.all([
          fetch(`${API_BASE}/api/themes`),
          fetch(`${API_BASE}/api/stats`)
        ]);

        if (themesRes.ok) {
          const themesData = await themesRes.json();
          setThemes(themesData);
        } else {
          setInitialLoadError(`API Error: /api/themes returned ${themesRes.status}`);
        }

        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        } else {
          if (!initialLoadError) setInitialLoadError(`API Error: /api/stats returned ${statsRes.status}`);
        }
      } catch (error: any) {
        console.error("Error fetching data:", error);
        setInitialLoadError("Failed to connect to backend. Please check NEXT_PUBLIC_API_URL in production.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="container" style={{ textAlign: 'center', marginTop: '100px' }}>Loading Blinkit AI Engine...</div>;
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Nav */}
      <div className="top-nav">
        <div className="nav-left" style={{ display: 'flex', alignItems: 'center' }}>
          <img src="/blinkitIcon.svg" alt="Blinkit Icon" style={{ height: '32px', marginRight: '8px', borderRadius: '4px' }} />
          <h1 style={{ color: 'var(--text-primary)', fontSize: '0.95rem', fontWeight: 700, margin: 0, letterSpacing: '-0.2px' }}>
            Review Analysis Engine
          </h1>
        </div>
        <div className="nav-right-pill">
          AI-Powered · {stats.total_reviews ? stats.total_reviews.toLocaleString() : '1,917'}+ Reviews
        </div>
      </div>

      {initialLoadError && (
        <div style={{ backgroundColor: '#EF4444', color: 'white', padding: '12px', textAlign: 'center', fontWeight: 'bold' }}>
          ⚠️ Dashboard Data Failed to Load: {initialLoadError}
        </div>
      )}

      <div className="container">
        <div className="header">
          <div className="eyebrow">Lexicon + LLM classification · 3 research loops</div>
          <h1>
            Why do users struggle to <br />
            <span className="highlight-yellow">explo</span><span style={{ color: 'var(--blinkit-green)' }}>re</span> new categories?
          </h1>
          <p className="subtitle">
            This AI system analyzes real user feedback from 10 sources and extracts the root causes of new category discovery failure using Groq AI.
          </p>
        </div>

        {/* Source Chips */}
        <div className="sources-section">
          <div className="source-pills-row">
            <div className="source-pill" style={{ color: 'var(--text-secondary)' }}>📱 Apple App Store</div>
            <div className="source-pill" style={{ color: 'var(--text-secondary)' }}>⭐ Community forums</div>
            <div className="source-pill" style={{ color: 'var(--text-secondary)' }}>🤖 Google Play Store</div>
            <div className="source-pill" style={{ color: 'var(--text-secondary)' }}>📝 Product reviews</div>
            <div className="source-pill" style={{ color: 'var(--text-secondary)' }}>🛒 Quick-commerce discussions</div>
            <div style={{ flexBasis: '100%', height: 0 }}></div>
            <div className="source-pill" style={{ color: 'var(--text-secondary)' }}>💬 Reddit</div>
            <div className="source-pill" style={{ color: 'var(--text-secondary)' }}>🌐 Social media</div>
            <div className="source-pill" style={{ color: 'var(--text-secondary)' }}>📊 Survey</div>
            <div className="source-pill" style={{ color: 'var(--text-secondary)' }}>🐦 Twitter (X)</div>
            <div className="source-pill" style={{ color: 'var(--text-secondary)' }}>▶️ YouTube</div>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="stats-bar">
          <div className="stat-card">
            <div className="stat-number">{stats.total_reviews ? stats.total_reviews.toLocaleString() : '1,917'}+</div>
            <div className="stat-label">Real reviews analyzed</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">10</div>
            <div className="stat-label">Data sources</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">8</div>
            <div className="stat-label">Research questions answered</div>
          </div>
        </div>





        {/* CTA Button */}
        <div className="cta-container" style={{ marginBottom: '50px', textAlign: 'center' }}>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', justifyContent: 'center', width: '100%', maxWidth: '600px', margin: '0 auto' }}>
            <button id="main-run-btn" className="run-btn" style={{ flex: '1 1 250px' }} onClick={() => {
              setShowDashboardView(false);
              handleRunAnalysis();
            }} disabled={isAnalyzing || isDashboardLoading}>
              <Play fill="currentColor" size={20} /> {isAnalyzing ? 'Analyzing...' : `Analyze ${stats.total_reviews ? stats.total_reviews.toLocaleString() : '1,917'} Reviews →`}
            </button>
            <button className="run-btn" style={{ flex: '1 1 250px' }} disabled={isAnalyzing || isDashboardLoading} onClick={async () => {
              setIsDashboardLoading(true);
              await new Promise(resolve => setTimeout(resolve, 300));
              setShowDashboardView(true);
              setIsDashboardLoading(false);
              setTimeout(() => {
                const dashboardHeader = document.getElementById('dashboard-container');
                if (dashboardHeader) {
                  const y = dashboardHeader.getBoundingClientRect().top + window.scrollY - 30;
                  window.scrollTo({ top: y, behavior: 'smooth' });
                }
              }, 100);
            }}>
              <BarChart2 size={20} /> {isDashboardLoading ? 'Loading...' : 'View Dashboard'}
            </button>
          </div>
        </div>

        <div style={{ display: showDashboardView ? 'none' : 'block' }}>
          {/* Research Questions Grid */}
          {!isAnalyzing && (
            <div style={{ marginBottom: '50px' }}>
              <div className="questions-header">8 RESEARCH QUESTIONS BEING ANSWERED</div>
              <div className="questions-grid">
                {researchQuestions.map((q, idx) => {
                  const isSelected = selectedQuestionFilter === q;
                  const isFaded = hasRunAnalysis && selectedQuestionFilter !== "All" && !isSelected;

                  return (
                    <div
                      key={idx}
                      className="question-box"
                      onClick={() => {
                        if (hasRunAnalysis) {
                          setSelectedQuestionFilter(isSelected ? "All" : q);
                          setCustomResult(null); // Hide AI Findings panel when clicking a predefined question
                          setCustomQuestion(""); // Clear out the input text as well
                          setTimeout(() => {
                            document.getElementById('analysis-results-panel')?.scrollIntoView({ behavior: 'smooth' });
                          }, 100);
                        }
                      }}
                      style={{
                        cursor: hasRunAnalysis ? 'pointer' : 'default',
                        opacity: isFaded ? 0.5 : 1,
                        border: isSelected ? '2px solid var(--blinkit-green)' : '1px solid var(--border-color)',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      <span className="question-number">Q{idx + 1}</span>
                      <p className="question-text">{q}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}


          {/* AI Analysis Result Panel */}
          {hasRunAnalysis && (
            <div id="analysis-results-panel" style={{ marginTop: '20px', marginBottom: '40px' }}>
              {isAnalyzing ? (
                <div className="analysis-result-panel" style={{ padding: '60px', display: 'flex', flexDirection: 'column', alignItems: 'center', maxWidth: '600px', margin: '0 auto' }}>
                  <h2 style={{ color: 'var(--text-primary)', margin: 0, fontSize: '1.4rem' }}>Running AI thematic analysis</h2>
                  <p style={{ color: 'var(--text-secondary)', marginTop: '8px', marginBottom: '40px' }}>Please wait while the system processes your request</p>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '100%', maxWidth: '400px' }}>
                    {loadingSteps.map((step, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'center', color: loadingStep > idx ? 'var(--text-primary)' : 'transparent', transition: 'color 0.3s ease' }}>
                        <span style={{ color: 'var(--blinkit-green)', marginRight: '12px', opacity: loadingStep > idx ? 1 : 0 }}>✓</span>
                        <span style={{ fontSize: '1rem', fontWeight: 500, opacity: loadingStep > idx ? 1 : 0 }}>{step}</span>
                      </div>
                    ))}

                    {loadingStep >= 6 && (
                      <>
                        <div style={{ textAlign: 'center', color: 'var(--text-secondary)', margin: '10px 0' }}>↓</div>
                        <div style={{ display: 'flex', alignItems: 'center', color: 'var(--blinkit-green)' }}>
                          <span className="spinner" style={{ marginRight: '12px' }}></span>
                          <span style={{ fontSize: '1rem', fontWeight: 500 }}>Running AI thematic analysis...</span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              ) : (
                analysisResult && (
                  <>
                    <div style={{ marginBottom: '30px' }}>
                      <h2 id="results-header" style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 8px 0', letterSpacing: '-0.5px', color: 'var(--text-primary)' }}>Analysis Results</h2>
                      <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '1.1rem' }}>
                        Structured insights across eight product research questions
                      </p>

                      <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', marginTop: '30px', marginBottom: '25px' }}>
                        <div className="result-metric-card" style={{ flex: '1 1 120px', minWidth: '0', padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '1px', marginBottom: '8px' }}>REVIEWS ANALYZED</div>
                          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--blinkit-green)' }}>{stats.total_reviews > 0 ? stats.total_reviews.toLocaleString() + '+' : '...'}</div>
                        </div>
                        <div className="result-metric-card" style={{ flex: '1 1 120px', minWidth: '0', padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '1px', marginBottom: '8px' }}>DATA SOURCES</div>
                          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>{stats.sources_count > 0 ? stats.sources_count + ' platforms' : '...'}</div>
                        </div>
                        <div className="result-metric-card" style={{ flex: '1 1 120px', minWidth: '0', padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '1px', marginBottom: '8px' }}>AI MODEL</div>
                          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                            {aiModel === 'openai/gpt-oss-120b' ? 'Groq GPT-OSS 120b' :
                              aiModel === 'llama-3.3-70b-versatile' ? 'Groq Llama 3.3' :
                                aiModel}
                          </div>
                        </div>
                        <div className="result-metric-card" style={{ flex: '1 1 120px', minWidth: '0', padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '1px', marginBottom: '8px' }}>EXECUTION TIMESTAMP</div>
                          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.4 }}>{executionTimestamp}<br />{executionTime}</div>
                        </div>
                        <div className="result-metric-card" style={{ flex: '1 1 120px', minWidth: '0', padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '1px', marginBottom: '8px' }}>RESEARCH CONFIDENCE</div>
                          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--blinkit-green)' }}>High</div>
                        </div>
                      </div>

                      <div style={{ display: 'flex', gap: '12px' }}>
                        <button onClick={handleExportMarkdown} style={{ padding: '8px 16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '50px', color: 'var(--text-primary)', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', transition: 'border 0.2s' }} onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--blinkit-green)'} onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}>
                          <span style={{ fontSize: '1.1rem', color: 'var(--blinkit-yellow)' }}>↓</span> Export Markdown
                        </button>
                        <button onClick={handleExportPDF} style={{ padding: '8px 16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '50px', color: 'var(--text-primary)', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', transition: 'border 0.2s' }} onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--blinkit-green)'} onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}>
                          <span style={{ fontSize: '1.1rem', color: 'var(--blinkit-yellow)' }}>↓</span> Export PDF
                        </button>
                      </div>
                    </div>

                    {/* AI Question & Insight Analysis Panel */}
                    <div style={{ marginBottom: '40px' }}>
                      <div style={{ display: 'flex', gap: '12px', alignItems: 'center', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '10px 10px 10px 20px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
                        <input
                          type="text"
                          value={customQuestion}
                          onChange={(e) => setCustomQuestion(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' && !isAskingCustom && customQuestion.trim()) {
                              handleAskCustomQuestion();
                            }
                          }}
                          placeholder="Ask a custom question (e.g. why users buy dog food or cosmetics)..."
                          style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent', color: 'var(--text-primary)', fontSize: '1rem' }}
                        />
                        <button
                          onClick={handleAskCustomQuestion}
                          disabled={isAskingCustom || !customQuestion.trim()}
                          style={{
                            backgroundColor: 'var(--blinkit-yellow)',
                            color: '#000',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '10px 24px',
                            fontWeight: 700,
                            cursor: (isAskingCustom || !customQuestion.trim()) ? 'not-allowed' : 'pointer',
                            opacity: (isAskingCustom || !customQuestion.trim()) ? 0.6 : 1
                          }}
                        >
                          {isAskingCustom ? 'Analyzing...' : 'Ask AI'}
                        </button>
                      </div>

                      {customError && (
                        <div style={{ marginTop: '16px', color: '#EF4444', fontSize: '0.9rem', padding: '12px', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>
                          {customError}
                        </div>
                      )}

                      {customResult && (
                        <div id="custom-result-panel" style={{ marginTop: '24px', borderTop: '1px solid var(--border-color)', paddingTop: '24px' }}>
                          {customResult.outOfScope ? (
                            <div style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', lineHeight: 1.6, padding: '20px', backgroundColor: 'var(--card-bg)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                              {customResult.message}
                            </div>
                          ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                              <h3 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.2rem', fontWeight: 800 }}>AI Findings</h3>
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                                {customResult.findings?.map((f: any, j: number) => (
                                  <div key={j} style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '20px', backgroundColor: 'var(--card-bg)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                                    <div style={{ color: 'var(--text-primary)', fontSize: '1.05rem', fontWeight: 800, marginBottom: '4px' }}>
                                      {f.findingNumber}
                                    </div>
                                    <div style={{ fontSize: '0.95rem', lineHeight: '1.6' }}>
                                      <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Observation: </span>
                                      <span style={{ color: 'var(--text-secondary)' }}>{f.observation}</span>
                                    </div>
                                    <div style={{ fontSize: '0.95rem', lineHeight: '1.6' }}>
                                      <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Supporting evidence: </span>
                                      <span style={{ color: 'var(--text-secondary)' }}>{f.evidence}</span>
                                    </div>
                                    <div style={{ fontSize: '0.95rem', lineHeight: '1.6' }}>
                                      <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Why it matters: </span>
                                      <span style={{ color: 'var(--text-secondary)' }}>{f.impact}</span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    {/* AI Output (Hidden when showing Custom Findings) */}
                    {(!customResult || customResult.outOfScope) && (
                      <div style={{ lineHeight: '1.6' }}>
                        {Array.isArray(analysisResult) ? (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

                            {analysisResult
                              .filter((theme: any) => {
                                if (selectedQuestionFilter === "All") return true;
                                const selectedIndex = researchQuestions.indexOf(selectedQuestionFilter);

                                return (
                                  (theme.questionText && theme.questionText.includes(selectedQuestionFilter.replace(/\?$/, ''))) ||
                                  (theme.questionText && selectedQuestionFilter.includes(theme.questionText.replace(/\?$/, ''))) ||
                                  (theme.questionNumber && theme.questionNumber.includes(String(selectedIndex + 1))) ||
                                  theme.questionText === selectedQuestionFilter
                                );
                              })
                              .map((theme, i) => (
                                <div key={i} style={{
                                  backgroundColor: 'var(--card-bg)',
                                  border: '1px solid var(--border-color)',
                                  borderRadius: '12px',
                                  padding: '24px',
                                  color: 'var(--text-primary)',
                                  fontFamily: 'system-ui, -apple-system, sans-serif'
                                }}>
                                  <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start', marginBottom: '24px' }}>
                                    <div style={{
                                      backgroundColor: 'rgba(245, 197, 24, 0.1)',
                                      borderRadius: '8px',
                                      width: '40px',
                                      height: '40px',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      fontSize: '1.2rem',
                                      flexShrink: 0
                                    }}>
                                      {theme.emoji}
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                                      <div style={{ color: 'var(--blinkit-green)', fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                                        {theme.category}
                                      </div>
                                      <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginTop: '2px' }}>
                                        {theme.questionNumber}
                                      </div>
                                      <div style={{ color: 'var(--text-primary)', fontSize: '1.1rem', fontWeight: 700, marginTop: '4px' }}>
                                        {theme.questionText}
                                      </div>
                                      {theme.insightHeadline && (
                                        <div style={{ color: 'var(--text-tertiary)', fontSize: '0.95rem', fontStyle: 'italic', marginTop: '6px' }}>
                                          {theme.insightHeadline}
                                        </div>
                                      )}
                                    </div>
                                  </div>

                                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                                    {theme.findings.map((f: any, j: number) => (
                                      <div key={j} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                        <div style={{ color: 'var(--text-primary)', fontSize: '0.95rem', fontWeight: 700 }}>
                                          {f.findingNumber}
                                        </div>
                                        <div style={{ fontSize: '0.9rem', lineHeight: '1.6' }}>
                                          <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Observation: </span>
                                          <span style={{ color: '#D1D5DB' }}>{f.observation}</span>
                                        </div>
                                        <div style={{ fontSize: '0.9rem', lineHeight: '1.6' }}>
                                          <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Supporting evidence: </span>
                                          <span style={{ color: '#D1D5DB' }}>{f.evidence}</span>
                                        </div>
                                        <div style={{ fontSize: '0.9rem', lineHeight: '1.6' }}>
                                          <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Why it matters: </span>
                                          <span style={{ color: '#D1D5DB' }}>{f.impact}</span>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              ))}
                          </div>
                        ) : (
                          <div style={{ whiteSpace: 'pre-wrap', color: '#374151', fontFamily: 'monospace', padding: '20px', background: '#f3f4f6', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            {String(analysisResult)}
                          </div>
                        )}
                      </div>
                    )}


                  </>
                )
              )}
            </div>
          )}

          {/* Refresh Button at the bottom (inline left) */}
          {hasRunAnalysis && !isAnalyzing && analysisResult && (
            <div style={{ marginTop: '20px', marginBottom: '60px', padding: '0 20px' }}>
              <button
                onClick={() => {
                  handleRunAnalysis();
                  setTimeout(() => {
                    const btn = document.getElementById('main-run-btn');
                    if (btn) {
                      const y = btn.getBoundingClientRect().top + window.scrollY - 80;
                      window.scrollTo({ top: y, behavior: 'smooth' });
                    }
                  }, 50);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 20px',
                  backgroundColor: 'transparent',
                  color: 'var(--text-secondary)',
                  border: '1px solid var(--text-tertiary)',
                  borderRadius: '50px',
                  cursor: 'pointer',
                  fontWeight: 500,
                  fontSize: '0.95rem',
                  transition: 'background-color 0.2s ease, color 0.2s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--card-hover)';
                  e.currentTarget.style.color = 'var(--text-primary)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }}
              >
                <RefreshCw size={16} />
                Run again
              </button>
            </div>
          )}
        </div>

        {/* Semantic Clusters Dashboard View */}
        {showDashboardView && (
          <div id="dashboard-container">
            <div style={{ display: 'flex', gap: '15px', flexWrap: 'nowrap', marginTop: '10px', marginBottom: '25px' }}>
              <div className="result-metric-card" style={{ flex: 1, minWidth: '0', padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '1px', marginBottom: '8px' }}>REVIEWS ANALYZED</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--blinkit-green)' }}>{stats.total_reviews > 0 ? stats.total_reviews.toLocaleString() + '+' : '...'}</div>
              </div>
              <div className="result-metric-card" style={{ flex: 1, minWidth: '0', padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '1px', marginBottom: '8px' }}>DATA SOURCES</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>{stats.sources_count > 0 ? stats.sources_count + ' platforms' : '...'}</div>
              </div>
              <div className="result-metric-card" style={{ flex: 1, minWidth: '0', padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '1px', marginBottom: '8px' }}>AI MODEL</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  {aiModel === 'openai/gpt-oss-120b' ? 'Groq GPT-OSS 120b' :
                    aiModel === 'llama-3.3-70b-versatile' ? 'Groq Llama 3.3' :
                      aiModel}
                </div>
              </div>
              <div className="result-metric-card" style={{ flex: 1, minWidth: '0', padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '1px', marginBottom: '8px' }}>EXECUTION TIMESTAMP</div>
                <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.4 }}>{executionTimestamp || 'N/A'}<br />{executionTime || 'N/A'}</div>
              </div>
              <div className="result-metric-card" style={{ flex: 1, minWidth: '0', padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '1px', marginBottom: '8px' }}>RESEARCH CONFIDENCE</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--blinkit-green)' }}>High</div>
              </div>
            </div>

            <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '30px', marginBottom: '40px' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 800, margin: '0 0 10px 0', color: 'var(--text-primary)' }}>Top Pain Points (Semantic Clusters)</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '30px', lineHeight: 1.5 }}>
                Two forces suppress category exploration: habit loops that keep users on autopilot, and trust gaps in unfamiliar categories — freshness, authenticity, and hygiene doubts that make trying a new category feel risky.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {[...themes].sort((a, b) => b.Frequency - a.Frequency).map((theme, idx) => {
                  const percentage = stats.total_reviews ? ((theme.Frequency / stats.total_reviews) * 100).toFixed(2) : (theme.Validation_Pct).toFixed(2);

                  const getThemeTag = (themeName: string) => {
                    const name = themeName.toLowerCase();
                    if (name.includes('habit') || name.includes('routine')) return { label: 'HABIT LOOP', color: 'var(--blinkit-yellow)', bg: 'rgba(245, 197, 24, 0.1)', border: 'rgba(245, 197, 24, 0.5)' };
                    if (name.includes('trust') || name.includes('reliability') && name.includes('emergencies')) return { label: 'TRUST GAP', color: '#f43f5e', bg: 'rgba(244, 63, 94, 0.1)', border: 'rgba(244, 63, 94, 0.5)' };
                    if (name.includes('payment') || name.includes('refund')) return { label: 'FINANCIAL FRICTION', color: '#f43f5e', bg: 'rgba(244, 63, 94, 0.1)', border: 'rgba(244, 63, 94, 0.5)' };
                    if (name.includes('speed') || name.includes('delivery')) return { label: 'OPERATIONAL', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.1)', border: 'rgba(59, 130, 246, 0.5)' };
                    if (name.includes('exploration') || name.includes('word-of-mouth') || name.includes('discovery')) return { label: 'DISCOVERY DRIVER', color: '#a855f7', bg: 'rgba(168, 85, 247, 0.1)', border: 'rgba(168, 85, 247, 0.5)' };
                    return { label: 'GENERAL FRICTION', color: 'var(--text-secondary)', bg: 'transparent', border: 'var(--border-color)' };
                  };

                  const tag = getThemeTag(theme.Theme);

                  return (
                    <div key={idx} style={{ border: '1px solid var(--border-color)', borderRadius: '8px', padding: '20px', background: 'var(--bg-color)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '10px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                          <span style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--text-primary)' }}>
                            {theme.Theme === 'Habit & Routine Formation' ? 'Habitual reorder loop & Poor Discovery' :
                              theme.Theme === 'Payment & Refund Anxiety' ? 'Payment & Transaction Issues' :
                                theme.Theme}
                          </span>
                          <span style={{
                            fontSize: '0.65rem',
                            fontWeight: 800,
                            padding: '4px 10px',
                            borderRadius: '50px',
                            border: tag.border,
                            color: tag.color,
                            backgroundColor: tag.bg,
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            whiteSpace: 'nowrap'
                          }}>
                            {tag.label}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                          {theme.Frequency} items <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>({percentage}%)</span>
                        </div>
                      </div>
                      <div style={{ height: '8px', width: '100%', backgroundColor: 'var(--border-color)', borderRadius: '50px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${percentage}%`, backgroundColor: 'var(--blinkit-yellow)', borderRadius: '50px' }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
        {/* Universal Footer */}
        <div className="footer-line" style={{ padding: '40px 20px', textAlign: 'center', marginTop: 'auto' }}>
          Built with Groq GPT-OSS 120b API · Validated against primary research · Growth Team · July 2026
        </div>
      </div>
    </div>
  );
}
