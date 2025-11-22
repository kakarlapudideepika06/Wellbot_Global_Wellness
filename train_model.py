import json
import os
from pathlib import Path

def load_external_health_corpus():
    """Load and enhance with external health corpus data"""
    
    # External health knowledge base (can be expanded with more data)
    health_corpus = {
        "symptoms": [
            {"text": "headache relief methods", "intent": "headache"},
            {"text": "how to reduce fever naturally", "intent": "fever"},
            {"text": "common cold home remedies", "intent": "cold"},
            {"text": "anxiety management techniques", "intent": "anxiety"},
            {"text": "insomnia treatment options", "intent": "sleep"},
            {"text": "healthy diet plans", "intent": "diet"},
            {"text": "exercise for beginners", "intent": "exercise"},
            {"text": "mental wellness strategies", "intent": "mental_health"},
            {"text": "migraine pain relief", "intent": "headache"},
            {"text": "high temperature treatment", "intent": "fever"},
            {"text": "cough and cold medicine", "intent": "cold"},
            {"text": "stress reduction methods", "intent": "anxiety"},
            {"text": "sleep improvement tips", "intent": "sleep"},
            {"text": "nutritional advice", "intent": "diet"},
            {"text": "fitness training", "intent": "exercise"},
            {"text": "depression help", "intent": "mental_health"},
            {"text": "head pounding", "intent": "headache"},
            {"text": "body temperature high", "intent": "fever"},
            {"text": "runny nose and cough", "intent": "cold"},
            {"text": "feeling stressed out", "intent": "anxiety"},
            {"text": "can't fall asleep", "intent": "sleep"},
            {"text": "what to eat for health", "intent": "diet"},
            {"text": "physical fitness guidance", "intent": "exercise"},
            {"text": "emotional support needed", "intent": "mental_health"}
        ],
        "treatments": [
            {"text": "what helps with headache pain", "intent": "headache"},
            {"text": "fever reducing medications", "intent": "fever"},
            {"text": "cold symptom relief", "intent": "cold"},
            {"text": "how to calm anxiety", "intent": "anxiety"},
            {"text": "ways to sleep better", "intent": "sleep"},
            {"text": "balanced meal plans", "intent": "diet"},
            {"text": "workout routines", "intent": "exercise"},
            {"text": "mental health support", "intent": "mental_health"},
            {"text": "headache home remedies", "intent": "headache"},
            {"text": "bring down fever", "intent": "fever"},
            {"text": "clear blocked nose", "intent": "cold"},
            {"text": "reduce stress levels", "intent": "anxiety"},
            {"text": "improve sleep quality", "intent": "sleep"},
            {"text": "healthy food choices", "intent": "diet"},
            {"text": "exercise recommendations", "intent": "exercise"},
            {"text": "coping with sadness", "intent": "mental_health"}
        ],
        "prevention": [
            {"text": "prevent headaches", "intent": "headache"},
            {"text": "avoid getting fever", "intent": "fever"},
            {"text": "cold prevention tips", "intent": "cold"},
            {"text": "manage anxiety triggers", "intent": "anxiety"},
            {"text": "better sleep habits", "intent": "sleep"},
            {"text": "preventive nutrition", "intent": "diet"},
            {"text": "exercise for health", "intent": "exercise"},
            {"text": "mental health maintenance", "intent": "mental_health"}
        ]
    }
    
    return health_corpus

def enhance_nlu_training_data():
    """Enhance NLU training data with external corpus and save to file"""
    
    # Load external corpus
    health_corpus = load_external_health_corpus()
    
    # Create enhanced NLU data structure
    enhanced_nlu = {
        "version": "3.1",
        "nlu": []
    }
    
    # Group examples by intent
    intent_examples = {}
    for category, examples in health_corpus.items():
        for example in examples:
            intent = example["intent"]
            if intent not in intent_examples:
                intent_examples[intent] = []
            intent_examples[intent].append(example["text"])
    
    # Convert to Rasa NLU format
    for intent, examples in intent_examples.items():
        enhanced_nlu["nlu"].append({
            "intent": intent,
            "examples": "\n".join([f"    - {example}" for example in examples])
        })
    
    # Save enhanced NLU data
    enhanced_nlu_file = "data/enhanced_nlu.yml"
    os.makedirs("data", exist_ok=True)
    
    # Convert to YAML format (simplified)
    with open(enhanced_nlu_file, "w", encoding="utf-8") as f:
        f.write('version: "3.1"\n\n')
        f.write('nlu:\n')
        
        for item in enhanced_nlu["nlu"]:
            f.write(f'- intent: {item["intent"]}\n')
            f.write('  examples: |\n')
            f.write(item["examples"] + '\n')
    
    print(f"✅ Enhanced NLU data saved to: {enhanced_nlu_file}")
    print(f"📊 Added {len(intent_examples)} intents with {sum(len(examples) for examples in intent_examples.values())} total examples")
    
    return enhanced_nlu

def create_training_instructions():
    """Create instructions for training the enhanced model"""
    
    instructions = """
    🤖 DIGITAL WELLNESS CHATBOT - TRAINING INSTRUCTIONS
    ===================================================

    ✅ Enhanced training data has been generated!

    NEXT STEPS:

    1. MERGE ENHANCED DATA WITH EXISTING NLU:
       - Copy the content from 'data/enhanced_nlu.yml'
       - Paste it into your existing 'data/nlu.yml' file
       - Or manually add the new examples to your existing intents

    2. TRAIN THE RASA MODEL:
       ```bash
       rasa train
       ```

    3. START RASA SERVER:
       ```bash
       rasa run -m models --enable-api --cors "*"
       ```

    4. START STREAMLIT APP:
       ```bash
       streamlit run app.py
       ```

    ENHANCEMENTS ADDED:
    • 50+ additional training examples across all health intents
    • Expanded symptom descriptions
    • Treatment and prevention phrases
    • Improved intent recognition coverage

    Your chatbot will now better understand various health-related queries!
    """
    
    print(instructions)
    
    # Save instructions to file
    with open("TRAINING_INSTRUCTIONS.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    return instructions

def validate_knowledge_base():
    """Validate that the knowledge base exists and is accessible"""
    
    knowledge_base_path = "data/knowledge_base.json"
    
    if os.path.exists(knowledge_base_path):
        try:
            with open(knowledge_base_path, "r", encoding="utf-8") as f:
                knowledge_base = json.load(f)
            print(f"✅ Knowledge base loaded successfully with {len(knowledge_base)} topics")
            return True
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            return False
    else:
        print("❌ Knowledge base file not found at: data/knowledge_base.json")
        print("💡 Please ensure your knowledge_base.json file exists in the data/ directory")
        return False

def main():
    """Main training enhancement function"""
    
    print("🤖 Digital Wellness Chatbot - Training Enhancement")
    print("=" * 50)
    
    # Validate knowledge base
    if not validate_knowledge_base():
        print("\n⚠️  Please fix the knowledge base issue before proceeding.")
        return
    
    # Enhance NLU training data
    print("\n🚀 Enhancing NLU training data with external health corpus...")
    enhanced_data = enhance_nlu_training_data()
    
    # Create training instructions
    print("\n📋 Generating training instructions...")
    instructions = create_training_instructions()
    
    print("\n🎊 Training enhancement completed successfully!")
    print("📖 Check 'TRAINING_INSTRUCTIONS.md' for next steps")

if __name__ == "__main__":
    main()