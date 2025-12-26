/**
 * API Client for HealthGuard Backend
 *
 * Provides functions to interact with the FastAPI backend endpoints:
 * - Risk prediction
 * - Intervention recommendation
 * - Intervention simulation
 */

import axios from 'axios';

// Base URL for API - uses Vite proxy in development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API Key from environment (for authenticated requests)
const API_KEY = import.meta.env.VITE_API_KEY;

// Debug logging (only in development)
if (import.meta.env.DEV) {
  console.log('🔧 API Configuration:', {
    baseURL: API_BASE_URL,
    hasApiKey: !!API_KEY,
    mode: import.meta.env.MODE,
  });
}

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // Include API key if available (for staging/production)
    ...(API_KEY && { 'X-API-Key': API_KEY }),
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor for logging (only in development)
apiClient.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.url} - ${response.status}`);
    }
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error(
        `[API Error] ${error.response.status} - ${error.response.data?.detail || error.message}`
      );
    } else if (error.request) {
      // Request made but no response
      console.error('[API Error] No response from server', error.request);
    } else {
      // Request setup error
      console.error('[API Error] Request setup failed', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Check API health status
 *
 * @returns {Promise<Object>} Health check response with model status
 */
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/');
    return response.data;
  } catch (error) {
    throw new Error('Failed to connect to API: ' + error.message);
  }
};

/**
 * Predict cardiovascular disease risk for a patient
 *
 * @param {Object} patientData - Patient clinical data (13 features)
 * @param {number} patientData.age - Age in years
 * @param {number} patientData.sex - Sex (1=male, 0=female)
 * @param {number} patientData.cp - Chest pain type (1-4)
 * @param {number} patientData.trestbps - Resting blood pressure (mm Hg)
 * @param {number} patientData.chol - Serum cholesterol (mg/dl)
 * @param {number} patientData.fbs - Fasting blood sugar > 120 mg/dl (1=true, 0=false)
 * @param {number} patientData.restecg - Resting ECG results (0-2)
 * @param {number} patientData.thalach - Maximum heart rate achieved
 * @param {number} patientData.exang - Exercise induced angina (1=yes, 0=no)
 * @param {number} patientData.oldpeak - ST depression induced by exercise
 * @param {number} patientData.slope - Slope of peak exercise ST segment (1-3)
 * @param {number} patientData.ca - Number of major vessels colored by fluoroscopy (0-3)
 * @param {number} patientData.thal - Thalassemia (3=normal, 6=fixed defect, 7=reversible defect)
 * @returns {Promise<Object>} Risk prediction with score, classification, and feature importance
 */
export const predictRisk = async (patientData) => {
  try {
    const response = await apiClient.post('/api/predict', patientData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to predict risk: ' + error.message);
  }
};

/**
 * Get RL-based intervention recommendation for a patient
 *
 * @param {Object} patientData - Patient clinical data (same as predictRisk)
 * @returns {Promise<Object>} Intervention recommendation with action, cost, and expected outcomes
 */
export const getRecommendation = async (patientData) => {
  try {
    const response = await apiClient.post('/api/recommend', patientData);
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || 'Failed to get recommendation: ' + error.message
    );
  }
};

/**
 * Simulate the effect of a specific intervention on patient metrics
 *
 * @param {Object} patientData - Patient clinical data
 * @param {number} action - Action to simulate (0-4)
 *   0: Monitor Only
 *   1: Lifestyle Intervention
 *   2: Single Medication
 *   3: Combination Therapy
 *   4: Intensive Treatment
 * @returns {Promise<Object>} Simulated health status with current vs optimized metrics
 */
export const simulateIntervention = async (patientData, action) => {
  try {
    const response = await apiClient.post('/api/simulate', {
      patient: patientData,
      action: action,
    });
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || 'Failed to simulate intervention: ' + error.message
    );
  }
};

/**
 * Get all predictions and recommendations for a patient in one call
 *
 * @param {Object} patientData - Patient clinical data
 * @returns {Promise<Object>} Combined risk prediction and recommendation
 */
export const getFullAnalysis = async (patientData) => {
  try {
    const [riskPrediction, recommendation] = await Promise.all([
      predictRisk(patientData),
      getRecommendation(patientData),
    ]);

    return {
      risk: riskPrediction,
      recommendation: recommendation,
    };
  } catch (error) {
    throw new Error('Failed to get full analysis: ' + error.message);
  }
};

export default {
  checkHealth,
  predictRisk,
  getRecommendation,
  simulateIntervention,
  getFullAnalysis,
};
