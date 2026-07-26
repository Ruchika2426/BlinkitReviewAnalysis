import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime

def validate_themes():
    """
    Executes Phase 5 Part 1: Keyword-Based Validation.
    Extracts top keywords from each AI-generated cluster and calculates
    what percentage of total reviews actually contain those exact keywords.
    """
    print(f"[{datetime.now()}] Starting Phase 5: Theme Validation...")
    
    file_path = os.path.join('data', 'themes_raw.json')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Ensure Phase 4 has been completed.")
        return
        
    print(f"Loading AI clustered dataset: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    total_reviews = len(df)
    
    # -------------------------------------------------------------------
    # 1. Keyword-Based Validation
    # -------------------------------------------------------------------
    print("\n--- 1. Keyword-Based Validation ---")
    
    themes = df['theme'].unique()
    validation_results = []
    
    for theme in themes:
        theme_docs = df[df['theme'] == theme]['text'].tolist()
        
        # Use TF-IDF to find the top mathematically significant keywords for this specific theme
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=15)
            tfidf_matrix = vectorizer.fit_transform(theme_docs)
            
            # Sum tfidf scores across all docs in this theme
            summed_tfidf = tfidf_matrix.sum(axis=0)
            words_freq = [(word, summed_tfidf[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
            words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
            
            # Select the top 5 most important keywords
            top_keywords = [w[0] for w in words_freq[:5]] 
            
        except ValueError:
            # Fallback for extremely small or empty clusters
            top_keywords = []
            
        # Scan entire dataset for these keywords to find validation_pct
        if top_keywords:
            def contains_keyword(text):
                text_lower = str(text).lower()
                return any(kw in text_lower for kw in top_keywords)
                
            validation_count = df['text'].apply(contains_keyword).sum()
            validation_pct = (validation_count / total_reviews) * 100
        else:
            validation_pct = 0.0
            
        validation_results.append({
            'Theme': theme,
            'Keywords': top_keywords,
            'Validation_Pct': validation_pct
        })
        
        print(f"Theme: {theme}")
        print(f"  -> Top Keywords: {', '.join(top_keywords)}")
        print(f"  -> Grounded Evidence: {round(validation_pct, 1)}% of all reviews explicitly contain these keywords.\n")
        
    # -------------------------------------------------------------------
    # 2. Aggregation & Ranking
    # -------------------------------------------------------------------
    print("\n--- 2. Aggregation & Ranking ---")
    summary_df = pd.DataFrame(validation_results)
    
    # Calculate Frequency and Source Count directly from the DataFrame
    theme_counts = df['theme'].value_counts().reset_index()
    theme_counts.columns = ['Theme', 'Frequency']
    
    source_counts = df.groupby('theme')['source'].nunique().reset_index()
    source_counts.columns = ['Theme', 'Source_Count']
    
    # Merge metrics
    summary_df = summary_df.merge(theme_counts, on='Theme')
    summary_df = summary_df.merge(source_counts, on='Theme')
    
    # Rank Top 10 by Frequency
    summary_df = summary_df.sort_values(by='Frequency', ascending=False).head(10)
    print("Top 10 Themes Ranked by Frequency:")
    print(summary_df[['Theme', 'Frequency', 'Validation_Pct']])
    
    # -------------------------------------------------------------------
    # 3. Generate Final Outputs
    # -------------------------------------------------------------------
    print("\n--- 3. Generating Final Outputs ---")
    os.makedirs('data', exist_ok=True)
    
    # Export CSV
    csv_path = os.path.join('data', 'themes_summary.csv')
    summary_df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Exported top metrics to {csv_path}")
    
    # Auto-generate PM Presentation Insights
    txt_path = os.path.join('data', 'presentation_insights.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("Blinkit Review Analyser - Executive Insights\n")
        f.write("=============================================\n\n")
        
        for _, row in summary_df.iterrows():
            f.write(f"Theme: {row['Theme']}\n")
            f.write(f"- Frequency: Mentioned in {row['Frequency']} distinct user reviews.\n")
            f.write(f"- Multichannel Presence: Discussed across {row['Source_Count']} different platforms/sources.\n")
            f.write(f"- Grounded Validation: {round(row['Validation_Pct'], 1)}% of all ingested data contains exact keywords defining this pain point ({', '.join(row['Keywords'])}).\n\n")
            
    print(f"Exported human-readable PM report to {txt_path}")
        
    print(f"\n[{datetime.now()}] Phase 5 fully complete! Final outputs generated.")

if __name__ == "__main__":
    validate_themes()
