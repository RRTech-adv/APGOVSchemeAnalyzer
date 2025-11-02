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
        
        Args:
            document_text: The extracted text from the document
            district_name: Name of the district
            upload_date: Upload date in YYYY-MM-DD format
            
        Returns:
            Structured data dictionary or None if extraction fails
        """
        # Build the extraction prompt
        prompt = self._build_extraction_prompt(document_text, district_name, upload_date)
        
        # Call Gemini API
        response = self.generate_completion(prompt, temperature=0.3)  # Lower temperature for more consistent extraction
        
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
            print(f"Error parsing JSON from Gemini response: {e}")
            print(f"Response: {response[:500]}")
            return None
    
    def _build_extraction_prompt(self, document_text: str, district_name: str, upload_date: str) -> str:
        """Build the extraction prompt for Gemini"""
        prompt = f"""You are an AI model that extracts structured and factual information
from government documents related to schemes in Arunachal Pradesh.

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

Predefined Sectors & Sub-Categories:

Sashakt Labharthi: Saturation Of Flagship Schemes
- Identification and Saturation of Beneficiaries
- Scheme Saturation Targets & Achievement Data
- Doorstep Delivery of Scheme Benefits
- Targeted Benefits and Entitlements
- Seva Aapke Dwar 2.0
- Department Guidelines

Shikshit Arunachal: Education, Entrepreneurship & Employment
- Student Enrolment and Teacher Distribution
- Pass Percentage Improvement
- Chintan Shivir & Consultative Meetings
- Skill Identification & Development

Swasth Arunachal: Health
- Ayushman Bharat and CMAAY Coverage
- Institutional Deliveries & Vaccinations
- One District One Health Theme
- Drug-Free Districts

Unnat Krishi: Agriculture
- Organic & Horticulture Development
- Animal Husbandry & Fisheries
- Integrated Farming System
- Agri-Tech & FPOs
- SHGs & Cooperatives
- Capacity Building

Sundar Arunachal: Tourism and Heritage
- One District One Tourist Spot
- Indigenous Festivals
- Zero Plastic Destination
- One District One Cuisine

Samriddh Arunachal: Good Governance
- Bottom-Up Planning
- Connectivity
- SDG Index
- Revenue Augmentation
- Infrastructure Inventory
- Grievance Redressal
- Government Servant Capacity Building
- Disciplinary Case Reviews

Surakshit Arunachal: Security, Law & Order
- Land Encroachments & Land Banks
- Status of Major Infrastructure Projects
- Frontier Highways
- 132 kV Transmission Line Issues
- Arunachal Pradesh–Assam Boundary Accord

Document Text:
{document_text[:10000]}  # Limit to first 10000 characters to avoid token limits

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

