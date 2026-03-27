"""
MoodMatch - Emotion Classifier Training Script
================================================
Trains a Multinomial Naive Bayes model with TF-IDF for emotion classification.

Dataset: emotion-emotion_69k.csv (64k+ conversational examples with 32 emotion labels)
Algorithm: Multinomial Naive Bayes + TF-IDF Vectorization
Expected Accuracy: 68-72%

Usage:
    python train_emotion_model.py

Output:
    - models/ml_models/emotion_classifier.pkl
    - models/ml_models/tfidf_vectorizer.pkl
    - models/ml_models/emotion_label_encoder.pkl
    - models/ml_models/emotion_categories.json
    - models/ml_models/model_metrics.json
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import pickle
import json
import os
from datetime import datetime

# Configuration
DATA_PATH = "emotion-emotion_69k.csv"
OUTPUT_DIR = "models/ml_models"
MIN_SAMPLES_PER_EMOTION = 100
TEST_SIZE = 0.2
RANDOM_STATE = 42

# TF-IDF Configuration
TFIDF_CONFIG = {
    'max_features': 5000,
    'ngram_range': (1, 2),
    'min_df': 2,
    'max_df': 0.95,
    'strip_accents': 'unicode',
    'lowercase': True,
    'stop_words': 'english'
}

# Model Configuration
MODEL_CONFIG = {
    'alpha': 0.1  # Laplace smoothing
}


def load_and_clean_data(filepath):
    """Load and clean the emotion dataset."""
    print("=" * 60)
    print("📥 LOADING DATA")
    print("=" * 60)
    
    df = pd.read_csv(filepath)
    print(f"✅ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Clean data
    df_clean = df[['Situation', 'emotion']].copy()
    df_clean = df_clean.dropna()
    print(f"✅ After dropping nulls: {df_clean.shape[0]} rows")
    
    # Filter malformed emotions (valid emotions should be short)
    df_clean = df_clean[df_clean['emotion'].str.len() < 20]
    print(f"✅ After filtering malformed emotions: {df_clean.shape[0]} rows")
    
    # Get emotion distribution
    emotion_counts = df_clean['emotion'].value_counts()
    print(f"\n📊 Found {len(emotion_counts)} unique emotions")
    
    # Keep only emotions with sufficient samples
    valid_emotions = emotion_counts[emotion_counts >= MIN_SAMPLES_PER_EMOTION].index.tolist()
    df_clean = df_clean[df_clean['emotion'].isin(valid_emotions)]
    
    print(f"✅ After filtering (min {MIN_SAMPLES_PER_EMOTION} samples): {df_clean.shape[0]} rows")
    print(f"✅ Final emotion categories: {len(valid_emotions)}\n")
    
    return df_clean, emotion_counts, valid_emotions


def prepare_data(df_clean):
    """Prepare training and test sets."""
    print("=" * 60)
    print("🔧 PREPARING DATA")
    print("=" * 60)
    
    X = df_clean['Situation'].values
    y = df_clean['emotion'].values
    
    print(f"📊 Total samples: {len(X)}")
    print(f"📊 Emotion categories: {len(set(y))}\n")
    
    # Encode labels
    print("🔧 Encoding emotion labels...")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split data
    print(f"🔧 Splitting train/test ({int((1-TEST_SIZE)*100)}/{int(TEST_SIZE*100)})...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_encoded
    )
    
    print(f"✅ Training set: {len(X_train)} samples")
    print(f"✅ Test set: {len(X_test)} samples\n")
    
    return X_train, X_test, y_train, y_test, label_encoder


def create_features(X_train, X_test):
    """Create TF-IDF features."""
    print("=" * 60)
    print("🔧 FEATURE ENGINEERING")
    print("=" * 60)
    
    print("🔧 Creating TF-IDF features...")
    tfidf = TfidfVectorizer(**TFIDF_CONFIG)
    
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)
    
    print(f"✅ Vocabulary size: {len(tfidf.vocabulary_)}")
    print(f"✅ Feature matrix shape: {X_train_tfidf.shape}\n")
    
    return X_train_tfidf, X_test_tfidf, tfidf


def train_model(X_train_tfidf, y_train):
    """Train Multinomial Naive Bayes model."""
    print("=" * 60)
    print("🤖 TRAINING MODEL")
    print("=" * 60)
    
    print("🤖 Training Multinomial Naive Bayes...")
    model = MultinomialNB(**MODEL_CONFIG)
    model.fit(X_train_tfidf, y_train)
    
    print("✅ Model training complete!\n")
    
    return model


def evaluate_model(model, X_test_tfidf, y_test, label_encoder):
    """Evaluate model performance."""
    print("=" * 60)
    print("📊 MODEL EVALUATION")
    print("=" * 60)
    
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n🎯 ACCURACY: {accuracy:.2%}")
    print(f"🎯 Correct predictions: {(y_test == y_pred).sum()} / {len(y_test)}\n")
    
    # Classification report
    emotion_names = label_encoder.classes_
    report = classification_report(y_test, y_pred, target_names=emotion_names, output_dict=True)
    
    # Show top 10 emotions by sample count
    print("📋 Classification Report (Top 10 emotions):\n")
    top_emotions = sorted([(e, report[e]['support']) for e in emotion_names], 
                          key=lambda x: x[1], reverse=True)[:10]
    
    for emotion, support in top_emotions:
        metrics = report[emotion]
        print(f"{emotion:15s} - Precision: {metrics['precision']:.2f} | "
              f"Recall: {metrics['recall']:.2f} | F1: {metrics['f1-score']:.2f} | "
              f"Samples: {int(support)}")
    
    print()
    
    return accuracy, report, y_pred


def save_models(model, tfidf, label_encoder, emotion_counts, valid_emotions, accuracy, report):
    """Save all model artifacts."""
    print("=" * 60)
    print("💾 SAVING MODEL FILES")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Save model
    model_path = os.path.join(OUTPUT_DIR, 'emotion_classifier.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✅ Model saved: {model_path}")
    
    # Save vectorizer
    vectorizer_path = os.path.join(OUTPUT_DIR, 'tfidf_vectorizer.pkl')
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(tfidf, f)
    print(f"✅ Vectorizer saved: {vectorizer_path}")
    
    # Save label encoder
    encoder_path = os.path.join(OUTPUT_DIR, 'emotion_label_encoder.pkl')
    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    print(f"✅ Label encoder saved: {encoder_path}")
    
    # Save emotion categories
    categories_data = {
        'total_emotions': len(valid_emotions),
        'emotions_list': valid_emotions,
        'samples_per_emotion': {e: int(emotion_counts[e]) for e in valid_emotions}
    }
    categories_path = os.path.join(OUTPUT_DIR, 'emotion_categories.json')
    with open(categories_path, 'w') as f:
        json.dump(categories_data, f, indent=2)
    print(f"✅ Emotion categories saved: {categories_path}")
    
    # Save metrics
    metrics_data = {
        'trained_at': datetime.now().isoformat(),
        'accuracy': float(accuracy),
        'model_type': 'MultinomialNB',
        'vectorizer': 'TfidfVectorizer',
        'vocab_size': len(tfidf.vocabulary_),
        'num_emotions': len(label_encoder.classes_),
        'emotions': label_encoder.classes_.tolist(),
        'classification_report': report,
        'config': {
            'tfidf': TFIDF_CONFIG,
            'model': MODEL_CONFIG,
            'test_size': TEST_SIZE,
            'min_samples_per_emotion': MIN_SAMPLES_PER_EMOTION
        }
    }
    metrics_path = os.path.join(OUTPUT_DIR, 'model_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    print(f"✅ Metrics saved: {metrics_path}")
    
    print(f"\n🎉 All model files saved to: {OUTPUT_DIR}/")


def main():
    """Main training pipeline."""
    print("\n" + "=" * 60)
    print("🚀 MOODMATCH EMOTION CLASSIFIER TRAINING")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    # Load and clean data
    df_clean, emotion_counts, valid_emotions = load_and_clean_data(DATA_PATH)
    
    # Prepare data
    X_train, X_test, y_train, y_test, label_encoder = prepare_data(df_clean)
    
    # Create features
    X_train_tfidf, X_test_tfidf, tfidf = create_features(X_train, X_test)
    
    # Train model
    model = train_model(X_train_tfidf, y_train)
    
    # Evaluate
    accuracy, report, y_pred = evaluate_model(model, X_test_tfidf, y_test, label_encoder)
    
    # Save everything
    save_models(model, tfidf, label_encoder, emotion_counts, valid_emotions, accuracy, report)
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Final Accuracy: {accuracy:.2%}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()