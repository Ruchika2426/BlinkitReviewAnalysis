import csv

data = [
    ["Reddit (r/india)", "2026-07-18 10:00:00.000000", "4.0", "Blinkit is great for last minute printouts, but they really need to improve the quality of fresh produce. Tomatoes were completely squashed.", "https://reddit.com/r/india/comments/123"],
    ["Reddit (r/delhi)", "2026-07-18 11:30:00.000000", "2.0", "Why is Blinkit charging a high surge fee during slight rain? Zepto and Instamart are much cheaper right now. Also their delivery partners seem very stressed.", "https://reddit.com/r/delhi/comments/456"],
    ["Reddit (r/bangalore)", "2026-07-18 12:45:00.000000", "5.0", "Honestly, Blinkit's 10-minute delivery is basically magic. I forgot my charger before a meeting and they delivered one in 8 minutes. Lifesaver.", "https://reddit.com/r/bangalore/comments/789"],
    ["Twitter (X)", "2026-07-18 14:20:00.000000", "1.0", "Absolutely terrible customer service. Received expired milk and the chatbot just closed my ticket automatically without refunding. Never using @letsblinkit again.", "https://twitter.com/user/status/101"],
    ["Twitter (X)", "2026-07-18 15:10:00.000000", "3.0", "Love the convenience of Blinkit, but the UI is getting so cluttered with ads for categories I never buy from. Just let me buy my groceries in peace.", "https://twitter.com/user/status/102"]
]

with open('c:/BlinkitReviewAnalyser/data/reviews_raw.csv', 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(data)
    
print("Successfully appended multi-platform mock reviews to reviews_raw.csv!")
