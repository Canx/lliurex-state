import firebase_admin
from firebase_admin import credentials, db
import os
import json

import re

def get_frontend_db_url():
    """Try to extract databaseURL from firebase_frontend_config.js"""
    try:
        if os.path.exists('firebase_frontend_config.js'):
            with open('firebase_frontend_config.js', 'r') as f:
                content = f.read()
                match = re.search(r'databaseURL:\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
    except:
        pass
    return None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if app is already initialized
        firebase_admin.get_app()
        return True
    except ValueError:
        pass # Not initialized

    # Try to get credentials
    cred = None
    
    # 1. Try environment variable with JSON content (GitHub Actions style)
    if os.environ.get('FIREBASE_KEY_JSON'):
        try:
            key_dict = json.loads(os.environ['FIREBASE_KEY_JSON'])
            cred = credentials.Certificate(key_dict)
        except json.JSONDecodeError:
            print("Error: FIREBASE_KEY_JSON is not valid JSON")

    # 2. Try local file
    elif os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
        
    if cred:
        # Initialize with database URL
        # Priority:
        # 1. Env var FIREBASE_DB_URL
        # 2. Extracted from frontend config
        # 3. Guess based on project ID
        
        db_url = os.environ.get('FIREBASE_DB_URL')
        
        if not db_url:
            db_url = get_frontend_db_url()

        if not db_url:
            # Try to infer from credential
            project_id = cred.project_id
            if project_id:
                # Default US region
                db_url = f"https://{project_id}-default-rtdb.firebaseio.com/"
        
        if db_url:
            print(f"🔥 Initializing Firebase connection to {db_url}...")
            firebase_admin.initialize_app(cred, {
                'databaseURL': db_url
            })
            return True
        else:
            print("❌ Error: Could not determine Firebase Database URL. Set FIREBASE_DB_URL environment variable.")
            return False
            
    print("⚠️ Warning: No Firebase credentials found. Skipping Firebase updates.")
    return False

def save_to_firebase(path, data):
    """Save data to a specific path in Firebase Realtime Database"""
    if not initialize_firebase():
        return False
        
    try:
        ref = db.reference(path)
        ref.set(data)
        print(f"✅ Saved data to Firebase: {path}")
        return True
    except Exception as e:
        print(f"❌ Error saving to Firebase: {e}")
        return False

def push_to_firebase(path, data):
    """Push new item to a list in Firebase Realtime Database"""
    if not initialize_firebase():
        return False
        
    try:
        ref = db.reference(path)
        ref.push(data)
        print(f"✅ Pushed data to Firebase: {path}")
        return True
    except Exception as e:
        print(f"❌ Error pushing to Firebase: {e}")
        return False
