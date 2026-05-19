from textblob import TextBlob


def analyze_sentiment(text: str) -> dict:
    if not text or not text.strip():
        return {"label": "Neutral", "score": 0.0, "subjectivity": 0.0}

    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "label": label,
        "score": round(polarity, 3),
        "subjectivity": round(subjectivity, 3),
    }


def sentiment_color(label: str) -> str:
    colors = {
        "Positive": "#6B8F71",
        "Negative": "#C0392B",
        "Neutral": "#8D8072",
    }
    return colors.get(label, "#8D8072")


def mood_to_valence(mood: str) -> float:
    valence = {
        "Happy": 1.0,
        "Calm": 0.6,
        "Neutral": 0.0,
        "Stressed": -0.4,
        "Sad": -0.7,
        "Angry": -0.8,
        "Anxious": -0.5,
    }
    return valence.get(mood, 0.0)


def mood_emoji(mood: str) -> str:
    emojis = {
        "Happy": "😊",
        "Calm": "😌",
        "Neutral": "😐",
        "Stressed": "😓",
        "Sad": "😔",
        "Angry": "😠",
        "Anxious": "😰",
    }
    return emojis.get(mood, "")


MOOD_COLORS = {
    "Happy": "#F4D03F",
    "Calm": "#76C7A0",
    "Neutral": "#BDC3C7",
    "Stressed": "#E67E22",
    "Sad": "#85A0C9",
    "Angry": "#E74C3C",
    "Anxious": "#D7BDE2",
}
