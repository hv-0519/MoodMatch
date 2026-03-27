"""
MoodMatch - Emotion Classifier Test Script
===========================================
Test the trained emotion classifier with sample inputs.

Usage:
    python test_emotion_model.py
"""

import pickle
import json
import os


def load_models():
    """Load trained models."""
    model_dir = "models/ml_models"
    
    with open(os.path.join(model_dir, 'emotion_classifier.pkl'), 'rb') as f:
        model = pickle.load(f)
    
    with open(os.path.join(model_dir, 'tfidf_vectorizer.pkl'), 'rb') as f:
        vectorizer = pickle.load(f)
    
    with open(os.path.join(model_dir, 'emotion_label_encoder.pkl'), 'rb') as f:
        label_encoder = pickle.load(f)
    
    return model, vectorizer, label_encoder


def predict_emotion(text, model, vectorizer, label_encoder, top_n=3):
    """
    Predict emotion from text.
    
    Returns:
        dict with primary_emotion, confidence, and top_predictions
    """
    # Transform text
    text_tfidf = vectorizer.transform([text])
    
    # Predict
    prediction = model.predict(text_tfidf)[0]
    probabilities = model.predict_proba(text_tfidf)[0]
    
    # Get primary emotion
    primary_emotion = label_encoder.inverse_transform([prediction])[0]
    confidence = probabilities[prediction]
    
    # Get top N predictions
    top_indices = probabilities.argsort()[-top_n:][::-1]
    top_predictions = [
        {
            'emotion': label_encoder.inverse_transform([idx])[0],
            'confidence': float(probabilities[idx])
        }
        for idx in top_indices
    ]
    
    return {
        'primary_emotion': primary_emotion,
        'confidence': float(confidence),
        'top_predictions': top_predictions
    }


def run_tests():
    """Run test cases."""
    print("=" * 60)
    print("🧪 TESTING EMOTION CLASSIFIER")
    print("=" * 60)
    
    # Load models
    print("\n📥 Loading models...")
    model, vectorizer, label_encoder = load_models()
    print("✅ Models loaded successfully!\n")
    
    # Test cases
    test_cases = [
        "I just got rejected from my dream job and feel terrible",
        "I can't believe I won the lottery! This is amazing!",
        "I'm so bored, I don't know what to do with myself",
        "I feel stressed out about the upcoming exams",
        "I'm feeling really creative and want to make something",
        "I miss my best friend who moved away",
        "I'm anxious about my presentation tomorrow",
        "I'm so grateful for all the support from my family",
        "I feel lonely even when I'm surrounded by people",
        "I'm angry at my coworker for taking credit for my work",
        "I'm terrified of the upcoming surgery",
        "I'm proud of finishing my first marathon",
        "I'm disappointed that the concert got cancelled",
        "I'm excited about my vacation next week",
        "I feel guilty for forgetting my friend's birthday"
    ]
    
    print("📝 TEST PREDICTIONS:\n")
    print("-" * 60)
    
    for i, text in enumerate(test_cases, 1):
        result = predict_emotion(text, model, vectorizer, label_encoder)
        
        print(f"\n{i}. Input: \"{text}\"")
        print(f"   Primary: {result['primary_emotion'].upper()} ({result['confidence']:.1%})")
        print(f"   Top 3:", end=" ")
        for j, pred in enumerate(result['top_predictions']):
            print(f"{pred['emotion']} ({pred['confidence']:.1%})", end="")
            if j < len(result['top_predictions']) - 1:
                print(", ", end="")
        print()
    
    print("\n" + "-" * 60)
    print("\n✅ Testing complete!")
    print("=" * 60)


def interactive_mode():
    """Interactive testing mode."""
    print("\n" + "=" * 60)
    print("🎮 INTERACTIVE MODE")
    print("=" * 60)
    print("Type your message to detect emotion (or 'quit' to exit)\n")
    
    model, vectorizer, label_encoder = load_models()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        result = predict_emotion(user_input, model, vectorizer, label_encoder)
        
        print(f"\n🎯 Detected Emotion: {result['primary_emotion'].upper()}")
        print(f"📊 Confidence: {result['confidence']:.1%}")
        print(f"📋 Top 3 Predictions:")
        for pred in result['top_predictions']:
            print(f"   - {pred['emotion']}: {pred['confidence']:.1%}")
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        run_tests()
        
        print("\n💡 Tip: Run with --interactive flag for interactive mode:")
        print("   python test_emotion_model.py --interactive\n")