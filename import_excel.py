import pandas as pd
import sys

excel_path = r'c:\BlinkitReviewAnalyser\docs\rawdata.xlsx'
csv_path = r'c:\BlinkitReviewAnalyser\data\reviews_raw.csv'

try:
    # Read the excel file with NO headers (since the first row is actual data)
    df_excel = pd.read_excel(excel_path, header=None)
    
    # Map the expected columns based on their index in the Excel file
    # Col 1: Source
    # Col 2: Date
    # Col 3: Text
    # Col 5: URL
    
    df_mapped = pd.DataFrame()
    df_mapped['source'] = df_excel[1]
    df_mapped['date'] = df_excel[2]
    df_mapped['rating'] = '' # This dataset doesn't seem to have a star rating
    df_mapped['text'] = df_excel[3]
    df_mapped['url'] = df_excel[5]
    
    # Append to the CSV
    df_mapped.to_csv(csv_path, mode='a', header=False, index=False)
    print(f"SUCCESS: Appended {len(df_mapped)} rows from {excel_path} to {csv_path}")
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
