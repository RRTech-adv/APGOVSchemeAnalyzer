from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from services.db_service import DatabaseService
from models.schemas import DeleteDistrictResponse, CreateDistrictRequest, CreateDistrictResponse

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

@router.post("/", response_model=CreateDistrictResponse)
async def create_district(request: CreateDistrictRequest):
    """
    Create a new district
    
    This endpoint allows you to add a district before uploading documents.
    Uploads can only be made to existing districts.
    
    Example request:
    {
        "district_name": "Tawang"
    }
    
    Example response:
    {
        "success": true,
        "message": "District 'Tawang' created successfully",
        "district_name": "Tawang",
        "district_id": 1
    }
    """
    db_service = DatabaseService()
    
    # Check if district already exists
    existing_districts = db_service.get_district_names_list()
    if request.district_name in existing_districts:
        raise HTTPException(
            status_code=400,
            detail=f"District '{request.district_name}' already exists"
        )
    
    # Create the district
    district_id = db_service.get_or_create_district(request.district_name)
    
    return CreateDistrictResponse(
        success=True,
        message=f"District '{request.district_name}' created successfully",
        district_name=request.district_name,
        district_id=district_id
    )

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

@router.delete("/{district_name}", response_model=DeleteDistrictResponse)
async def delete_district(district_name: str):
    """
    Delete a district and all its associated data (documents, extractions, files)
    
    This will permanently remove:
    - The district record
    - All documents associated with the district
    - All extractions/data for the district
    - Uploaded files for the district (optional)
    
    **Warning: This action cannot be undone!**
    
    Example response:
    {
        "success": true,
        "message": "District 'Tawang' and all its data have been deleted",
        "district_name": "Tawang",
        "deleted_documents": 5,
        "deleted_extractions": 12,
        "deleted_files": 5
    }
    """
    db_service = DatabaseService()
    
    result = db_service.delete_district(district_name)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=result.get("message", f"District '{district_name}' not found")
        )
    
    return result

