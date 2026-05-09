import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from django.conf import settings
from categories.models import Category
from products.models import Product

class CategoryClassifier:
    def __init__(self):
        self.model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'category_classifier.pkl')
        self.vectorizer_path = os.path.join(settings.BASE_DIR, 'ml_models', 'vectorizer.pkl')
        self.pipeline = None
        self.load_or_train()
    
    def load_or_train(self):
        """মডেল লোড করো, না থাকলে ট্রেইন করো"""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            # Load existing model
            self.pipeline = joblib.load(self.model_path)
            print("✅ ML Model loaded successfully")
        else:
            # Train new model
            self.train()
    
    def train(self):
        """ডাটাবেস থেকে প্রোডাক্ট ও ক্যাটাগরি ডাটা নিয়ে মডেল ট্রেইন করো"""
        print("🔄 Training ML model...")
        
        # Get training data from database
        products = Product.objects.select_related('category').all()
        
        if products.count() < 10:
            print("⚠️ Not enough data for training. Using fallback rules.")
            self.create_fallback_classifier()
            return
        
        # Prepare training data
        X_train = []
        y_train = []
        
        for product in products:
            if product.category:  # শুধু যাদের ক্যাটাগরি আছে
                # Use product name and description for training
                text = f"{product.name} {product.description or ''}"
                X_train.append(text.lower())
                y_train.append(product.category.name)
        
        if len(set(y_train)) < 2:
            print("⚠️ Need at least 2 categories for training. Using fallback.")
            self.create_fallback_classifier()
            return
        
        # Create pipeline
        self.pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )),
            ('classifier', MultinomialNB())
        ])
        
        # Train
        self.pipeline.fit(X_train, y_train)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.pipeline, self.model_path)
        
        accuracy = self.pipeline.score(X_train, y_train)
        print(f"✅ Model trained! Accuracy: {accuracy:.2%}")
    
    def create_fallback_classifier(self):
        """যখন পর্যাপ্ত ডাটা নেই, তখন keyword-based classifier ব্যবহার করো"""
        self.keyword_rules = {
            'Electronics': ['phone', 'mobile', 'laptop', 'computer', 'tv', 'television', 
                           'camera', 'headphone', 'speaker', 'smartwatch', 'tablet', 
                           'charger', 'battery', 'monitor', 'keyboard', 'mouse'],
            'Clothing': ['shirt', 'pant', 'dress', 'jacket', 'coat', 'jean', 't-shirt',
                        'trouser', 'sweater', 'hoodie', 'cap', 'hat', 'sock', 'belt'],
            'Groceries': ['rice', 'oil', 'flour', 'sugar', 'salt', 'spice', 'vegetable',
                         'fruit', 'milk', 'egg', 'bread', 'butter', 'cheese', 'tea', 'coffee'],
            'Books': ['book', 'novel', 'magazine', 'journal', 'textbook', 'dictionary',
                     'encyclopedia', 'comic', 'guide', 'manual'],
            'Furniture': ['chair', 'table', 'desk', 'sofa', 'bed', 'cabinet', 'shelf',
                         'drawer', 'wardrobe', 'bench', 'stool']
        }
        self.pipeline = None
        print("✅ Using fallback keyword-based classifier")
    
    def predict(self, product_name, description=''):
        """প্রোডাক্টের জন্য ক্যাটাগরি সাজেস্ট করো"""
        text = f"{product_name} {description}".lower()
        
        # Try ML model first
        if self.pipeline:
            try:
                categories = self.pipeline.classes_
                probabilities = self.pipeline.predict_proba([text])[0]
                best_idx = np.argmax(probabilities)
                best_category = categories[best_idx]
                confidence = probabilities[best_idx]
                
                return {
                    'category': best_category,
                    'confidence': round(float(confidence) * 100, 2),
                    'method': 'ml'
                }
            except Exception as e:
                print(f"ML prediction failed: {e}")
        
        # Fallback to keyword-based
        return self.keyword_based_predict(text)
    
    def keyword_based_predict(self, text):
        """Keyword matching based prediction"""
        scores = {}
        
        for category, keywords in self.keyword_rules.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            if score > 0:
                scores[category] = score
        
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = min(95, scores[best_category] * 20)
            return {
                'category': best_category,
                'confidence': confidence,
                'method': 'keyword'
            }
        
        return {
            'category': 'Other',
            'confidence': 30,
            'method': 'fallback'
        }
    
    def suggest_for_multiple(self, products_data):
        """একসাথে একাধিক প্রোডাক্টের জন্য সাজেশন"""
        suggestions = []
        for product in products_data:
            suggestion = self.predict(
                product.get('name', ''),
                product.get('description', '')
            )
            suggestions.append(suggestion)
        return suggestions

# Global instance
classifier = None

def get_classifier():
        global classifier
        if classifier is None:
            classifier = CategoryClassifier()
        return classifier