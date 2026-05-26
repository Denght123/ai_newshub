from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    return {
        "code": 200,
        "message": "success",
        "data": {
            "status": "ok",
            "service": "ai-newshub-backend",
        },
    }
