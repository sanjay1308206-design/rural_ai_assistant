"""
app/utils/intent.py
====================
Keyword-based intent classifier. Fast, offline, no model needed.
"""
INTENT_WEATHER = "weather"
INTENT_CROP    = "crop_advice"
INTENT_SOIL    = "soil_advice"
INTENT_SCHEME  = "government_scheme"
INTENT_PEST    = "pest_disease"
INTENT_MARKET  = "market_price"
INTENT_GENERAL = "general"

KEYWORDS = {
    INTENT_WEATHER: ["weather","rain","temperature","forecast","humidity","monsoon","wind","storm","बारिश","मौसम"],
    INTENT_CROP:    ["crop","grow","plant","sow","harvest","seed","yield","cultivation","kharif","rabi","फसल"],
    INTENT_SOIL:    ["soil","fertilizer","compost","nutrient","organic","pH","loam","clay","मिट्टी","उर्वरक"],
    INTENT_SCHEME:  ["scheme","subsidy","government","pm-kisan","loan","insurance","yojana","योजना","सब्सिडी"],
    INTENT_PEST:    ["pest","disease","insect","fungus","rust","blight","spray","pesticide","weed","कीट","रोग"],
    INTENT_MARKET:  ["price","market","msp","mandi","sell","rate","cost","भाव","कीमत"],
}

LABELS = {
    INTENT_WEATHER: "🌦️ Weather Query",   INTENT_CROP:   "🌾 Crop Advice",
    INTENT_SOIL:    "🪱 Soil & Fertilizer", INTENT_SCHEME: "📋 Government Scheme",
    INTENT_PEST:    "🐛 Pest / Disease",    INTENT_MARKET: "💰 Market Prices",
    INTENT_GENERAL: "💬 General Query",
}


def detect_intent(query: str) -> str:
    q = query.lower()
    for intent, words in KEYWORDS.items():
        if any(w in q for w in words):
            return intent
    return INTENT_GENERAL


def get_intent_label(intent: str) -> str:
    return LABELS.get(intent, "💬 General Query")