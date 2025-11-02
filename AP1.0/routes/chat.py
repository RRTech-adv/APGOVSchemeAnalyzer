from fastapi import APIRouter, HTTPException
from typing import Optional

from services.extraction_service import ExtractionService
from services.gemini_client import GeminiClient
from models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat interface for querying district-wise scheme information
    
    Request body:
    - district_name: Name of the district (required)
    - sector_name: Optional sector filter
    - sub_category: Optional sub_category filter
    - question: Optional specific question (if not provided, returns summary)
    """
    extraction_service = ExtractionService()
    gemini_client = GeminiClient()
    
    # Get context data from database
    context_data = extraction_service.get_context_for_chat(
        district_name=request.district_name,
        sector_name=request.sector_name,
        sub_category=request.sub_category
    )
    
    if "No data found" in context_data:
        return ChatResponse(
            response=f"Sorry, I couldn't find any data for the district '{request.district_name}'. Please upload documents for this district first.",
            district=request.district_name
        )
    
    # Generate question if not provided
    if not request.question:
        if request.sector_name and request.sub_category:
            question = f"What is the status and information about {request.sub_category} in the {request.sector_name} sector for {request.district_name}?"
        elif request.sector_name:
            question = f"Provide a summary of all schemes and activities in the {request.sector_name} sector for {request.district_name}."
        else:
            question = f"Provide a comprehensive summary of all schemes and activities for {request.district_name} district."
    else:
        question = request.question
    
    # Generate chat response using Gemini
    response_text = gemini_client.generate_chat_response(
        question=question,
        context_data=context_data,
        district_name=request.district_name
    )
    
    if not response_text:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate chat response"
        )
    
    # Get source documents for reference
    from services.db_service import DatabaseService
    db_service = DatabaseService()
    data = db_service.get_district_data(
        request.district_name,
        request.sector_name,
        request.sub_category
    )
    sources = list(set([item["file_name"] for item in data])) if data else None
    
    return ChatResponse(
        response=response_text,
        district=request.district_name,
        sources=sources
    )

