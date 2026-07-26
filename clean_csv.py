import os

csv_path = r'c:\BlinkitReviewAnalyser\data\reviews_raw.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Filter out empty lines or lines that just contain commas
clean_lines = []
for line in lines:
    stripped = line.strip()
    if stripped and stripped != ',,,,' and stripped.replace(',', '') != '':
        clean_lines.append(line)

with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    f.writelines(clean_lines)

print(f"Cleaned up {len(lines) - len(clean_lines)} empty rows from the CSV.")
