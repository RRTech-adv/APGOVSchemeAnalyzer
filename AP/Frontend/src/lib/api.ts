// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Get auth token from localStorage
const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

// Helper function for API calls
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add Authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config: RequestInit = {
    headers,
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If JSON parsing fails, use status text
        errorMessage = response.statusText || errorMessage;
      }
      
      // Special handling for 401 errors (unauthorized)
      if (response.status === 401) {
        throw new Error('Incorrect username or password');
      }
      
      throw new Error(errorMessage);
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const text = await response.text();
      return text ? JSON.parse(text) : null;
    }
    return await response.json();
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      console.error(`Network error for ${endpoint}: Backend may not be running`);
      throw new Error('Unable to connect to backend. Please ensure the backend is running on http://localhost:8000');
    }
    console.error(`API call failed for ${endpoint}:`, error);
    throw error;
  }
}

// API Functions
export const api = {
  // Get all districts
  getDistricts: async (): Promise<string[]> => {
    return apiCall<string[]>('/districts/');
  },

  // Get district data
  getDistrictData: async (districtName: string): Promise<any> => {
    return apiCall<any>(`/districts/${encodeURIComponent(districtName)}`);
  },

  // Get district analytics
  getDistrictAnalytics: async (districtName: string): Promise<Record<string, number>> => {
    return apiCall<Record<string, number>>(`/districts/${encodeURIComponent(districtName)}/analytics`);
  },

  // Upload document
  uploadDocument: async (
    file: File,
    districtName: string,
    uploadedBy: string = 'User',
    uploadDate?: string
  ): Promise<{ status: string; message: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('district_name', districtName);
    formData.append('uploaded_by', uploadedBy);
    if (uploadDate) {
      formData.append('upload_date', uploadDate);
    }

    return apiCall<{ status: string; message: string }>('/upload/', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type with boundary for FormData
      body: formData,
    });
  },

  // Chat endpoint
  chat: async (
    query: string,
    districtName?: string,
    sectorName?: string,
    subCategory?: string
  ): Promise<{ query: string; response: string }> => {
    return apiCall<{ query: string; response: string }>('/chat/', {
      method: 'POST',
      body: JSON.stringify({
        query,
        district_name: districtName,
        sector_name: sectorName,
        sub_category: subCategory,
      }),
    });
  },

  // Get categories
  getCategories: async (): Promise<any[]> => {
    return apiCall<any[]>('/categories/');
  },

  // Get district history
  getDistrictHistory: async (districtName: string): Promise<any[]> => {
    return apiCall<any[]>(`/history/${encodeURIComponent(districtName)}`);
  },

  // Authentication
  login: async (username: string, password: string): Promise<{ access_token: string; token_type: string; username: string; message: string }> => {
    // Don't include auth token for login endpoint
    const url = `${API_BASE_URL}/auth/login`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  },

  verifyToken: async (): Promise<any> => {
    return apiCall<any>('/auth/verify', {
      method: 'GET',
    });
  },
};

