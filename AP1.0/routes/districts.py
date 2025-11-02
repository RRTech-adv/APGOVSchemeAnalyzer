from fastapi import APIRouter

from services.db_service import DatabaseService
from models.schemas import DistrictInfo

router = APIRouter(prefix="/districts", tags=["districts"])

@router.get("/", response_model=list[DistrictInfo])
async def list_districts():
    """
    List all districts with available data
    
    Returns list of districts with their IDs and document counts
    """
    db_service = DatabaseService()
    districts = db_service.get_all_districts()
    
    return [
        DistrictInfo(
            id=district["id"],
            name=district["name"],
            document_count=district["document_count"]
        )
        for district in districts
    ]

