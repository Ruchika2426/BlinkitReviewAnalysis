import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import scipy.spatial.distance as dist
from groq import Groq

# Load environment variables
load_dotenv()

def extract_themes():
    """
    Executes Phase 4: AI Theme Discovery Engine.
    Uses Sentence-Transformers to embed and cluster reviews, then calls Groq API to assign canonical themes.
    """
    print(f"[{datetime.now()}] Starting Phase 4: AI Theme Discovery Engine...")
    
    file_path = os.path.join('data', 'reviews_raw.csv')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Ensure Phase 3 has been completed.")
        return
        
    print(f"Loading cleaned dataset: {file_path}")
    df = pd.read_csv(file_path)
    if df.empty:
        print("Error: Dataset is empty.")
        return
        
    print(f"Loaded {len(df)} records for analysis.")
    
    # -------------------------------------------------------------------
    # 1. Semantic Clustering (Local Embeddings)
    # -------------------------------------------------------------------
    print("\n--- 1. Semantic Clustering ---")
    print("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
    # This model runs completely locally and is very fast for sentence embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Generating 384-dimensional mathematical embeddings for all reviews (this may take a moment)...")
    embeddings = model.encode(df['text'].tolist(), show_progress_bar=True)
    
    # K-Means Clustering
    n_clusters = 15
    print(f"Clustering reviews into {n_clusters} semantic themes using KMeans...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    df['cluster_id'] = kmeans.fit_predict(embeddings)
    
    # Find representative reviews for each cluster (the 5 closest points to the centroid)
    print("Identifying the 5 most representative reviews for each cluster...")
    cluster_representatives = {}
    
    for i in range(n_clusters):
        cluster_mask = df['cluster_id'] == i
        cluster_indices = df.index[cluster_mask].tolist()
        cluster_embeddings = embeddings[cluster_indices]
        
        # Calculate distance to the cluster's centroid
        centroid = kmeans.cluster_centers_[i]
        distances = dist.cdist(cluster_embeddings, [centroid], metric='euclidean').flatten()
        
        # Get indices of the 5 closest reviews
        closest_local_indices = distances.argsort()[:5]
        closest_global_indices = [cluster_indices[idx] for idx in closest_local_indices]
        
        cluster_representatives[i] = df.loc[closest_global_indices, 'text'].tolist()
        
    # -------------------------------------------------------------------
    # 2. LLM Theme Extraction (Groq API)
    # -------------------------------------------------------------------
    print("\n--- 2. LLM Theme Extraction (Groq) ---")
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Warning: GROQ_API_KEY not found in .env. Cannot contact Groq API. Please add it!")
        return
        
    client = Groq(api_key=groq_api_key)
    cluster_mapping = {}
    
    for cluster_id, reviews in cluster_representatives.items():
        print(f"Requesting Groq LLM to analyze Cluster {cluster_id}...")
        
        # Format the 5 representative reviews into a bulleted list for the prompt
        reviews_text = "\n".join([f"- {r}" for r in reviews])
        prompt = f"""You are an expert Product Manager analyzing customer feedback for quick commerce apps (Blinkit, Zepto).
Here are 5 highly related customer reviews:

{reviews_text}

Analyze these reviews deeply. Look beyond surface-level complaints and try to identify underlying **shopping habits, category exploration friction, unmet needs, and operational/UX frustrations**.

Provide exactly two things in JSON format:
1. "canonical_theme_name": A short 2-5 word label focusing on user behavior, habits, or systemic UX friction (e.g. "Fresh Produce Trust Issues", "Payment Gateway Friction", "Routine Grocery Restocking", "Language Preference Friction").
2. "summary": A 1-sentence summary explaining the underlying user behavior, unmet need, or friction point.

Return ONLY valid JSON. Do not include markdown formatting or extra text.
Format: {{"canonical_theme_name": "...", "summary": "..."}}
"""
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            response_text = chat_completion.choices[0].message.content
            parsed = json.loads(response_text)
            
            cluster_mapping[cluster_id] = {
                "theme": parsed.get("canonical_theme_name", f"Theme {cluster_id}"),
                "summary": parsed.get("summary", "")
            }
            print(f"  -> Extracted Theme: {cluster_mapping[cluster_id]['theme']}")
            
        except Exception as e:
            print(f"  [!] Failed to analyze cluster {cluster_id} with Groq: {e}")
            cluster_mapping[cluster_id] = {"theme": f"Uncategorized Theme {cluster_id}", "summary": "N/A"}
            
    # -------------------------------------------------------------------
    # 3. Data Merging & Export
    # -------------------------------------------------------------------
    print("\n--- 3. Merging and Exporting Data ---")
    df['theme'] = df['cluster_id'].apply(lambda x: cluster_mapping[x]['theme'])
    df['theme_summary'] = df['cluster_id'].apply(lambda x: cluster_mapping[x]['summary'])
    
    output_path = os.path.join('data', 'themes_raw.json')
    
    # Convert dates to strings for JSON serialization
    df['date'] = df['date'].astype(str)
    
    # Export to JSON format
    records = df.to_dict(orient='records')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=4, ensure_ascii=False)
        
    print(f"\n[{datetime.now()}] Phase 4 complete! {len(df)} records were successfully mapped to {n_clusters} canonical themes and exported to {output_path}")

if __name__ == '__main__':
    extract_themes()
