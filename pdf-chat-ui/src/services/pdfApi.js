import axios from 'axios';

// Configuration
const API_BASE_URL = 'http://localhost:5000/api'; // Adjust this to your Python backend URL

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    return Promise.reject(error);
  }
);

// Mock data for development/testing
const mockResults = [
  {
    content: "Form W-4 is required for all new employees to determine federal income tax withholding. This form should be completed on or before the first day of employment.",
    metadata: {
      source: "Employee_Handbook.pdf",
      type: "text",
      page: 5
    }
  },
  {
    content: "Tax ID: 123-45-6789\nEmployee Name: John Doe\nPosition: Software Engineer\nDepartment: Engineering",
    metadata: {
      source: "Employee_Forms.pdf",
      type: "field",
      page: 2
    }
  },
  {
    content: "| Document | Deadline | Status |\n| --- | --- | --- |\n| Form W-4 | First day | Required |\n| Direct Deposit | Within 30 days | Optional |\n| Emergency Contact | Within 7 days | Required |",
    metadata: {
      source: "HR_Requirements.pdf",
      type: "table",
      page: 3
    }
  }
];

/**
 * Query the PDF system with a user question
 * @param {string} query - The user's question
 * @returns {Promise<Object>} - The response from the PDF system
 */
export const queryPDFSystem = async (query) => {
  try {
    // Try to use the real Python backend first
    try {
      const response = await apiClient.post('/query', {
        query: query,
        n_results: 5, // Number of results to return
        include_metadata: true
      });

      return {
        query: query,
        results: response.data.results.map((result, index) => ({
          content: result.content,
          metadata: result.metadata
        })),
        total_results: response.data.total_results,
        processing_time: response.data.processing_time
      };
    } catch (backendError) {
      console.warn('Backend not available, using mock data:', backendError.message);
      
      // Fallback to mock data if backend is not available
      const mockResponse = {
        query: query,
        results: mockResults.filter(result => 
          result.content.toLowerCase().includes(query.toLowerCase().split(' ')[0]) ||
          query.toLowerCase().includes('form') ||
          query.toLowerCase().includes('document') ||
          query.toLowerCase().includes('deadline') ||
          query.toLowerCase().includes('requirement')
        ),
        total_results: mockResults.length,
        processing_time: Math.random() * 2 + 0.5 // Random processing time between 0.5-2.5 seconds
      };

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, mockResponse.processing_time * 1000));

      return mockResponse;
    }
  } catch (error) {
    console.error('Error querying PDF system:', error);
    
    // Handle different types of errors
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. Please try again.');
    } else if (error.response) {
      // Server responded with an error
      throw new Error(`Server error: ${error.response.data.message || 'Unknown error'}`);
    } else if (error.request) {
      // Network error
      throw new Error('Network error. Please check your connection and try again.');
    } else {
      // Other error
      throw new Error('An unexpected error occurred. Please try again.');
    }
  }
};

/**
 * Get available PDF documents
 * @returns {Promise<Array>} - List of available PDF documents
 */
export const getAvailableDocuments = async () => {
  try {
    // Try to use the real Python backend first
    try {
      const response = await apiClient.get('/documents');
      return response.data.documents;
    } catch (backendError) {
      console.warn('Backend not available, using mock data:', backendError.message);
      
      // Fallback to mock data if backend is not available
      return [
        {
          id: 1,
          name: "Employee_Handbook.pdf",
          size: "2.3 MB",
          pages: 45,
          uploaded: "2024-01-15T10:30:00Z",
          status: "processed"
        },
        {
          id: 2,
          name: "Employee_Forms.pdf",
          size: "1.8 MB",
          pages: 12,
          uploaded: "2024-01-15T10:30:00Z",
          status: "processed"
        },
        {
          id: 3,
          name: "HR_Requirements.pdf",
          size: "956 KB",
          pages: 8,
          uploaded: "2024-01-15T10:30:00Z",
          status: "processed"
        }
      ];
    }
  } catch (error) {
    console.error('Error fetching documents:', error);
    throw error;
  }
};

/**
 * Upload a new PDF document
 * @param {File} file - The PDF file to upload
 * @returns {Promise<Object>} - Upload response
 */
export const uploadPDF = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error uploading PDF:', error);
    throw error;
  }
};

/**
 * Delete a PDF document
 * @param {number} documentId - The ID of the document to delete
 * @returns {Promise<Object>} - Delete response
 */
export const deletePDF = async (documentId) => {
  try {
    const response = await apiClient.delete(`/documents/${documentId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting PDF:', error);
    throw error;
  }
};