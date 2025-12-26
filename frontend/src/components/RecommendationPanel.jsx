/**
 * RecommendationPanel Component
 *
 * Displays comprehensive cardiovascular risk assessment and intervention recommendations:
 * - Risk score visualization with feature importance
 * - Disease detection and impact explanation
 * - Recommended action with clinical rationale
 * - Comparison table of all intervention options
 * - Expected outcomes and risk reduction for each option
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

// Risk level thresholds and styling
// These thresholds align with clinical cardiovascular risk stratification
const RISK_LEVELS = {
  low: {
    threshold: 20,
    label: 'Low Risk',
    color: 'text-success-600',
    bgColor: 'bg-success-100',
    borderColor: 'border-success-500',
    gaugeColor: '#22c55e',
  },
  moderate: {
    threshold: 50,
    label: 'Moderate Risk',
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

// Action definitions with specific medications
const ACTIONS = [
  {
    id: 0,
    name: 'Monitor Only',
    icon: '👁️',
    description: 'Quarterly checkups with no active intervention',
    medications: [],
    details: 'Regular cardiovascular check-ups every 3 months. No active medications prescribed.',
  },
  {
    id: 1,
    name: 'Lifestyle Modifications',
    icon: '🏃',
    description: 'Diet and exercise program with regular monitoring',
    medications: [],
    details:
      'Structured exercise program (150 min/week moderate activity), Mediterranean diet, smoking cessation support.',
  },
  {
    id: 2,
    name: 'Single Medication',
    icon: '💊',
    description: 'Single medication targeting cholesterol or blood pressure',
    medications: ['Statin (e.g., Atorvastatin 10-20mg) OR Beta-blocker (e.g., Metoprolol 50mg)'],
    details:
      'Single medication to manage either cholesterol or blood pressure, combined with lifestyle counseling.',
  },
  {
    id: 3,
    name: 'Combination Therapy',
    icon: '💊🏃',
    description: 'Multiple medications plus supervised lifestyle program',
    medications: [
      'Statin (e.g., Atorvastatin 40mg)',
      'ACE Inhibitor (e.g., Lisinopril 10mg) OR Beta-blocker',
    ],
    details:
      'Combination of cholesterol-lowering and blood pressure medication, plus supervised lifestyle program.',
  },
  {
    id: 4,
    name: 'Intensive Treatment',
    icon: '🏥',
    description: 'Multiple medications with intensive lifestyle management',
    medications: [
      'High-dose Statin (e.g., Atorvastatin 80mg)',
      'ACE Inhibitor OR ARB',
      'Beta-blocker',
      'Antiplatelet (e.g., Aspirin 81mg)',
    ],
    details:
      'Multiple medications targeting cholesterol, blood pressure, and blood clotting, with intensive lifestyle coaching and cardiology follow-up.',
  },
];

function getRiskLevel(riskScore) {
  if (riskScore < RISK_LEVELS.low.threshold) return RISK_LEVELS.low;
  if (riskScore < RISK_LEVELS.moderate.threshold) return RISK_LEVELS.moderate;
  return RISK_LEVELS.high;
}

function CircularGauge({ value, level }) {
  const radius = 80;
  const strokeWidth = 12;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg
        width={radius * 2 + strokeWidth * 2}
        height={radius * 2 + strokeWidth * 2}
        className="transform -rotate-90"
      >
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
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            domain={[0, 'auto']}
            label={{
              value: 'Importance (%)',
              position: 'insideBottom',
              offset: -5,
            }}
          />
          <YAxis type="category" dataKey="feature" />
          <Tooltip
            formatter={(value) => [`${value}%`, 'Importance']}
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
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

function InterventionComparisonTable({ allOptions }) {
  if (!allOptions || allOptions.length === 0) return null;

  return (
    <div className="mt-6">
      <h4 className="text-lg font-semibold text-gray-800 mb-3">
        Comparing All Intervention Options
      </h4>
      <p className="text-sm text-gray-600 mb-4">
        This table shows expected outcomes for all possible interventions, helping you understand
        why the recommended option is best for your risk level.
      </p>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Intervention
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                New Risk
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Risk Reduction
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cost
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Side Effects
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Monitoring
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {allOptions.map((option) => {
              const isRecommended = option.is_recommended;
              const isAlternative = option.is_alternative;
              const rowClass = isRecommended
                ? 'bg-primary-50 border-l-4 border-primary-500'
                : isAlternative
                  ? 'bg-blue-50 border-l-4 border-blue-400'
                  : '';

              return (
                <tr key={option.action_id} className={rowClass}>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-2xl mr-2">{ACTIONS[option.action_id]?.icon}</span>
                      <div>
                        <div className="text-sm font-medium text-gray-900 flex items-center">
                          {option.name}
                          {isRecommended && (
                            <span className="ml-2 px-2 py-0.5 text-xs font-semibold text-primary-700 bg-primary-200 rounded">
                              RECOMMENDED
                            </span>
                          )}
                          {isAlternative && !isRecommended && (
                            <span className="ml-2 px-2 py-0.5 text-xs font-semibold text-blue-700 bg-blue-200 rounded">
                              ALTERNATIVE
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">{option.description}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-sm font-semibold text-gray-900">
                      {option.new_risk.toFixed(1)}%
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      <div className="font-semibold text-success-600">
                        -{option.risk_reduction.toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-500">
                        ({option.pct_reduction.toFixed(1)}% relative)
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                    {option.cost}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                    {option.side_effects}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">{option.monitoring}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-gray-700">
          <strong>Why this recommendation?</strong> The recommended intervention is selected based
          on your risk tier, balancing effectiveness (risk reduction) with cost, side effects, and
          monitoring burden. The alternative option provides a different balance that may be
          appropriate depending on your personal circumstances.
        </p>
      </div>
    </div>
  );
}

export default function RecommendationPanel({ recommendation, riskPrediction }) {
  if (!recommendation) return null;

  // Handle both old and new API response formats
  const isNewFormat = 'recommended_action' in recommendation;

  const recommendedActionId = isNewFormat
    ? recommendation.recommended_action
    : recommendation.action;
  const actionName = isNewFormat ? recommendation.recommendation_name : recommendation.action_name;
  const description = isNewFormat
    ? recommendation.recommendation_description
    : recommendation.description;
  const rationale = recommendation.rationale;
  const allOptions = isNewFormat ? recommendation.all_options : null;

  // Get old format fields if available
  const cost = recommendation.cost;
  const intensity = recommendation.intensity;
  const riskFactors = recommendation.risk_factors;

  const recommendedAction = ACTIONS[recommendedActionId];

  // Extract risk prediction data
  const riskScore = riskPrediction?.risk_score;
  const featureImportance = riskPrediction?.feature_importance;
  const level = riskScore !== undefined ? getRiskLevel(riskScore) : null;

  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Risk Assessment & Personalized Recommendation
      </h2>

      {/* Risk Assessment Section */}
      {riskScore !== undefined && level && (
        <div className="mb-8 p-6 bg-gradient-to-br from-blue-50 to-white rounded-lg border border-blue-200">
          <h3 className="text-xl font-bold text-gray-800 mb-6">Your Cardiovascular Risk</h3>

          <div className="flex flex-col items-center">
            {/* Circular Gauge */}
            <CircularGauge value={riskScore} level={level} />

            {/* Risk Classification Badge */}
            <div
              className={`mt-6 px-6 py-3 rounded-full border-2 ${level.bgColor} ${level.borderColor}`}
            >
              <span className={`text-xl font-bold ${level.color}`}>{level.label}</span>
            </div>

            {/* Risk Interpretation */}
            <div className="mt-4 text-center max-w-2xl">
              <p className="text-sm text-gray-600">
                Based on your clinical indicators, you have a{' '}
                <strong className={level.color}>{riskScore.toFixed(1)}%</strong> probability of
                coronary artery disease (≥50% vessel narrowing).
                {level === RISK_LEVELS.high && (
                  <> Medical evaluation and intervention are recommended.</>
                )}
                {level === RISK_LEVELS.moderate && (
                  <> Regular monitoring and risk factor management are advised.</>
                )}
                {level === RISK_LEVELS.low && (
                  <> Continue monitoring and maintain a healthy lifestyle.</>
                )}
              </p>
            </div>
          </div>

          {/* Feature Importance Chart */}
          {featureImportance && <FeatureImportanceChart featureImportance={featureImportance} />}

          {/* Explanation */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="mb-3">
              <h4 className="text-sm font-bold text-gray-800 mb-2">
                What does this risk score mean?
              </h4>
              <p className="text-sm text-gray-700 mb-2">
                This score represents the probability of{' '}
                <strong>Coronary Artery Disease (CAD)</strong> - significant narrowing (≥50%
                blockage) in the arteries that supply blood to your heart muscle.
              </p>
            </div>

            {/* Life Quality and Expectancy Impact */}
            <div className="mb-3 p-3 bg-amber-50 rounded-lg border border-amber-300">
              <h4 className="text-sm font-bold text-gray-800 mb-2 flex items-center">
                <span className="mr-2">⚠️</span>
                Impact on Life Quality and Life Expectancy:
              </h4>
              <div className="space-y-2">
                <div>
                  <p className="text-xs font-semibold text-gray-800 mb-1">Quality of Life:</p>
                  <ul className="text-xs text-gray-700 ml-4 space-y-0.5">
                    <li>
                      • <strong>Physical Limitations:</strong> Reduced exercise tolerance, fatigue
                      during daily activities
                    </li>
                    <li>
                      • <strong>Angina Symptoms:</strong> Frequent chest pain limiting work, travel,
                      and recreation
                    </li>
                    <li>
                      • <strong>Psychological Impact:</strong> Anxiety about heart events,
                      depression from activity restrictions
                    </li>
                    <li>
                      • <strong>Treatment Burden:</strong> Daily medications, frequent doctor
                      visits, potential procedures (stents, bypass)
                    </li>
                  </ul>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-800 mb-1">Life Expectancy:</p>
                  <ul className="text-xs text-gray-700 ml-4 space-y-0.5">
                    <li>
                      • <strong>Untreated CAD:</strong> Reduces life expectancy by 7-10 years on
                      average, with 3-5x higher risk of heart attack
                    </li>
                    <li>
                      • <strong>With Treatment:</strong> Modern interventions can restore
                      near-normal life expectancy if started early
                    </li>
                    <li>
                      • <strong>Post-Heart Attack:</strong> 5-year survival rate is ~75%, with
                      higher risk of recurrent events
                    </li>
                  </ul>
                </div>
                <div className="pt-2 mt-2 border-t border-amber-300">
                  <p className="text-xs font-semibold text-green-700">
                    ✓ Good News: Early detection and intervention dramatically improve outcomes
                  </p>
                </div>
              </div>
            </div>

            <div className="mb-3">
              <h4 className="text-sm font-bold text-gray-800 mb-2">
                What conditions could develop?
              </h4>
              <p className="text-sm text-gray-700 mb-2">
                If left untreated, coronary artery disease can lead to:
              </p>
              <ul className="text-sm text-gray-700 ml-4 space-y-1">
                <li>
                  • <strong>Angina</strong> - chest pain or discomfort due to reduced blood flow
                </li>
                <li>
                  • <strong>Heart Attack (Myocardial Infarction)</strong> - if a coronary artery
                  becomes completely blocked
                </li>
                <li>
                  • <strong>Heart Failure</strong> - weakened heart muscle from chronic oxygen
                  deprivation
                </li>
                <li>
                  • <strong>Arrhythmias</strong> - irregular heartbeats due to damaged heart tissue
                </li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-bold text-gray-800 mb-2">
                Understanding the top risk factors:
              </h4>
              <p className="text-sm text-gray-700">
                The chart above shows which of your clinical measurements contribute most to this
                prediction. Higher importance means that factor has more influence on your
                individual risk assessment.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Clinical Rationale Section */}
      {rationale && (
        <div className="mb-6 p-5 bg-blue-50 border-l-4 border-primary-500 rounded-r-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-2 flex items-center">
            <span className="mr-2">🩺</span>
            Clinical Rationale
          </h3>
          <p className="text-gray-700 leading-relaxed">{rationale}</p>
        </div>
      )}

      {/* Risk Factors Section (old format) */}
      {riskFactors && riskFactors.details && riskFactors.details.length > 0 && (
        <div className="mb-6 p-5 bg-amber-50 border-l-4 border-warning-500 rounded-r-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
            <span className="mr-2">⚠️</span>
            Identified Risk Factors
          </h3>
          <div className="flex flex-wrap gap-2 mb-3">
            {riskFactors.severe_count > 0 && (
              <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold">
                {riskFactors.severe_count} Severe
              </span>
            )}
            {riskFactors.moderate_count > 0 && (
              <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-semibold">
                {riskFactors.moderate_count} Moderate
              </span>
            )}
          </div>
          <ul className="space-y-1">
            {riskFactors.details.map((factor, index) => (
              <li key={index} className="text-gray-700 flex items-start">
                <span className="mr-2 text-warning-600">•</span>
                <span className="capitalize">{factor}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommended Action */}
      <div className="p-6 bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg border-2 border-primary-500 mb-6">
        <div className="flex items-start">
          <div className="text-4xl mr-4">{recommendedAction.icon}</div>
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-primary-700 mb-2">{actionName}</h3>
            <p className="text-gray-700 mb-3">{description}</p>

            {/* Medications Section */}
            {recommendedAction.medications && recommendedAction.medications.length > 0 && (
              <div className="mb-3 p-3 bg-white rounded-lg border border-primary-200">
                <h4 className="text-sm font-semibold text-gray-800 mb-2">💊 Medications:</h4>
                <ul className="space-y-1">
                  {recommendedAction.medications.map((med, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start">
                      <span className="mr-2 text-primary-600">•</span>
                      <span>{med}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Details */}
            {recommendedAction.details && (
              <p className="text-sm text-gray-600 mb-3 italic">{recommendedAction.details}</p>
            )}

            {/* Cost and Intensity (old format) */}
            {(cost || intensity) && (
              <div className="flex flex-wrap gap-4 text-sm">
                {cost && (
                  <div>
                    <span className="font-semibold text-gray-700">Cost:</span>{' '}
                    <span className="text-gray-600">{cost}</span>
                  </div>
                )}
                {intensity && (
                  <div>
                    <span className="font-semibold text-gray-700">Intensity:</span>{' '}
                    <span className="text-gray-600">{intensity}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Intervention Comparison Table (new format) */}
      {allOptions && <InterventionComparisonTable allOptions={allOptions} />}

      {/* Information Box */}
      <div className="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
        <p className="text-sm text-gray-700">
          <strong>Note:</strong> These recommendations are based on risk-stratified analysis and
          clinical guidelines. This is a demonstration system - always consult with healthcare
          professionals before making medical decisions.
        </p>
      </div>
    </div>
  );
}
