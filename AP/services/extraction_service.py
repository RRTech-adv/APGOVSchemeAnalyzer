from typing import Dict, Any, Optional
from services.gemini_client import GeminiClient
from services.db_service import DatabaseService
from models.schemas import ExtractionSchema
import json

class ExtractionService:
    """Service for handling data extraction and storage"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.db_service = DatabaseService()
    
    def extract_and_store(self, document_id: int, district_name: str, 
                         document_text: str, upload_date: str) -> Dict[str, Any]:
        """
        Extract structured data from document text and store in database
        
        Args:
            document_id: ID of the document in database
            district_name: Name of the district
            document_text: Extracted text from document
            upload_date: Upload date in YYYY-MM-DD format
            
        Returns:
            Dictionary with extraction results
        """
        # Get district ID
        district_id = self.db_service.get_or_create_district(district_name)
        
        # Extract structured data using Gemini
        extracted_data = self.gemini_client.extract_structured_data(
            document_text, district_name, upload_date
        )
        
        if not extracted_data:
            return {
                "success": False,
                "error": "Failed to extract data from document"
            }
        
        # Validate and store extractions
        stored_count = 0
        errors = []
        
        try:
            # Validate against schema
            extraction_schema = ExtractionSchema(**extracted_data)
            
            # Store each sector and sub_category as separate extraction
            for sector in extraction_schema.sectors:
                for sub_category in sector.sub_categories:
                    # Get existing data for this sector+sub_category to merge
                    existing_data = self.db_service.get_district_data(
                        district_name, 
                        sector.sector_name, 
                        sub_category.sub_category_name
                    )
                    
                    # Collect existing action points
                    existing_action_points = []
                    for existing_item in existing_data:
                        try:
                            existing_ap_data = json.loads(existing_item["data_json"])
                            existing_action_points.extend(existing_ap_data.get("action_points", []))
                        except (json.JSONDecodeError, KeyError):
                            pass
                    
                    # Get new action points from current document
                    new_action_points = [
                        {
                            "action_name": ap.action_name,
                            "current_status": ap.current_status,
                            "achievement_percentage": ap.achievement_percentage,
                            "data_source": ap.data_source,
                            "remarks": ap.remarks
                        }
                        for ap in sub_category.action_points
                    ]
                    
                    # Merge: Combine existing and new action points
                    # Use a dictionary to avoid duplicates based on action_name
                    merged_action_points_dict = {}
                    
                    # Add existing action points first
                    for ap in existing_action_points:
                        action_name = ap.get("action_name", "")
                        if action_name:
                            merged_action_points_dict[action_name] = ap
                    
                    # Add/update with new action points (newer data takes precedence)
                    for ap in new_action_points:
                        action_name = ap.get("action_name", "")
                        if action_name:
                            merged_action_points_dict[action_name] = ap
                    
                    # Convert back to list
                    merged_action_points = list(merged_action_points_dict.values())
                    
                    # Serialize merged action_points to JSON
                    data_json = json.dumps({
                        "action_points": merged_action_points
                    })
                    
                    try:
                        # Mark old extractions as outdated and create new merged extraction
                        self.db_service.create_extraction(
                            document_id=document_id,
                            district_id=district_id,
                            sector_name=sector.sector_name,
                            sub_category=sub_category.sub_category_name,
                            data_json=data_json,
                            version_date=upload_date
                        )
                        stored_count += 1
                    except Exception as e:
                        errors.append(f"Error storing {sector.sector_name}/{sub_category.sub_category_name}: {str(e)}")
            
            return {
                "success": True,
                "extracted_data": extracted_data,
                "stored_extractions": stored_count,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Validation or storage error: {str(e)}",
                "raw_data": extracted_data
            }
    
    def get_context_for_chat(self, district_name: str, sector_name: Optional[str] = None,
                            sub_category: Optional[str] = None) -> str:
        """
        Get relevant context data from database for chat
        
        Args:
            district_name: Name of the district
            sector_name: Optional sector filter
            sub_category: Optional sub_category filter
            
        Returns:
            Formatted context string
        """
        data = self.db_service.get_district_data(district_name, sector_name, sub_category)
        
        if not data:
            return f"No data found for district: {district_name}"
        
        # Format data for context
        context_parts = []
        for item in data:
            try:
                action_points = json.loads(item["data_json"]).get("action_points", [])
                context_parts.append(f"\nSector: {item['sector_name']}")
                context_parts.append(f"Sub-Category: {item['sub_category']}")
                context_parts.append(f"Version Date: {item['version_date']}")
                context_parts.append(f"Source Document: {item['file_name']}")
                
                for ap in action_points:
                    context_parts.append(f"  - Action: {ap.get('action_name', 'N/A')}")
                    if ap.get('current_status'):
                        context_parts.append(f"    Status: {ap['current_status']}")
                    if ap.get('achievement_percentage') is not None:
                        context_parts.append(f"    Achievement: {ap['achievement_percentage']}%")
                    if ap.get('data_source'):
                        context_parts.append(f"    Data Source: {ap['data_source']}")
                    if ap.get('remarks'):
                        context_parts.append(f"    Remarks: {ap['remarks']}")
                context_parts.append("")
            except Exception as e:
                print(f"Error formatting context item: {e}")
                continue
        
        return "\n".join(context_parts)

