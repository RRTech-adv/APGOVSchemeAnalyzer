from fastapi import APIRouter

from services.db_service import DatabaseService
from models.schemas import CategoryInfo

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=list[CategoryInfo])
async def list_categories():
    """
    List all sectors and their sub-categories available in the database
    """
    db_service = DatabaseService()
    categories = db_service.get_all_categories()
    
    return [
        CategoryInfo(
            sector_name=cat["sector_name"],
            sub_categories=cat["sub_categories"]
        )
        for cat in categories
    ]

