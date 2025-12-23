/**
 * Main Application Component for HealthGuard
 *
 * Orchestrates the entire frontend:
 * - Patient data input form
 * - Risk prediction display
 * - Intervention recommendations
 * - API communication and state management
 */

import { useState, useEffect } from 'react';
import PatientForm from './components/PatientForm';
import RiskDisplay from './components/RiskDisplay';
import RecommendationPanel from './components/RecommendationPanel';
import { getFullAnalysis, checkHealth } from './api/client';

function App() {
  const [loading, setLoading] = useState(false);
  const [apiHealth, setApiHealth] = useState(null);
  const [patientData, setPatientData] = useState(null);
  const [riskPrediction, setRiskPrediction] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [error, setError] = useState(null);

  // Check API health on mount
  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        const health = await checkHealth();
        setApiHealth(health);
        console.log('API Health:', health);
      } catch (err) {
        console.error('API health check failed:', err);
        setApiHealth({ status: 'unavailable', message: err.message });
      }
    };

    checkApiHealth();
  }, []);

  const handleAnalyze = async (formData) => {
    setLoading(true);
    setError(null);
    setPatientData(formData);
    setRiskPrediction(null);
    setRecommendation(null);

    try {
      // Get both risk prediction and recommendation in parallel
      const { risk, recommendation: rec } = await getFullAnalysis(formData);

      setRiskPrediction(risk);
      setRecommendation(rec);

      // Scroll to results
      setTimeout(() => {
        document.getElementById('results')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err) {
      setError(err.message);
      console.error('Analysis failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                HealthGuard
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Predictive Health Monitoring with AI-Powered Intervention Recommendations
              </p>
            </div>

            {/* API Status Indicator */}
            {apiHealth && (
              <div className="flex items-center">
                <div
                  className={`w-3 h-3 rounded-full mr-2 ${
                    apiHealth.status === 'healthy'
                      ? 'bg-green-500'
                      : apiHealth.status === 'degraded'
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                />
                <span className="text-sm text-gray-600">
                  {apiHealth.status === 'healthy'
                    ? 'API Connected'
                    : apiHealth.status === 'degraded'
                    ? 'API Degraded'
                    : 'API Unavailable'}
                </span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* API Unavailable Warning */}
        {apiHealth?.status === 'unavailable' && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="text-red-800 font-semibold mb-1">Backend API Unavailable</h3>
            <p className="text-red-700 text-sm">
              Cannot connect to the backend server. Please ensure the FastAPI server is running at{' '}
              <code className="bg-red-100 px-1 rounded">http://localhost:8000</code>
            </p>
            <p className="text-red-600 text-xs mt-2">
              Start the backend: <code className="bg-red-100 px-1 rounded">cd backend && uvicorn api.main:app --reload</code>
            </p>
          </div>
        )}

        {/* Introduction */}
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Cardiovascular Disease Risk Assessment
          </h2>
          <p className="text-gray-600 max-w-3xl mx-auto">
            Enter patient clinical measurements to receive an AI-powered risk assessment and personalized
            intervention recommendations. Our system combines Random Forest prediction with Reinforcement
            Learning to optimize treatment strategies.
          </p>
        </div>

        {/* Patient Form */}
        <div className="mb-8">
          <PatientForm onSubmit={handleAnalyze} loading={loading} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="text-red-800 font-semibold mb-1">Analysis Failed</h3>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Results Section */}
        {(riskPrediction || recommendation) && (
          <div id="results" className="space-y-8">
            {/* Risk Display */}
            {riskPrediction && (
              <div className="animate-fadeIn">
                <RiskDisplay prediction={riskPrediction} />
              </div>
            )}

            {/* Recommendation Panel */}
            {recommendation && patientData && (
              <div className="animate-fadeIn" style={{ animationDelay: '200ms' }}>
                <RecommendationPanel
                  recommendation={recommendation}
                  patientData={patientData}
                />
              </div>
            )}
          </div>
        )}

        {/* Footer Info */}
        <div className="mt-12 p-6 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">About This System</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-700">
            <div>
              <h4 className="font-semibold mb-1">Risk Prediction Model</h4>
              <p className="text-gray-600">
                Random Forest classifier trained on the UCI Heart Disease dataset with 89% accuracy
                and 94.5% ROC-AUC. Provides interpretable feature importance for clinical decision-making.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-1">Intervention Agent</h4>
              <p className="text-gray-600">
                Q-Learning reinforcement learning agent that optimizes treatment strategies by balancing
                risk reduction, treatment costs, and quality of life impacts.
              </p>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-300">
            <p className="text-xs text-gray-500 text-center">
              This is a portfolio project demonstrating the application of predictive maintenance ML
              principles to preventive healthcare. Not for clinical use without proper validation.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
