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
      <header className="bg-gradient-to-r from-primary-600 to-blue-700 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="text-4xl mr-3">❤️</div>
              <div>
                <h1 className="text-3xl font-bold text-white">HealthGuard</h1>
                <p className="text-sm text-blue-100 mt-1">
                  AI-Powered Cardiovascular Risk Assessment & Clinical Guidance
                </p>
              </div>
            </div>

            {/* API Status Indicator */}
            {apiHealth && (
              <div className="flex items-center bg-white bg-opacity-20 px-4 py-2 rounded-lg backdrop-blur-sm">
                <div
                  className={`w-2.5 h-2.5 rounded-full mr-2 ${
                    apiHealth.status === 'healthy'
                      ? 'bg-green-400 animate-pulse'
                      : apiHealth.status === 'degraded'
                        ? 'bg-yellow-400'
                        : 'bg-red-400'
                  }`}
                />
                <span className="text-sm text-white font-medium">
                  {apiHealth.status === 'healthy'
                    ? 'System Online'
                    : apiHealth.status === 'degraded'
                      ? 'Limited Service'
                      : 'Offline'}
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
              Start the backend:{' '}
              <code className="bg-red-100 px-1 rounded">
                cd backend && uvicorn api.main:app --reload
              </code>
            </p>
          </div>
        )}

        {/* Introduction */}
        <div className="mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
            <div className="flex justify-center mb-4">
              <div className="bg-gradient-to-r from-primary-100 to-blue-100 rounded-full p-4">
                <span className="text-4xl">🩺</span>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-3">
              Coronary Artery Disease Risk Prediction
            </h2>
            <p className="text-gray-600 max-w-3xl mx-auto leading-relaxed mb-4">
              Enter patient clinical measurements to receive an AI-powered risk assessment and
              evidence-based intervention recommendations. This system predicts{' '}
              <strong>Coronary Artery Disease (CAD)</strong> — the narrowing of arteries that supply
              blood to your heart — and recommends personalized treatment strategies.
            </p>

            {/* Demo Information Box */}
            <div className="max-w-4xl mx-auto mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200 text-left">
              <h3 className="text-sm font-semibold text-gray-800 mb-2 flex items-center">
                <span className="mr-2">ℹ️</span>
                About This Demo
              </h3>
              <div className="space-y-2 text-sm text-gray-700">
                <p>
                  <strong>What it predicts:</strong> Probability of ≥50% narrowing in coronary
                  arteries (clinical threshold for significant CAD), validated by angiography
                </p>
                <p>
                  <strong>How it works:</strong> Random Forest classifier analyzes 13 cardiovascular
                  risk factors, then applies ACC/AHA clinical guidelines to recommend interventions
                  (lifestyle changes, medications, or intensive treatment)
                </p>
                <p>
                  <strong>Dataset:</strong> UCI Heart Disease Dataset — 303 patients from Cleveland
                  Clinic with angiography-confirmed diagnoses
                </p>
                <p>
                  <strong>Performance:</strong> 89% accuracy, 94.5% ROC-AUC on validation data
                </p>
              </div>
              <p className="text-xs text-amber-700 mt-3 italic bg-amber-50 p-2 rounded border border-amber-200">
                ⚠️ <strong>Demonstration Only:</strong> This is a portfolio project showing how ML
                can be applied to healthcare. Not validated for clinical use — always consult
                healthcare professionals for medical decisions.
              </p>
            </div>

            <div className="mt-4 flex justify-center gap-6 text-sm">
              <div className="flex items-center text-gray-600">
                <span className="mr-2">✓</span>
                <span>89% Accuracy</span>
              </div>
              <div className="flex items-center text-gray-600">
                <span className="mr-2">✓</span>
                <span>ACC/AHA Guidelines</span>
              </div>
              <div className="flex items-center text-gray-600">
                <span className="mr-2">✓</span>
                <span>Angiography-Validated</span>
              </div>
            </div>
          </div>
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
            {/* Patient Info Banner */}
            {patientData && (
              <div className="bg-gradient-to-r from-gray-50 to-blue-50 border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="text-2xl mr-3">📊</div>
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700">Analysis Results</h3>
                      <p className="text-xs text-gray-600">
                        Patient: {patientData.age} years old,{' '}
                        {patientData.sex === 1 ? 'Male' : 'Female'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Risk Display */}
            {riskPrediction && (
              <div className="animate-fadeIn">
                <RiskDisplay prediction={riskPrediction} />
              </div>
            )}

            {/* Recommendation Panel */}
            {recommendation && patientData && (
              <div className="animate-fadeIn" style={{ animationDelay: '200ms' }}>
                <RecommendationPanel recommendation={recommendation} patientData={patientData} />
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
                and 94.5% ROC-AUC. Provides interpretable feature importance for clinical
                decision-making.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-1">Guideline-Based Recommendations</h4>
              <p className="text-gray-600">
                Evidence-based intervention recommender following ACC/AHA clinical guidelines.
                Provides personalized treatment strategies based on risk stratification and
                identified cardiovascular risk factors.
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
