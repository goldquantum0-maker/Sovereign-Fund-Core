import os
from huggingface_hub import InferenceClient
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

class AmazonIntel:
    """The Spy: Finds institutional flow and sentiment."""
    def __init__(self):
        self.serp_key = os.getenv("SERPAPI_KEY")
        self.hf_client = InferenceClient(token=os.getenv("HUGGINGFACE_TOKEN"))
        self.finbert_model = "ProsusAI/finbert"

    def get_sentiment(self, text):
        try:
            result = self.hf_client.text_classification(text, model=self.finbert_model)
            return result[0]['label'], result[0]['score']
        except:
            return "neutral", 0.0

    def scout_trades(self, regime):
        if "🔴 RISK-OFF" in regime:
            query = "institutional accumulation gold treasury defensive stocks 13F"
        elif "🟢 RISK-ON" in regime:
            query = "institutional accumulation AI tech growth stocks dark pool 13F"
        else:
            query = "top institutional buys blue chip value stocks 13F"

        search = GoogleSearch("Sovereign-Intel", "apiKey", self.serp_key)
        results = search.get_dict()
        snippets = [res['snippet'] for res in results.get('organic_results', [])[:3]]
        
        leads = []
        for text in snippets:
            sentiment, score = self.get_sentiment(text)
            if sentiment == "positive" and score > 0.75:
                leads.append({"evidence": text, "score": score})
        
        return leads if leads else None
