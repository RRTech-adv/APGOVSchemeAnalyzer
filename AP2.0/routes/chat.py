from fastapi import APIRouter, HTTPException
from typing import Optional

from services.extraction_service import ExtractionService
from services.gemini_client import GeminiClient
from services.db_service import DatabaseService
from models.schemas import ChatRequest, ChatResponseModel

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponseModel)
async def chat(request: ChatRequest):
    """
    Chat endpoint integrating Gemini to query data contextually
    
    Example request: { "query": "Health stats for Tawang" }
    Example response: { "query": "Health stats for Tawang", "response": "Ayushman Bharat coverage is 94.4%..." }
    """
    extraction_service = ExtractionService()
    gemini_client = GeminiClient()
    
    # Extract district name from query if not provided
    district_name = request.district_name
    if not district_name:
        # Try to extract district name from query (simple heuristic)
        district_names = DatabaseService().get_district_names_list()
        query_lower = request.query.lower()
        for dn in district_names:
            if dn.lower() in query_lower:
                district_name = dn
                break
        
        if not district_name:
            return {
                "query": request.query,
                "response": "Please specify a district name in your query or provide it in the request."
            }
    
    # Get context data from database
    context_data = extraction_service.get_context_for_chat(
        district_name=district_name,
        sector_name=request.sector_name,
        sub_category=request.sub_category
    )
    
    if "No data found" in context_data:
        return {
            "query": request.query,
            "response": f"Sorry, I couldn't find any data for the district '{district_name}'. Please upload documents for this district first."
        }
    
    # Use the query directly
    question = request.query
    
    # Generate chat response using Gemini
    response_text = gemini_client.generate_chat_response(
        question=question,
        context_data=context_data,
        district_name=district_name
    )
    
    if not response_text:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate chat response"
        )
    
    return {
        "query": request.query,
        "response": response_text
    }

