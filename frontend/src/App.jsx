import { useState } from 'react';
import ProfessionalHeader from './components/ProfessionalHeader';
import PageContainer from './components/PageContainer';
import PatientForm from './components/PatientForm';
import RecommendationPanel from './components/RecommendationPanel';
import { getFullAnalysis } from './api/client';
import { Icon, MedicalIcons } from './utils/icons.jsx';

function App() {
  const [loading, setLoading] = useState(false);
  const [riskPrediction, setRiskPrediction] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (formData) => {
    setLoading(true);
    setError(null);
    setRiskPrediction(null);
    setRecommendation(null);

    try {
      const { risk, recommendation: rec } = await getFullAnalysis(formData);
      setRiskPrediction(risk);
      setRecommendation(rec);

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
    <div className="min-h-screen bg-gray-100">
      <ProfessionalHeader />

      <PageContainer
        title="Coronary Artery Disease Risk Assessment"
        subtitle="Enter patient clinical data to receive AI-powered risk stratification and evidence-based intervention recommendations."
      >
        {/* Patient Data Entry */}
        <PatientForm onSubmit={handleAnalyze} loading={loading} />

        {/* Error Display */}
        {error && (
          <div className="info-panel info-panel-critical">
            <div className="flex items-start gap-2">
              <Icon
                icon={MedicalIcons.error}
                size="md"
                className="text-critical-600 flex-shrink-0 mt-0.5"
              />
              <div>
                <h3 className="text-sm font-semibold text-critical-900 mb-1">Analysis Failed</h3>
                <p className="text-sm text-critical-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results Display */}
        {recommendation && (
          <div id="results" className="animate-fadeIn">
            <RecommendationPanel recommendation={recommendation} riskPrediction={riskPrediction} />
          </div>
        )}
      </PageContainer>
    </div>
  );
}

export default App;
