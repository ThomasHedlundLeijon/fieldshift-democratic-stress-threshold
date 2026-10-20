"""
swebert_sentiment.py – Djup sentimentanalys med svensk BERT.
Använder en tillgänglig svensk modell från Hugging Face.
"""

import numpy as np
from textblob import TextBlob
import re
import warnings
warnings.filterwarnings('ignore')

# Försök importera transformers
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers ej installerat. Använder TextBlob som fallback.")


class SweBERTSentiment:
    """
    Sentimentanalys med svensk BERT-modell.
    """

    def __init__(self, use_gpu: bool = False):
        # Lista över svenska modeller som faktiskt finns på Hugging Face
        self.models_to_try = [
            # Svenska modeller
            "AI-Sweden-Models/gpt-sw3-1.3b-instruct",  # Svensk GPT
            "sbx/superb-sv-bert",                       # Svensk BERT
            "KBLab/bert-base-swedish-cased",            # Svensk BERT (ej sentiment)
            # Fallback till engelska
            "siebert/sentiment-roberta-large-english",  # Engelska (fungerar)
            "cardiffnlp/twitter-roberta-base-sentiment-latest"  # Twitter-sentiment
        ]

        self.use_gpu = use_gpu and torch.cuda.is_available() if TRANSFORMERS_AVAILABLE else False
        self.loaded = False
        self.model_name_loaded = None

        if TRANSFORMERS_AVAILABLE:
            for model_name in self.models_to_try:
                try:
                    print(f"📥 Försöker ladda modell: {model_name}")

                    # Försök ladda
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

                    if self.use_gpu:
                        self.model = self.model.to('cuda')

                    self.model.eval()

                    self.classifier = pipeline(
                        "sentiment-analysis",
                        model=self.model,
                        tokenizer=self.tokenizer,
                        device=0 if self.use_gpu else -1
                    )

                    self.loaded = True
                    self.model_name_loaded = model_name
                    print(f"✅ Modell laddad: {model_name}")
                    break

                except Exception as e:
                    print(f"⚠️ Kunde inte ladda {model_name}: {str(e)[:100]}")
                    continue

            if not self.loaded:
                print("⚠️ Ingen modell kunde laddas. Använder TextBlob som fallback.")
        else:
            print("ℹ️ Transformers ej installerat. Använder TextBlob som fallback.")

        # Politiska entiteter för kontextanalys
        self.political_context = {
            "regeringen": "höger",
            "oppositionen": "vänster",
            "magdalena andersson": "vänster",
            "ulf kristersson": "höger",
            "jimmie åkesson": "höger",
            "nooshi dadgostar": "vänster",
            "ebba busch": "höger",
            "amanda lind": "vänster",
            "muharrem demirok": "center",
            "johan pehrson": "höger"
        }

    def analyze(self, text: str):
        text = self._clean_text(text)

        if self.loaded and TRANSFORMERS_AVAILABLE:
            try:
                if len(text) > 500:
                    text = text[:500]

                result = self.classifier(text)[0]

                label = result['label'].upper()
                polarity_map = {
                    'POSITIVE': 1.0,
                    'NEUTRAL': 0.0,
                    'NEGATIVE': -1.0
                }

                # Hantera olika etiketter
                if label not in polarity_map:
                    if 'POS' in label or '5' in label:
                        polarity = 1.0
                    elif 'NEG' in label or '1' in label:
                        polarity = -1.0
                    else:
                        polarity = 0.0
                else:
                    polarity = polarity_map.get(label, 0.0)

                return {
                    'label': label,
                    'score': result['score'],
                    'polarity': polarity * result['score']
                }
            except Exception as e:
                return self._textblob_analyze(text)
        else:
            return self._textblob_analyze(text)

    def _textblob_analyze(self, text: str):
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            return {
                'label': 'POSITIVE' if polarity > 0.1 else 'NEGATIVE' if polarity < -0.1 else 'NEUTRAL',
                'score': abs(polarity),
                'polarity': polarity
            }
        except:
            return {'label': 'NEUTRAL', 'score': 0.5, 'polarity': 0.0}

    def analyze_batch(self, texts):
        return [self.analyze(text) for text in texts]

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text


class SweBERTSentimentRobot:
    def __init__(self):
        self.swebert = SweBERTSentiment()
        self.use_swebert = self.swebert.loaded

        if self.use_swebert:
            print(f"✅ SweBERT-robot redo (använder {self.swebert.model_name_loaded})")
        else:
            print("ℹ️ SweBERT-robot redo (använder TextBlob som fallback)")

    def analyze_text(self, text: str) -> float:
        result = self.swebert.analyze(text)
        return result['polarity']

    def analyze_news_batch(self, news_items):
        if not news_items:
            return {"sentiment_score": 0.5, "media_intensity": 0.5}

        texts = []
        for item in news_items[:30]:
            text = item.get('title', '') + ' ' + item.get('text', '')
            texts.append(text)

        results = self.swebert.analyze_batch(texts)
        polarities = [r['polarity'] for r in results]
        avg_polarity = np.mean(polarities) if polarities else 0.0

        sentiment_score = 0.5 + avg_polarity * 0.5
        sentiment_score = max(0.0, min(1.0, sentiment_score))

        media_intensity = min(1.0, len(news_items) / 30)

        return {
            "sentiment_score": sentiment_score,
            "media_intensity": media_intensity,
            "avg_polarity": avg_polarity,
            "article_count": len(news_items),
            "using_swebert": self.use_swebert,
            "model": self.swebert.model_name_loaded if self.use_swebert else "TextBlob"
        }


# ========== TEST ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 SWEBERT SENTIMENTANALYS – TEST")
    print("=" * 60)

    test_texts = [
        "Regeringen gör ett fantastiskt jobb med ekonomin.",
        "Oppositionen har presenterat ett uselt förslag.",
        "Magdalena Andersson höll ett starkt tal i riksdagen.",
        "Ulf Kristerssons politik har misslyckats totalt."
    ]

    robot = SweBERTSentimentRobot()

    print("\n📝 ANALYS AV TEXTER:")
    for text in test_texts:
        result = robot.analyze_text(text)
        emoji = "🟢" if result > 0.2 else "🔴" if result < -0.2 else "🟡"
        print(f"  {emoji} {text[:50]:50s} → {result:+.2f}")

    dummy_news = [{"title": t, "text": ""} for t in test_texts]
    batch_result = robot.analyze_news_batch(dummy_news)
    print(f"\n📊 Sentiment score: {batch_result['sentiment_score']:.3f}")
    print(f"   Använder SweBERT: {batch_result['using_swebert']}")
    print(f"   Modell: {batch_result.get('model', 'Okänd')}")
