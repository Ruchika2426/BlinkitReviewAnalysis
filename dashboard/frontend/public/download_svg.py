import urllib.request

url = 'https://upload.wikimedia.org/wikipedia/commons/2/2f/Blinkit-yellow-rounded.svg'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
with urllib.request.urlopen(req) as response, open('c:\\BlinkitReviewAnalyser\\dashboard\\frontend\\public\\blinkitIcon.svg', 'wb') as out_file:
    data = response.read()
    out_file.write(data)
