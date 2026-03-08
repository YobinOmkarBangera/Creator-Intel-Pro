from textblob import TextBlob
import polars as pl

def analyze_brand_fit(data):
    # 1. Engagement Rate
    total_interact = data['avg_likes'] + data['avg_comments']
    er = (total_interact / data['avg_views']) * 100 if data['avg_views'] > 0 else 0
    
    # 2. Sentiment Analytics
    sentiments = [TextBlob(txt).sentiment.polarity for txt in data['comment_data']['text']]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    
    # 3. Bot Risk
    unique_ratio = len(set(data['comment_data']['text'])) / len(data['comment_data']['text'])
    bot_risk = (1 - unique_ratio) * 100

    # 4. Sentiment Interpretation Insight
    if avg_sentiment > 0.35:
        insight = "🌟 **Exceptional Advocacy:** The audience shows high emotional loyalty. Perfect for premium brand integrations."
    elif avg_sentiment > 0.1:
        insight = "✅ **Constructive Vibe:** Audience interactions are mostly positive, polite, and topically relevant."
    elif avg_sentiment > -0.1:
        insight = "⚖️ **Neutral/Objective:** The audience is primarily factual or critical. Best for niche utility products."
    else:
        insight = "⚠️ **High Friction:** Negative sentiment peaks detected. Suggests controversy or audience dissatisfaction."

    # 5. Verdict
    if er > 4.5 and bot_risk < 15:
        verdict = "💎 PREMIUM PARTNER: High organic engagement."
        status = "Success"
    else:
        verdict = "⚖️ STANDARD: Consistent reach, monitor specific niche fit."
        status = "Warning"

    return {
        "er": round(er, 2),
        "bot_risk": round(bot_risk, 1),
        "sentiment_score": round(avg_sentiment, 2),
        "sentiment_insight": insight,
        "verdict": verdict,
        "status": status,
        "sentiment_list": sentiments
    }