/**
 * RiskDisplay Component
 *
 * Displays cardiovascular disease risk prediction results:
 * - Circular risk gauge with color coding
 * - Risk classification label
 * - Feature importance bar chart showing top risk factors
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

// Risk level thresholds and styling
const RISK_LEVELS = {
  low: {
    threshold: 30,
    label: 'Low Risk',
    color: 'text-success-600',
    bgColor: 'bg-success-100',
    borderColor: 'border-success-500',
    gaugeColor: '#22c55e',
  },
  medium: {
    threshold: 70,
    label: 'Medium Risk',
    color: 'text-warning-600',
    bgColor: 'bg-warning-100',
    borderColor: 'border-warning-500',
    gaugeColor: '#f59e0b',
  },
  high: {
    threshold: 100,
    label: 'High Risk',
    color: 'text-danger-600',
    bgColor: 'bg-danger-100',
    borderColor: 'border-danger-500',
    gaugeColor: '#ef4444',
  },
};

// Feature name mapping for better display
const FEATURE_LABELS = {
  age: 'Age',
  sex: 'Sex',
  cp: 'Chest Pain Type',
  trestbps: 'Blood Pressure',
  chol: 'Cholesterol',
  fbs: 'Fasting Blood Sugar',
  restecg: 'Resting ECG',
  thalach: 'Max Heart Rate',
  exang: 'Exercise Angina',
  oldpeak: 'ST Depression',
  slope: 'ST Slope',
  ca: 'Major Vessels',
  thal: 'Thalassemia',
};

function getRiskLevel(riskScore) {
  if (riskScore < RISK_LEVELS.low.threshold) return RISK_LEVELS.low;
  if (riskScore < RISK_LEVELS.medium.threshold) return RISK_LEVELS.medium;
  return RISK_LEVELS.high;
}

function CircularGauge({ value, level }) {
  const radius = 80;
  const strokeWidth = 12;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={radius * 2 + strokeWidth * 2} height={radius * 2 + strokeWidth * 2} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={radius + strokeWidth}
          cy={radius + strokeWidth}
          r={radius}
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx={radius + strokeWidth}
          cy={radius + strokeWidth}
          r={radius}
          stroke={level.gaugeColor}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      {/* Center text */}
      <div className="absolute flex flex-col items-center">
        <span className="text-4xl font-bold text-gray-800">{value.toFixed(1)}%</span>
        <span className="text-sm text-gray-600">Risk Score</span>
      </div>
    </div>
  );
}

function FeatureImportanceChart({ featureImportance }) {
  // Convert feature importance object to array and sort by importance
  const chartData = Object.entries(featureImportance)
    .map(([feature, importance]) => ({
      feature: FEATURE_LABELS[feature] || feature,
      importance: (importance * 100).toFixed(1), // Convert to percentage
      importanceValue: importance,
    }))
    .sort((a, b) => b.importanceValue - a.importanceValue)
    .slice(0, 5); // Top 5 features

  // Color gradient for bars
  const colors = ['#0ea5e9', '#38bdf8', '#7dd3fc', '#bae6fd', '#e0f2fe'];

  return (
    <div className="mt-6">
      <h4 className="text-lg font-semibold text-gray-800 mb-3">Top Risk Factors</h4>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" domain={[0, 'auto']} label={{ value: 'Importance (%)', position: 'insideBottom', offset: -5 }} />
          <YAxis type="category" dataKey="feature" />
          <Tooltip
            formatter={(value) => [`${value}%`, 'Importance']}
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
          />
          <Bar dataKey="importance" radius={[0, 8, 8, 0]}>
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={colors[index]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-500 mt-2 text-center">
        Features ranked by their contribution to the risk prediction
      </p>
    </div>
  );
}

export default function RiskDisplay({ prediction }) {
  if (!prediction) return null;

  const { risk_score, classification, feature_importance, has_disease } = prediction;
  const level = getRiskLevel(risk_score);

  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Risk Assessment</h2>

      <div className="flex flex-col items-center">
        {/* Circular Gauge */}
        <CircularGauge value={risk_score} level={level} />

        {/* Risk Classification Badge */}
        <div className={`mt-6 px-6 py-3 rounded-full border-2 ${level.bgColor} ${level.borderColor}`}>
          <span className={`text-xl font-bold ${level.color}`}>{classification}</span>
        </div>

        {/* Disease Prediction */}
        <div className="mt-4 text-center">
          <p className="text-gray-700">
            {has_disease ? (
              <>
                <span className="font-semibold text-danger-600">Cardiovascular disease detected</span>
                <br />
                <span className="text-sm text-gray-600">
                  Based on clinical features, intervention recommended
                </span>
              </>
            ) : (
              <>
                <span className="font-semibold text-success-600">No disease detected</span>
                <br />
                <span className="text-sm text-gray-600">
                  Continue monitoring and maintain healthy lifestyle
                </span>
              </>
            )}
          </p>
        </div>
      </div>

      {/* Feature Importance Chart */}
      {feature_importance && <FeatureImportanceChart featureImportance={feature_importance} />}

      {/* Explanation */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-gray-700">
          <strong>How to interpret:</strong> The risk score represents the probability of cardiovascular disease
          based on your clinical measurements. The top risk factors show which features contribute most to this prediction.
        </p>
      </div>
    </div>
  );
}
