import { useState } from "react";
import PatientForm from "./components/PatientForm";
import RiskDisplay from "./components/RiskDisplay";
import RecommendationPanel from "./components/RecommendationPanel";
import { getFullAnalysis } from "./api/client";

function App() {
  const [loading, setLoading] = useState(false);
  const [patientData, setPatientData] = useState(null);
  const [riskPrediction, setRiskPrediction] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (formData) => {
    setLoading(true);
    setError(null);
    setPatientData(formData);
    setRiskPrediction(null);
    setRecommendation(null);

    try {
      const { risk, recommendation: rec } = await getFullAnalysis(formData);
      setRiskPrediction(risk);
      setRecommendation(rec);

      setTimeout(() => {
        document
          .getElementById("results")
          ?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    } catch (err) {
      setError(err.message);
      console.error("Analysis failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      <header className="bg-gradient-to-r from-primary-600 to-blue-700 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center">
            <div className="text-4xl mr-3">❤️</div>
            <div>
              <h1 className="text-3xl font-bold text-white">HealthGuard</h1>
              <p className="text-sm text-blue-100 mt-1">
                AI-Powered Cardiovascular Risk Assessment
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
            <h2 className="text-2xl font-bold text-gray-800 mb-3">
              Coronary Artery Disease Risk Prediction
            </h2>
            <p className="text-gray-600 max-w-3xl mx-auto">
              Enter patient clinical measurements to receive AI-powered risk assessment
              and evidence-based intervention recommendations.
            </p>
          </div>
        </div>

        <div className="mb-8">
          <PatientForm onSubmit={handleAnalyze} loading={loading} />
        </div>

        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="text-red-800 font-semibold mb-1">Analysis Failed</h3>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {(riskPrediction || recommendation) && (
          <div id="results" className="space-y-8">
            {riskPrediction && (
              <div className="animate-fadeIn">
                <RiskDisplay prediction={riskPrediction} />
              </div>
            )}

            {recommendation && patientData && (
              <div className="animate-fadeIn">
                <RecommendationPanel
                  recommendation={recommendation}
                  patientData={patientData}
                />
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
