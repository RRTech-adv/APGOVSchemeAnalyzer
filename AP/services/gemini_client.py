import requests
import json
from typing import Dict, Any, Optional
from config import settings

class GeminiClient:
    def __init__(self):
        self.api_url = settings.GEMINI_API_URL
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.headers = settings.gemini_headers
    
    def generate_completion(self, prompt: str, temperature: float = 1.0, 
                           top_p: float = 1.0, presence_penalty: float = 0.0,
                           seed: int = 25) -> Optional[str]:
        """
        Generate a completion using Gemini API
        
        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            presence_penalty: Presence penalty (-2 to 2)
            seed: Random seed for reproducibility
            
        Returns:
            Generated text response or None if error
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "presence_penalty": presence_penalty,
            "seed": seed,
            "stop": None,
            "stream": False,
            "stream_options": None,
            "temperature": temperature,
            "top_p": top_p
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the generated text from the response
            # The exact structure may vary, so we handle different possible formats
            if isinstance(result, dict):
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0].get("text", "") or result["choices"][0].get("message", {}).get("content", "")
                elif "text" in result:
                    return result["text"]
                elif "response" in result:
                    return result["response"]
                elif "content" in result:
                    return result["content"]
                else:
                    # Return the full response as JSON string if structure is unknown
                    return json.dumps(result)
            elif isinstance(result, str):
                return result
            else:
                return str(result)
                
        except requests.exceptions.RequestException as e:
            print(f"Error calling Gemini API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return None
    
    def extract_structured_data(self, document_text: str, district_name: str, 
                               upload_date: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from document text using Gemini
        Handles large documents by splitting into chunks and merging results
        
        Args:
            document_text: The extracted text from the document
            district_name: Name of the district
            upload_date: Upload date in YYYY-MM-DD format
            
        Returns:
            Structured data dictionary or None if extraction fails
        """
        # Define chunk size (characters) - leaving room for prompt overhead
        # Approximately 8000 chars for document text, leaving space for prompt template
        CHUNK_SIZE = 8000
        OVERLAP_SIZE = 500  # Overlap between chunks to avoid losing context
        
        # Check if document needs chunking
        if len(document_text) <= CHUNK_SIZE:
            # Small document - process directly
            return self._extract_from_chunk(document_text, district_name, upload_date, is_last=True)
        
        # Large document - split into chunks
        print(f"Document is large ({len(document_text)} chars). Splitting into chunks...")
        chunks = self._split_text_into_chunks(document_text, CHUNK_SIZE, OVERLAP_SIZE)
        print(f"Split document into {len(chunks)} chunks")
        
        # Process each chunk and collect results
        all_extracted_data = []
        for i, chunk in enumerate(chunks):
            is_last = (i == len(chunks) - 1)
            print(f"Processing chunk {i + 1}/{len(chunks)}...")
            
            chunk_result = self._extract_from_chunk(chunk, district_name, upload_date, is_last=is_last, chunk_num=i+1, total_chunks=len(chunks))
            
            if chunk_result:
                all_extracted_data.append(chunk_result)
            else:
                print(f"Warning: Failed to extract data from chunk {i + 1}")
        
        if not all_extracted_data:
            return None
        
        # Merge all chunk results into a single structured data
        merged_data = self._merge_extraction_results(all_extracted_data, district_name, upload_date)
        return merged_data
    
    def _split_text_into_chunks(self, text: str, chunk_size: int, overlap_size: int) -> list:
        """
        Split text into chunks with overlap
        
        Args:
            text: Full document text
            chunk_size: Maximum size of each chunk
            overlap_size: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = min(start + chunk_size, text_length)
            
            # Extract chunk
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap_size
            
            # Prevent infinite loop
            if start >= text_length - 1:
                break
        
        return chunks
    
    def _extract_from_chunk(self, chunk_text: str, district_name: str, upload_date: str, 
                           is_last: bool = True, chunk_num: int = 1, total_chunks: int = 1) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from a single chunk
        
        Args:
            chunk_text: Text chunk to process
            district_name: Name of the district
            upload_date: Upload date
            is_last: Whether this is the last chunk
            chunk_num: Current chunk number (for logging)
            total_chunks: Total number of chunks
            
        Returns:
            Extracted data dictionary or None
        """
        # Build the extraction prompt for this chunk
        prompt = self._build_extraction_prompt(chunk_text, district_name, upload_date, 
                                              is_chunk=(total_chunks > 1), chunk_num=chunk_num, total_chunks=total_chunks)
        
        # Call Gemini API
        response = self.generate_completion(prompt, temperature=0.3)
        
        if not response:
            return None
        
        # Try to parse JSON from response
        try:
            # Extract JSON from response if it's wrapped in markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            # Try to find JSON object in the response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                response = response[json_start:json_end]
            
            extracted_data = json.loads(response)
            return extracted_data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini response for chunk {chunk_num}: {e}")
            print(f"Response: {response[:500]}")
            return None
    
    def _merge_extraction_results(self, all_results: list, district_name: str, upload_date: str) -> Dict[str, Any]:
        """
        Merge extraction results from multiple chunks into a single structured data
        
        Args:
            all_results: List of extracted data dictionaries from all chunks
            district_name: Name of the district
            upload_date: Upload date
            
        Returns:
            Merged structured data dictionary
        """
        # Initialize merged structure
        merged_sectors = {}  # sector_name -> {sub_category_name -> [action_points]}
        
        # Process each chunk's results
        for result in all_results:
            if not result or "sectors" not in result:
                continue
            
            sectors = result.get("sectors", [])
            for sector in sectors:
                sector_name = sector.get("sector_name", "")
                if not sector_name:
                    continue
                
                # Initialize sector if not exists
                if sector_name not in merged_sectors:
                    merged_sectors[sector_name] = {}
                
                # Process sub_categories
                sub_categories = sector.get("sub_categories", [])
                for sub_cat in sub_categories:
                    sub_category_name = sub_cat.get("sub_category_name", "")
                    if not sub_category_name:
                        continue
                    
                    # Initialize sub_category if not exists
                    if sub_category_name not in merged_sectors[sector_name]:
                        merged_sectors[sector_name][sub_category_name] = []
                    
                    # Collect action points
                    action_points = sub_cat.get("action_points", [])
                    merged_sectors[sector_name][sub_category_name].extend(action_points)
        
        # Build final merged structure
        merged_sectors_list = []
        for sector_name, sub_cats in merged_sectors.items():
            sub_categories_list = []
            for sub_category_name, action_points in sub_cats.items():
                # Deduplicate action points based on action_name
                action_points_dict = {}
                for ap in action_points:
                    action_name = ap.get("action_name", "")
                    if action_name:
                        # Keep the most recent/complete version (prefer non-null values)
                        if action_name not in action_points_dict:
                            action_points_dict[action_name] = ap
                        else:
                            # Merge: prefer non-null values from newer data
                            existing = action_points_dict[action_name]
                            for key in ["current_status", "achievement_percentage", "data_source", "remarks"]:
                                if ap.get(key) and not existing.get(key):
                                    existing[key] = ap.get(key)
                                elif ap.get(key) and existing.get(key):
                                    # Newer data takes precedence
                                    existing[key] = ap.get(key)
                
                # Convert back to list
                unique_action_points = list(action_points_dict.values())
                
                sub_categories_list.append({
                    "sub_category_name": sub_category_name,
                    "action_points": unique_action_points
                })
            
            merged_sectors_list.append({
                "sector_name": sector_name,
                "sub_categories": sub_categories_list
            })
        
        # Return merged structure
        return {
            "district": district_name,
            "upload_date": upload_date,
            "sectors": merged_sectors_list
        }
    
    def _build_extraction_prompt(self, document_text: str, district_name: str, upload_date: str,
                                is_chunk: bool = False, chunk_num: int = 1, total_chunks: int = 1) -> str:
        """Build the extraction prompt for Gemini"""
        
        chunk_info = ""
        if is_chunk:
            chunk_info = f"""

IMPORTANT: This is chunk {chunk_num} of {total_chunks} from a large document.
- Extract all relevant information from THIS chunk only.
- Focus on finding any sectors, sub-categories, and action_points mentioned in this portion of the document.
- The results from all chunks will be merged together, so extract everything you find in this chunk."""
        
        prompt = f"""You are an AI model that extracts structured and factual information
from government documents related to schemes in Arunachal Pradesh.{chunk_info}

Analyze the document text and organize data according to this exact JSON schema:

{{
  "district": "{district_name}",
  "upload_date": "{upload_date}",
  "sectors": [
    {{
      "sector_name": "Sashakt Labharthi: Saturation Of Flagship Schemes",
      "sub_categories": [
        {{
          "sub_category_name": "Identification and Saturation of Beneficiaries",
          "action_points": [
            {{
              "action_name": "Achieve 100% beneficiary identification",
              "current_status": "text or null",
              "achievement_percentage": "number or null",
              "data_source": "text or null",
              "remarks": "text or null"
            }}
          ]
        }}
      ]
    }}
  ]
}}

Rules:
- Always include all fields (use null if data not available).
- Maintain consistent key names exactly as shown above.
- Ensure the district field is "{district_name}" and upload_date is "{upload_date}".
- Categorize content strictly into predefined sectors and sub-categories listed below.
- Only include sectors and sub_categories that have relevant data in the document.
- Extract action_points with all specified fields.
{("- Extract ALL relevant information from this chunk, even if it seems incomplete. The chunks will be merged." if is_chunk else "")}

Predefined Sectors & Sub-Categories:

Sashakt Labharthi: Saturation Of Flagship Schemes
- Identification and Saturation of Beneficiaries
- Doorstep Delivery of Scheme Benefits

Shikshit Arunachal: Education, Entrepreneurship & Employment
- Rationalization of Student Enrolment and Teacher Distribution
- Inclusive Education and focus on Improving Learning Outcomes
- Improve pass percentage of students
- Action Points from Chintan Shivir & Consultative Meetings
- Skill Identification and Promotion of Skill Developmet Programs
- Monitor and support ITI and polytechnic graduates

Swasth Arunachal: Health
- Health Coverage under Ayushman Bharat and CMAAY
- Institutional Deliveries, Vaccinations and TB Notifications Rate
- One District One Health Theme
- Drug-Free Districts by 2029

Unnat Krishi: Agriculture
- Key interventions under Unnat Krishi initiative
- One District, One Product

Sundar Arunachal: Tourism and Heritage
- Tourism Development:One District, One Tourist Spot
- One District, One Cuisine Program

Samriddh Arunachal: Good Governance
- Bottom-Up Planning and Community Participation
- Connectivity of Unconnected Areas
- Northeast Region SDG Index
- Revenue Augmentation
- Inventor of Public Infrastructure and Master Plans for Towns
- Enhancing Quality of Life of Citizens and Improved Grievance Redressal
- Capacty Building of Government Servants
- Review of Suspension Cases and Disciplinary Proceedings

Surakshit Arunachal: Security, Law & Order
- Removal and Halt of Land Encroachments and creation of Land Banks

Major Infrastructure Projects:
- Status of Long Pending Infrastructure Projects

Document Text:
{document_text}

Return ONLY valid JSON following the schema above. Do not include any explanatory text before or after the JSON."""
        
        return prompt
    
    def generate_chat_response(self, question: str, context_data: str, district_name: str) -> Optional[str]:
        """
        Generate a chat response using Gemini based on context data from database
        
        Args:
            question: User's question
            context_data: Relevant data from database as JSON string
            district_name: Name of the district being queried
            
        Returns:
            Chat response string or None if error
        """
        prompt = f"""You are an AI assistant helping users query information about government schemes 
in Arunachal Pradesh districts. Answer questions based on the provided context data.

District: {district_name}

Context Data (from database):
{context_data}

User Question: {question}

Instructions:
- Answer the question based only on the provided context data.
- If the context doesn't contain relevant information, politely state that.
- Be conversational and helpful.
- Include specific details, numbers, and facts from the context when available.
- Organize your response clearly with bullet points or short paragraphs as needed.

Provide a helpful and accurate response:"""
        
        response = self.generate_completion(prompt, temperature=0.7)
        return response

