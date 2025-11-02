import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from config import settings

class DatabaseService:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create districts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS districts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        
        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district_id INTEGER,
                file_name TEXT,
                file_path TEXT,
                upload_date TEXT,
                uploaded_by TEXT,
                raw_text TEXT,
                FOREIGN KEY (district_id) REFERENCES districts(id)
            )
        """)
        
        # Create extractions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                district_id INTEGER,
                sector_name TEXT,
                sub_category TEXT,
                data_json TEXT,
                version_date TEXT,
                is_latest INTEGER DEFAULT 1,
                FOREIGN KEY (document_id) REFERENCES documents(id),
                FOREIGN KEY (district_id) REFERENCES districts(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_or_create_district(self, district_name: str) -> int:
        """Get district ID or create if doesn't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Try to get existing district
        cursor.execute("SELECT id FROM districts WHERE name = ?", (district_name,))
        result = cursor.fetchone()
        
        if result:
            district_id = result[0]
        else:
            cursor.execute("INSERT INTO districts (name) VALUES (?)", (district_name,))
            district_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return district_id
    
    def create_document(self, district_id: int, file_name: str, file_path: str, 
                       upload_date: str, uploaded_by: str, raw_text: str) -> int:
        """Create a new document entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO documents (district_id, file_name, file_path, upload_date, uploaded_by, raw_text)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (district_id, file_name, file_path, upload_date, uploaded_by, raw_text))
        
        document_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return document_id
    
    def mark_extractions_outdated(self, district_id: int, sector_name: str, sub_category: str):
        """Mark previous extractions as not latest for given district, sector, and sub_category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE extractions 
            SET is_latest = 0 
            WHERE district_id = ? AND sector_name = ? AND sub_category = ?
        """, (district_id, sector_name, sub_category))
        
        conn.commit()
        conn.close()
    
    def create_extraction(self, document_id: int, district_id: int, sector_name: str,
                         sub_category: str, data_json: str, version_date: str):
        """Create a new extraction entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Mark previous extractions as outdated
        self.mark_extractions_outdated(district_id, sector_name, sub_category)
        
        cursor.execute("""
            INSERT INTO extractions (document_id, district_id, sector_name, sub_category, data_json, version_date, is_latest)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (document_id, district_id, sector_name, sub_category, data_json, version_date))
        
        extraction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return extraction_id
    
    def get_all_districts(self) -> List[Dict[str, Any]]:
        """Get all districts with document counts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT d.id, d.name, COUNT(DISTINCT doc.id) as document_count
            FROM districts d
            LEFT JOIN documents doc ON d.id = doc.district_id
            GROUP BY d.id, d.name
            ORDER BY d.name
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "name": row[1],
                "document_count": row[2]
            })
        
        conn.close()
        return results
    
    def get_district_data(self, district_name: str, sector_name: Optional[str] = None,
                         sub_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get extraction data for a district, optionally filtered by sector and sub_category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get district ID
        cursor.execute("SELECT id FROM districts WHERE name = ?", (district_name,))
        district_row = cursor.fetchone()
        
        if not district_row:
            return []
        
        district_id = district_row[0]
        
        # Build query
        query = """
            SELECT e.id, e.document_id, e.district_id, e.sector_name, e.sub_category, 
                   e.data_json, e.version_date, e.is_latest, doc.file_name
            FROM extractions e
            JOIN documents doc ON e.document_id = doc.id
            WHERE e.district_id = ? AND e.is_latest = 1
        """
        
        params = [district_id]
        
        if sector_name:
            query += " AND e.sector_name = ?"
            params.append(sector_name)
        
        if sub_category:
            query += " AND e.sub_category = ?"
            params.append(sub_category)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "document_id": row[1],
                "district_id": row[2],
                "sector_name": row[3],
                "sub_category": row[4],
                "data_json": row[5],
                "version_date": row[6],
                "is_latest": bool(row[7]),
                "file_name": row[8]
            })
        
        conn.close()
        return results
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all sectors and their sub_categories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT sector_name, sub_category
            FROM extractions
            WHERE is_latest = 1
            ORDER BY sector_name, sub_category
        """)
        
        categories = {}
        for row in cursor.fetchall():
            sector = row[0]
            sub_cat = row[1]
            
            if sector not in categories:
                categories[sector] = []
            
            if sub_cat not in categories[sector]:
                categories[sector].append(sub_cat)
        
        results = [
            {"sector_name": sector, "sub_categories": sub_cats}
            for sector, sub_cats in categories.items()
        ]
        
        conn.close()
        return results
    
    def get_district_history(self, district_name: str) -> List[Dict[str, Any]]:
        """Get version history for a district"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get district ID
        cursor.execute("SELECT id FROM districts WHERE name = ?", (district_name,))
        district_row = cursor.fetchone()
        
        if not district_row:
            return []
        
        district_id = district_row[0]
        
        cursor.execute("""
            SELECT doc.id, doc.file_name, doc.upload_date, doc.uploaded_by,
                   e.sector_name, e.sub_category, e.version_date, e.is_latest
            FROM extractions e
            JOIN documents doc ON e.document_id = doc.id
            WHERE e.district_id = ?
            ORDER BY e.version_date DESC, e.sector_name, e.sub_category
        """, (district_id,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "document_id": row[0],
                "file_name": row[1],
                "upload_date": row[2],
                "uploaded_by": row[3],
                "sector_name": row[4],
                "sub_category": row[5],
                "version_date": row[6],
                "is_latest": bool(row[7])
            })
        
        conn.close()
        return results
    
    def get_district_names_list(self) -> List[str]:
        """Get a simple list of all district names"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM districts ORDER BY name")
        names = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return names
    
    def get_district_data_structured(self, district_name: str) -> Dict[str, Any]:
        """
        Get all extracted data for a district in structured format
        Returns: {
            "district": "Tawang",
            "sectors": {
                "Sector Name": {
                    "Sub-Category Name": {
                        "action_points": [...]
                    }
                }
            }
        }
        """
        data = self.get_district_data(district_name)
        
        result = {
            "district": district_name,
            "sectors": {}
        }
        
        for item in data:
            sector_name = item["sector_name"]
            sub_category = item["sub_category"]
            
            if sector_name not in result["sectors"]:
                result["sectors"][sector_name] = {}
            
            try:
                action_points_data = json.loads(item["data_json"])
                result["sectors"][sector_name][sub_category] = action_points_data
            except json.JSONDecodeError:
                result["sectors"][sector_name][sub_category] = {"action_points": []}
        
        return result
    
    def get_district_analytics(self, district_name: str) -> Dict[str, float]:
        """
        Calculate analytics/completion percentages per sector for a district
        Returns: {"Sector Name": completion_percentage, ...}
        """
        data = self.get_district_data(district_name)
        
        sector_stats = {}  # {sector_name: {"total": 0, "completed": 0}}
        
        for item in data:
            sector_name = item["sector_name"]
            
            if sector_name not in sector_stats:
                sector_stats[sector_name] = {"total": 0, "sum_percentage": 0.0, "count": 0}
            
            try:
                action_points_data = json.loads(item["data_json"])
                action_points = action_points_data.get("action_points", [])
                
                for ap in action_points:
                    sector_stats[sector_name]["total"] += 1
                    achievement = ap.get("achievement_percentage")
                    if achievement is not None:
                        try:
                            percentage = float(achievement)
                            sector_stats[sector_name]["sum_percentage"] += percentage
                            sector_stats[sector_name]["count"] += 1
                        except (ValueError, TypeError):
                            pass
            except json.JSONDecodeError:
                pass
        
        # Calculate average completion percentage per sector
        analytics = {}
        for sector_name, stats in sector_stats.items():
            if stats["count"] > 0:
                # Average of all achievement percentages
                avg_percentage = stats["sum_percentage"] / stats["count"]
                analytics[sector_name] = round(avg_percentage, 2)
            elif stats["total"] > 0:
                # If there are action points but no percentages, return 0
                analytics[sector_name] = 0.0
            else:
                # No data for this sector
                analytics[sector_name] = 0.0
        
        return analytics
    
    def delete_district(self, district_name: str) -> Dict[str, Any]:
        """
        Delete a district and all its associated data (documents, extractions)
        
        Args:
            district_name: Name of the district to delete
            
        Returns:
            Dictionary with deletion results
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get district ID
        cursor.execute("SELECT id FROM districts WHERE name = ?", (district_name,))
        district_row = cursor.fetchone()
        
        if not district_row:
            conn.close()
            return {
                "success": False,
                "message": f"District '{district_name}' not found",
                "deleted_documents": 0,
                "deleted_extractions": 0
            }
        
        district_id = district_row[0]
        
        # Get document IDs and file paths for this district
        cursor.execute("SELECT id, file_path FROM documents WHERE district_id = ?", (district_id,))
        documents = cursor.fetchall()
        document_ids = [doc[0] for doc in documents]
        file_paths = [doc[1] for doc in documents]
        
        # Count extractions to be deleted
        cursor.execute("SELECT COUNT(*) FROM extractions WHERE district_id = ?", (district_id,))
        extraction_count = cursor.fetchone()[0]
        
        # Delete extractions first (due to foreign key constraints)
        cursor.execute("DELETE FROM extractions WHERE district_id = ?", (district_id,))
        deleted_extractions = cursor.rowcount
        
        # Delete documents
        cursor.execute("DELETE FROM documents WHERE district_id = ?", (district_id,))
        deleted_documents = cursor.rowcount
        
        # Delete district
        cursor.execute("DELETE FROM districts WHERE id = ?", (district_id,))
        
        conn.commit()
        conn.close()
        
        # Optionally delete uploaded files (optional - comment out if you want to keep files)
        deleted_files = 0
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_files += 1
                except Exception as e:
                    print(f"Warning: Could not delete file {file_path}: {e}")
        
        return {
            "success": True,
            "message": f"District '{district_name}' and all its data have been deleted",
            "district_name": district_name,
            "deleted_documents": deleted_documents,
            "deleted_extractions": deleted_extractions,
            "deleted_files": deleted_files
        }

