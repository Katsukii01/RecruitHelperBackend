from fastapi import APIRouter, HTTPException
import firebase_admin
from firebase_admin import auth
from pydantic import BaseModel
from typing import Optional

# Router FastAPI
edit_firebase_user_router = APIRouter()

# Pydantic model for request body validation
class UpdateUserRequest(BaseModel):
    uid: str
    userName: Optional[str] = None
    password: Optional[str] = None

@edit_firebase_user_router.put("/api/update-user/")
async def update_firebase_user(request: UpdateUserRequest):
    try:
        update_params = {}

        # Only include the display_name if a username is provided
        if request.userName:
            update_params["display_name"] = request.userName

        # Only include the password if it's provided
        if request.password:
            update_params["password"] = request.password

        # If no update params were provided, raise an error
        if not update_params:
            raise HTTPException(status_code=400, detail="No update parameters provided")

        # Update the user
        auth.update_user(request.uid, **update_params)
        return {"message": f"User {request.uid} updated successfully with {', '.join(update_params.keys())}."}

    except firebase_admin.exceptions.FirebaseError as error:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
