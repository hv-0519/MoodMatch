"""
MoodMatch - Emotion Detection Module
=====================================
Integrates ML-based emotion classification with VADER sentiment analysis.

This module provides the predict_emotion_with_vader() function that combines:
1. Multinomial Naive Bayes emotion classifier (32 emotions)
2. VADER sentiment analysis (positive/negative/neutral with intensity)
"""

import pickle
import os

# Global variables for loaded models
_model = None
_vectorizer = None
_label_encoder = None
_models_loaded = False


def load_emotion_models():
    """Load emotion classification models (called once at startup)."""
    global _model, _vectorizer, _label_encoder, _models_loaded
    
    if _models_loaded:
        return True
    
    try:
        model_dir = "models/ml_models"
        
        with open(os.path.join(model_dir, 'emotion_classifier.pkl'), 'rb') as f:
            _model = pickle.load(f)
        
        with open(os.path.join(model_dir, 'tfidf_vectorizer.pkl'), 'rb') as f:
            _vectorizer = pickle.load(f)
        
        with open(os.path.join(model_dir, 'emotion_label_encoder.pkl'), 'rb') as f:
            _label_encoder = pickle.load(f)
        
        _models_loaded = True
        print("✅ Emotion models loaded successfully")
        return True
        
    except Exception as e:
        print(f"⚠️ Could not load emotion models: {e}")
        return False


def predict_emotion(text, top_n=3):
    """
    Predict emotion from text using ML model.
    
    Args:
        text: User input text
        top_n: Number of top predictions to return
    
    Returns:
        dict with:
            - primary_emotion: str (e.g., 'anxious')
            - confidence: float (0-1)
            - top_predictions: list of dicts with emotion and confidence
    """
    if not _models_loaded:
        load_emotion_models()
    
    if not _models_loaded:
        return None
    
    try:
        # Transform text
        text_tfidf = _vectorizer.transform([text])
        
        # Predict
        prediction = _model.predict(text_tfidf)[0]
        probabilities = _model.predict_proba(text_tfidf)[0]
        
        # Get primary emotion
        primary_emotion = _label_encoder.inverse_transform([prediction])[0]
        confidence = float(probabilities[prediction])
        
        # Get top N predictions
        top_indices = probabilities.argsort()[-top_n:][::-1]
        top_predictions = [
            {
                'emotion': _label_encoder.inverse_transform([idx])[0],
                'confidence': float(probabilities[idx])
            }
            for idx in top_indices
        ]
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': confidence,
            'top_predictions': top_predictions
        }
    
    except Exception as e:
        print(f"⚠️ Emotion prediction error: {e}")
        return None


def map_emotion_to_mood(emotion):
    """
    Map 32 emotions to mood categories (positive/negative/neutral).
    
    This allows integration with existing activity recommendation system.
    """
    # Positive emotions
    positive_emotions = {
        'excited', 'proud', 'grateful', 'confident', 'hopeful', 'impressed',
        'joyful', 'prepared', 'content', 'sentimental', 'caring', 'trusting',
        'faithful', 'anticipating', 'surprised'
    }
    
    # Negative emotions
    negative_emotions = {
        'angry', 'sad', 'annoyed', 'lonely', 'afraid', 'terrified', 'guilty',
        'furious', 'disgusted', 'anxious', 'disappointed', 'jealous',
        'devastated', 'embarrassed', 'ashamed', 'apprehensive'
    }
    
    # Neutral emotions
    neutral_emotions = {
        'nostalgic'
    }
    
    emotion_lower = emotion.lower()
    
    if emotion_lower in positive_emotions:
        return 'positive', '😊'
    elif emotion_lower in negative_emotions:
        return 'negative', '😔'
    else:
        return 'neutral', '😐'


def get_emotion_emoji(emotion):
    """Get appropriate emoji for detected emotion."""
    emotion_emojis = {
        'excited': '🤩',
        'happy': '😊',
        'joyful': '😄',
        'grateful': '🙏',
        'proud': '😎',
        'confident': '💪',
        'hopeful': '🌟',
        'impressed': '😮',
        'content': '😌',
        
        'sad': '😢',
        'lonely': '😞',
        'disappointed': '😔',
        'devastated': '💔',
        'nostalgic': '🥲',
        
        'angry': '😠',
        'furious': '😡',
        'annoyed': '😤',
        'disgusted': '🤢',
        
        'afraid': '😨',
        'terrified': '😱',
        'anxious': '😰',
        'apprehensive': '😟',
        
        'embarrassed': '😳',
        'ashamed': '😖',
        'guilty': '😔',
        
        'surprised': '😲',
        'jealous': '😒',
        
        'sentimental': '🥺',
        'caring': '🤗',
        'trusting': '🤝',
        'faithful': '✨',
        'anticipating': '🤔',
        'prepared': '✅'
    }
    
    return emotion_emojis.get(emotion.lower(), '🎭')


def predict_emotion_with_vader(text, vader_scores=None):
    """
    Combined emotion detection: ML model + VADER sentiment.
    
    Args:
        text: User input text
        vader_scores: Optional pre-computed VADER scores dict
    
    Returns:
        dict with comprehensive emotion analysis:
            - emotion: str (detected emotion)
            - emotion_confidence: float
            - emotion_emoji: str
            - mood_category: str (positive/negative/neutral)
            - mood_emoji: str
            - vader_compound: float (-1 to 1)
            - vader_label: str
            - top_emotions: list of alternatives
            - combined_label: str (for display)
    """
    result = {
        'emotion': 'neutral',
        'emotion_confidence': 0.0,
        'emotion_emoji': '😐',
        'mood_category': 'neutral',
        'mood_emoji': '😐',
        'vader_compound': 0.0,
        'vader_label': 'neutral',
        'top_emotions': [],
        'combined_label': 'Neutral'
    }
    
    # Get ML emotion prediction
    emotion_pred = predict_emotion(text, top_n=3)
    
    if emotion_pred:
        result['emotion'] = emotion_pred['primary_emotion']
        result['emotion_confidence'] = emotion_pred['confidence']
        result['emotion_emoji'] = get_emotion_emoji(emotion_pred['primary_emotion'])
        result['top_emotions'] = emotion_pred['top_predictions']
        
        # Map to mood category
        mood_cat, mood_emoji = map_emotion_to_mood(emotion_pred['primary_emotion'])
        result['mood_category'] = mood_cat
        result['mood_emoji'] = mood_emoji
    
    # Add VADER if provided
    if vader_scores:
        compound = vader_scores.get('compound', 0.0)
        result['vader_compound'] = compound
        
        if compound >= 0.2:
            result['vader_label'] = 'positive'
        elif compound <= -0.2:
            result['vader_label'] = 'negative'
        else:
            result['vader_label'] = 'neutral'
    
    # Create combined label
    emotion_str = result['emotion'].capitalize()
    confidence_str = f"{result['emotion_confidence']:.0%}"
    result['combined_label'] = f"{emotion_str} ({confidence_str})"
    
    return result


# Initialize models when module is imported
load_emotion_models()