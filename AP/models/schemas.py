from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

# Upload schemas
class UploadMetadata(BaseModel):
    district_name: str
    uploaded_by: str
    upload_date: str  # YYYY-MM-DD format

class UploadResponse(BaseModel):
    message: str
    document_id: int
    district_id: int

# Extraction schemas (matching the fixed schema)
class ActionPoint(BaseModel):
    action_name: str
    current_status: Optional[str] = None
    achievement_percentage: Optional[float] = None
    data_source: Optional[str] = None
    remarks: Optional[str] = None

class SubCategory(BaseModel):
    sub_category_name: str
    # Support both old format (action_points directly) and new format (information object)
    action_points: Optional[List[ActionPoint]] = None
    information: Optional[Dict[str, Any]] = None  # Contains action_points and additional_details

class Sector(BaseModel):
    sector_name: str
    sub_categories: List[SubCategory] = []

class ExtractionSchema(BaseModel):
    district: str
    upload_date: str  # YYYY-MM-DD
    sectors: List[Sector] = []

# Chat schemas
class ChatRequest(BaseModel):
    query: str  # User's question/query
    district_name: Optional[str] = None  # Optional, can be inferred from query
    sector_name: Optional[str] = None
    sub_category: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    district: str
    sources: Optional[List[str]] = None

# Response schemas
class DistrictInfo(BaseModel):
    id: int
    name: str
    document_count: int

class CategoryInfo(BaseModel):
    sector_name: str
    sub_categories: List[str]

class HistoryEntry(BaseModel):
    document_id: int
    file_name: str
    upload_date: str
    uploaded_by: str
    sector_name: str
    sub_category: str
    version_date: str
    is_latest: bool

# District data schemas
class DistrictDataResponse(BaseModel):
    district: str
    sectors: dict  # Dictionary with sector names as keys

class UploadResponseModel(BaseModel):
    status: str
    message: str

class ChatResponseModel(BaseModel):
    query: str
    response: str

class DeleteDistrictResponse(BaseModel):
    success: bool
    message: str
    district_name: str
    deleted_documents: int
    deleted_extractions: int
    deleted_files: int

class CreateDistrictRequest(BaseModel):
    district_name: str

class CreateDistrictResponse(BaseModel):
    success: bool
    message: str
    district_name: str
    district_id: int

# Authentication schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    message: str

