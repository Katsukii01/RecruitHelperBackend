import os
import json
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

# Wczytaj zmienne środowiskowe
load_dotenv()

# Pobierz poświadczenia z env
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

# Jeśli nie jest None, sparsuj JSON
if firebase_credentials:
    try:
        credentials_dict = json.loads(firebase_credentials)
        cred = credentials.Certificate(credentials_dict)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Initialized!")
    except json.JSONDecodeError as e:
        print(f"❌ Błąd dekodowania JSON: {e}")
else:
    print("❌ Zmienna FIREBASE_CREDENTIALS jest pusta lub nie została poprawnie wczytana!")
