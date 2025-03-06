from fastapi import APIRouter, HTTPException
import firebase_admin
from firebase_admin import auth
from typing import List

# Router FastAPI
delete_firebase_user_router = APIRouter()

@delete_firebase_user_router.delete("/api/delete-user/")  # Use GET for fetching users
async def delete_firebase_user(userId: str):
    try:
        # Delete the user by userId
        print(f"Deleting user with ID: {userId}")
        auth.delete_user(userId)
        return {"message": f"User {userId} deleted successfully."}

    except firebase_admin.exceptions.FirebaseError as error:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

 
