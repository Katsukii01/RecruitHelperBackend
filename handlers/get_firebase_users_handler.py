from fastapi import APIRouter, HTTPException
import firebase_admin
from firebase_admin import auth
from typing import List

# Router FastAPI
get_firebase_users_router = APIRouter()

@get_firebase_users_router.get("/api/get-users/")  # Use GET for fetching users
async def get_firebase_users():
    try:
        # Pobieranie użytkowników z Firebase Authentication
        page = auth.list_users()  # Domyślnie zwróci 1000 użytkowników na raz
        users = []

        # Iteracja po użytkownikach i pobieranie danych
        while page:
            for user in page.users:
                users.append({
                    "uid": user.uid,
                    "email": user.email,
                    "displayName": user.display_name,
                })
            if page.next_page_token:
                page = auth.list_users(page_token=page.next_page_token)
            else:
                break

        return users

    except firebase_admin.exceptions.FirebaseError as error:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
