import os
import json
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

# Wczytaj zmienne środowiskowe z pliku .env
load_dotenv()

# Pobierz poświadczenia z zmiennej środowiskowej
firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
credentials_dict = json.loads(firebase_credentials)

# Zainicjalizuj Firebase za pomocą tych poświadczeń
cred = credentials.Certificate(credentials_dict)
firebase_admin.initialize_app(cred)
