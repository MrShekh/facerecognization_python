from fastapi import Request, HTTPException
from fastapi.routing import APIRoute
from gps_location import is_within_worksite

class GPSValidationMiddleware(APIRoute):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/mark_attendance" and request.method == "POST":
            body = await request.json()
            employee_location = (body.get("latitude"), body.get("longitude"))

            if not employee_location or not all(employee_location):
                raise HTTPException(status_code=400, detail="Invalid GPS data.")

            if not is_within_worksite(employee_location):
                raise HTTPException(status_code=403, detail="You are not at the worksite.")

        return await call_next(request)
