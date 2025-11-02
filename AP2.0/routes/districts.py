from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from services.db_service import DatabaseService

router = APIRouter(prefix="/districts", tags=["districts"])

@router.get("/")
async def list_districts():
    """
    Returns list of available districts
    
    Example: ["Tawang", "West Kameng", "Papum Pare"]
    """
    db_service = DatabaseService()
    district_names = db_service.get_district_names_list()
    return district_names

@router.get("/{district_name}", response_model=Dict[str, Any])
async def get_district_data(district_name: str):
    """
    Returns all extracted and processed data for that district
    
    Example: { "district": "Tawang", "sectors": { "Health": {...}, "Education": {...} } }
    """
    db_service = DatabaseService()
    
    # Check if district exists
    district_names = db_service.get_district_names_list()
    if district_name not in district_names:
        raise HTTPException(
            status_code=404,
            detail=f"District '{district_name}' not found"
        )
    
    data = db_service.get_district_data_structured(district_name)
    return data

@router.get("/{district_name}/analytics", response_model=Dict[str, float])
async def get_district_analytics(district_name: str):
    """
    Returns preprocessed statistics for graphs (e.g., % completion per sector)
    
    Example: { "Health": 94.4, "Education": 70.0, "Agriculture": 88.0 }
    """
    db_service = DatabaseService()
    
    # Check if district exists
    district_names = db_service.get_district_names_list()
    if district_name not in district_names:
        raise HTTPException(
            status_code=404,
            detail=f"District '{district_name}' not found"
        )
    
    analytics = db_service.get_district_analytics(district_name)
    return analytics

