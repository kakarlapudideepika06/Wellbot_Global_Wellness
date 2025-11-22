import json
import re
import requests
from deep_translator import GoogleTranslator

# Initialize translators
translator_hi = GoogleTranslator(source='auto', target='hi')
translator_en = GoogleTranslator(source='auto', target='en')

def get_rasa_entities(message):
    """Get entities from Rasa NLU"""
    try:
        response = requests.post(
            'http://localhost:5005/model/parse',
            json={"text": message},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: Rasa entities: {data.get('entities', [])}")
            return data.get('entities', [])
        return []
    except Exception as e:
        print(f"Rasa entity extraction error: {e}")
        return []

def process_detected_symptoms(symptoms, original_input):
    """Process symptoms extracted by Rasa"""
    try:
        with open("data/knowledge_base.json", "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)
    except Exception as e:
        return f"⚠️ Unable to load health information. Error: {e}"

    responses = []
    matched_symptoms = []
    
    # Process each symptom found by Rasa
    for symptom in symptoms:
        symptom_lower = symptom.lower()
        matched = False
        
        for topic, data in knowledge_base.items():
            keywords = [topic] + data.get("keywords", [])
            # Check if any keyword matches the symptom
            if any(re.search(r'\b' + re.escape(keyword) + r'\b', symptom_lower) for keyword in keywords if keyword):
                desc = data.get("description", "")
                remedy = data.get("remedy", "")
                prevention = data.get("prevention", "")
                
                response = f"🩺 **{topic.title()}**\n{desc}\n\n"
                response += f"💡 **Advice:** {remedy}\n"
                
                if prevention:
                    response += f"🛡️ **Prevention:** {prevention}\n"
                
                responses.append(response)
                matched_symptoms.append(topic)
                matched = True
                break
        
        if not matched:
            responses.append(f"ℹ️ For '{symptom}', I recommend consulting a healthcare professional for proper diagnosis.")

    # Combine all responses
    if responses:
        if len(responses) > 1:
            final_response = f"🔍 **I found {len(responses)} health concerns:**\n\n" + "\n---\n".join(responses)
        else:
            final_response = responses[0]
    else:
        final_response = "I understand you're not feeling well. Could you describe your symptoms in more detail?"

    # Add disclaimer
    final_response += "\n\n⚠️ **Disclaimer:** This information is for educational purposes only. Please consult a healthcare professional."

    return final_response

def process_with_knowledge_base(original_input):
    """Fallback: Direct knowledge base matching"""
    try:
        translated_input = translator_en.translate(original_input)
        user_input = translated_input.lower()
    except:
        user_input = original_input.lower()

    # Knowledge base matching
    kb_response = ""
    try:
        with open("data/knowledge_base.json", "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)

        matches = []
        for topic, data in knowledge_base.items():
            keywords = [topic] + data.get("keywords", [])
            pattern = r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b'
            if re.search(pattern, user_input, re.IGNORECASE):
                matches.append((topic, data))

        # Build response
        if matches:
            matched_topics = []
            for topic, data in matches:
                desc = data.get("description", "")
                remedy = data.get("remedy", "")
                prevention = data.get("prevention", "")
                
                topic_response = f"🩺 **{topic.title()}**\n{desc}\n\n"
                topic_response += f"💡 **Advice:** {remedy}\n\n"
                
                if prevention:
                    topic_response += f"🛡️ **Prevention:** {prevention}\n\n"
                
                matched_topics.append(topic_response)

            kb_response = "\n".join(matched_topics)
            
            if len(matches) > 1:
                kb_response = f"🔍 **I found {len(matches)} health concerns:**\n\n" + kb_response
            else:
                kb_response = f"🔍 **I found this health concern:**\n\n" + kb_response

    except Exception as e:
        kb_response = "⚠️ Unable to load health information. Please try again later."

    if not kb_response.strip():
        kb_response = "I'm here to help! Could you describe your symptoms a bit more?"

    disclaimer = "\n\n⚠️ **Disclaimer:** This information is for educational purposes only. Please consult a healthcare professional."
    return kb_response.strip() + disclaimer

def detect_language(text):
    """Detect if text is Hindi or English"""
    def contains_hindi(text):
        return any('\u0900' <= ch <= '\u097f' for ch in text)

    def is_roman_hindi(text):
        roman_words = ["mujhe", "bukhar", "sardi", "sir", "dard", "thoda", "hai", "nahi", "jal", "pani", "thakan"]
        return any(word in text.lower() for word in roman_words)

    return "Hindi" if contains_hindi(text) or is_roman_hindi(text) else "English"

def get_response(user_input, target_language="English"):
    """
    Smart Health Chatbot:
    - Uses Rasa for intelligent entity extraction
    - Falls back to keyword matching if Rasa fails
    - Supports multilingual responses
    """

    original_input = user_input.strip()

    # Language detection
    detected_language = detect_language(original_input)

    # Greetings
    greetings = ["hi", "hello", "hey", "namaste", "नमस्ते"]
    if any(word in original_input.lower() for word in greetings):
        response = "Hello! 👋 How can I help you with your health today?"
        return translator_hi.translate(response) if detected_language == "Hindi" else response

    # Emergency detection
    EMERGENCY_KEYWORDS = [
        'heart attack', 'chest pain', 'bleeding', 'unconscious',
        'stroke', 'severe pain', 'emergency', 'सांस नहीं', 'दिल का दौरा'
    ]
    if any(word in original_input.lower() for word in EMERGENCY_KEYWORDS):
        response = "🚨 **Emergency!** Please contact 112/108 or visit the nearest hospital immediately."
        return translator_hi.translate(response) if detected_language == "Hindi" else response

    # Step 1: Try Rasa entity extraction first
    entities = get_rasa_entities(original_input)
    symptoms = [e['value'] for e in entities if e['entity'] == 'symptom']
    
    if symptoms:
        print(f"DEBUG: Rasa extracted symptoms: {symptoms}")
        final_response = process_detected_symptoms(symptoms, original_input)
    else:
        print("DEBUG: No symptoms found by Rasa, using fallback")
        final_response = process_with_knowledge_base(original_input)

    # Translate if needed
    if detected_language == "Hindi" and target_language == "Hindi":
        try:
            final_response = translator_hi.translate(final_response)
        except:
            pass

    return final_response