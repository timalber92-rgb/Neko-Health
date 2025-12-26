/**
 * RecommendationPanel Component
 *
 * Professional clinical decision support display:
 * - Risk score visualization with feature importance
 * - Disease detection and impact explanation
 * - Recommended intervention with clinical rationale
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
import { Icon, MedicalIcons, ActionIcon } from '../utils/icons.jsx';

// Risk level thresholds and styling
// These thresholds align with clinical cardiovascular risk stratification
const RISK_LEVELS = {
  low: {
    threshold: 20,
    label: 'Low Risk',
    color: 'text-normal-700',
    bgColor: 'bg-normal-100',
    borderColor: 'border-normal-500',
    gaugeColor: '#16a34a',
  },
  moderate: {
    threshold: 50,
    label: 'Moderate Risk',
    color: 'text-warning-700',
    bgColor: 'bg-warning-100',
    borderColor: 'border-warning-500',
    gaugeColor: '#d97706',
  },
  high: {
    threshold: 100,
    label: 'High Risk',
    color: 'text-critical-700',
    bgColor: 'bg-critical-100',
    borderColor: 'border-critical-500',
    gaugeColor: '#dc2626',
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
    description: 'Quarterly checkups with no active intervention',
    medications: [],
    details: 'Regular cardiovascular check-ups every 3 months. No active medications prescribed.',
  },
  {
    id: 1,
    name: 'Lifestyle Modifications',
    description: 'Diet and exercise program with regular monitoring',
    medications: [],
    details:
      'Structured exercise program (150 min/week moderate activity), Mediterranean diet, smoking cessation support.',
  },
  {
    id: 2,
    name: 'Single Medication',
    description: 'Single medication targeting cholesterol or blood pressure',
    medications: ['Statin (e.g., Atorvastatin 10-20mg) OR Beta-blocker (e.g., Metoprolol 50mg)'],
    details:
      'Single medication to manage either cholesterol or blood pressure, combined with lifestyle counseling.',
  },
  {
    id: 3,
    name: 'Combination Therapy',
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
  const radius = 60;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg
        width={radius * 2 + strokeWidth * 2}
        height={radius * 2 + strokeWidth * 2}
        className="transform -rotate-90"
        aria-hidden="true"
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
          className="transition-all duration-700 ease-out"
        />
      </svg>
      {/* Center text */}
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold text-gray-900">{value.toFixed(1)}%</span>
        <span className="text-xs text-gray-600 font-medium">CAD Risk</span>
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

  // Professional clinical color gradient
  const colors = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe'];

  return (
    <div className="mt-4">
      <h4 className="section-subtitle flex items-center gap-2">
        <Icon icon={MedicalIcons.chart} size="sm" className="text-gray-500" />
        Top Contributing Risk Factors
      </h4>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 20, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            type="number"
            domain={[0, 'auto']}
            tick={{ fontSize: 12, fill: '#6b7280' }}
            label={{
              value: 'Contribution (%)',
              position: 'insideBottom',
              offset: -3,
              style: { fontSize: 11, fill: '#6b7280' },
            }}
          />
          <YAxis type="category" dataKey="feature" tick={{ fontSize: 12, fill: '#374151' }} />
          <Tooltip
            formatter={(value) => [`${value}%`, 'Contribution']}
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              fontSize: '12px',
            }}
          />
          <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={colors[index]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-600 mt-2">
        Clinical parameters ranked by contribution to overall risk assessment
      </p>
    </div>
  );
}

function InterventionComparisonTable({ allOptions }) {
  if (!allOptions || allOptions.length === 0) return null;

  return (
    <div className="mt-6">
      <h4 className="section-subtitle flex items-center gap-2">
        <Icon icon={MedicalIcons.document} size="sm" className="text-gray-500" />
        Intervention Options Comparison
      </h4>
      <p className="text-sm text-gray-600 mb-4">
        Expected outcomes for all possible interventions, ranked by clinical appropriateness for the
        assessed risk level.
      </p>

      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th>Intervention</th>
              <th>New Risk</th>
              <th>Risk Reduction</th>
              <th>Cost</th>
              <th>Side Effects</th>
              <th>Monitoring</th>
            </tr>
          </thead>
          <tbody>
            {allOptions.map((option) => {
              const isRecommended = option.is_recommended;
              const isAlternative = option.is_alternative;
              const rowClass = isRecommended
                ? 'bg-clinical-50 border-l-4 border-clinical-600'
                : isAlternative
                  ? 'bg-info-50 border-l-4 border-info-400'
                  : '';

              return (
                <tr key={option.action_id} className={rowClass}>
                  <td>
                    <div className="flex items-center gap-2">
                      <ActionIcon action={option.action_id} size="md" />
                      <div>
                        <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
                          {option.name}
                          {isRecommended && <span className="badge badge-info">Recommended</span>}
                          {isAlternative && !isRecommended && (
                            <span className="badge badge-neutral">Alternative</span>
                          )}
                        </div>
                        <div className="text-xs text-gray-600 mt-0.5">{option.description}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div className="font-semibold text-gray-900">{option.new_risk.toFixed(1)}%</div>
                  </td>
                  <td>
                    <div>
                      <div className="font-semibold text-normal-700">
                        -{option.risk_reduction.toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-600">
                        ({option.pct_reduction.toFixed(1)}% relative)
                      </div>
                    </div>
                  </td>
                  <td className="text-gray-700">{option.cost}</td>
                  <td className="text-gray-700">{option.side_effects}</td>
                  <td className="text-gray-700">{option.monitoring}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-4 info-panel info-panel-clinical">
        <div className="flex items-start gap-2">
          <Icon
            icon={MedicalIcons.infoSolid}
            size="sm"
            className="text-clinical-600 flex-shrink-0 mt-0.5"
          />
          <div className="text-sm text-gray-700">
            <strong>Clinical Rationale:</strong> The recommended intervention is selected based on
            risk stratification, balancing therapeutic effectiveness with treatment burden, cost
            considerations, and monitoring requirements. Alternative options may be appropriate
            based on patient-specific factors.
          </div>
        </div>
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
      <div className="card-header">
        <h3 className="section-title">
          <Icon icon={MedicalIcons.heartSolid} size="md" className="text-critical-600" />
          Clinical Risk Assessment & Recommendation
        </h3>
      </div>

      {/* Risk Assessment Section */}
      {riskScore !== undefined && level && (
        <div className="card-section">
          <div className="info-panel info-panel-clinical">
            <h4 className="section-subtitle flex items-center gap-2 mb-4">
              <Icon icon={MedicalIcons.chart} size="sm" className="text-clinical-600" />
              Cardiovascular Risk Score
            </h4>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Circular Gauge */}
              <div className="flex flex-col items-center justify-center">
                <CircularGauge value={riskScore} level={level} />

                {/* Risk Classification Badge */}
                <div
                  className={`mt-4 badge badge-${level === RISK_LEVELS.low ? 'normal' : level === RISK_LEVELS.moderate ? 'warning' : 'critical'} px-4 py-1.5 text-sm font-semibold`}
                >
                  {level.label}
                </div>

                {/* Risk Interpretation */}
                <div className="mt-3 text-center max-w-md">
                  <p className="text-sm text-gray-700 leading-relaxed">
                    <strong className={level.color}>{riskScore.toFixed(1)}%</strong> probability of
                    coronary artery disease (≥50% vessel stenosis).
                    {level === RISK_LEVELS.high && (
                      <> Immediate medical evaluation and intervention recommended.</>
                    )}
                    {level === RISK_LEVELS.moderate && (
                      <> Regular monitoring and risk factor management advised.</>
                    )}
                    {level === RISK_LEVELS.low && (
                      <> Continue preventive care and healthy lifestyle.</>
                    )}
                  </p>
                </div>
              </div>

              {/* Feature Importance Chart */}
              {featureImportance && (
                <div>
                  <FeatureImportanceChart featureImportance={featureImportance} />
                </div>
              )}
            </div>
          </div>

          {/* Clinical Education Panels */}
          <div className="mt-4 space-y-3">
            <div className="info-panel info-panel-info">
              <div className="flex items-start gap-2">
                <Icon
                  icon={MedicalIcons.infoSolid}
                  size="sm"
                  className="text-info-600 flex-shrink-0 mt-0.5"
                />
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-1">
                    Understanding Coronary Artery Disease (CAD)
                  </h5>
                  <p className="text-sm text-gray-700">
                    This score represents the probability of significant stenosis (≥50% blockage) in
                    coronary arteries that supply blood to the myocardium. CAD results from
                    atherosclerotic plaque buildup, restricting oxygen delivery to heart tissue.
                  </p>
                </div>
              </div>
            </div>

            {/* Life Quality and Expectancy Impact */}
            <div className="info-panel info-panel-warning">
              <div className="flex items-start gap-2">
                <Icon
                  icon={MedicalIcons.warningSolid}
                  size="sm"
                  className="text-warning-600 flex-shrink-0 mt-0.5"
                />
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-2">
                    Clinical Impact on Morbidity and Mortality
                  </h5>
                  <div className="space-y-2 text-xs text-gray-700">
                    <div>
                      <p className="font-semibold text-gray-800 mb-1">Quality of Life Impact:</p>
                      <ul className="ml-4 space-y-0.5 list-disc">
                        <li>
                          <strong>Physical:</strong> Reduced exercise tolerance, exertional fatigue
                        </li>
                        <li>
                          <strong>Angina:</strong> Chest pain limiting activities of daily living
                        </li>
                        <li>
                          <strong>Psychological:</strong> Anxiety regarding cardiac events
                        </li>
                        <li>
                          <strong>Treatment burden:</strong> Medications, monitoring, potential
                          revascularization
                        </li>
                      </ul>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-800 mb-1">Mortality Risk:</p>
                      <ul className="ml-4 space-y-0.5 list-disc">
                        <li>
                          <strong>Untreated:</strong> 7-10 year reduction in life expectancy; 3-5x
                          increased MI risk
                        </li>
                        <li>
                          <strong>With intervention:</strong> Near-normal life expectancy if treated
                          early
                        </li>
                        <li>
                          <strong>Post-MI:</strong> ~75% 5-year survival; increased recurrent event
                          risk
                        </li>
                      </ul>
                    </div>
                    <div className="pt-2 mt-2 border-t border-warning-200 flex items-center gap-1">
                      <Icon
                        icon={MedicalIcons.successSolid}
                        size="xs"
                        className="text-normal-600"
                      />
                      <p className="font-semibold text-normal-700">
                        Early detection and evidence-based intervention significantly improve
                        outcomes
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="info-panel">
              <div className="flex items-start gap-2">
                <Icon
                  icon={MedicalIcons.document}
                  size="sm"
                  className="text-gray-500 flex-shrink-0 mt-0.5"
                />
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-1">
                    Potential Clinical Sequelae
                  </h5>
                  <p className="text-xs text-gray-700 mb-2">
                    Untreated coronary artery disease may progress to:
                  </p>
                  <ul className="text-xs text-gray-700 ml-4 space-y-1 list-disc">
                    <li>
                      <strong>Stable Angina:</strong> Exertional chest pain due to myocardial
                      ischemia
                    </li>
                    <li>
                      <strong>Acute MI:</strong> Complete arterial occlusion causing myocardial
                      necrosis
                    </li>
                    <li>
                      <strong>Heart Failure:</strong> Chronic ischemia leading to reduced ejection
                      fraction
                    </li>
                    <li>
                      <strong>Arrhythmias:</strong> Electrical instability from damaged myocardium
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Clinical Rationale Section */}
      {rationale && (
        <div className="card-section">
          <div className="info-panel info-panel-clinical">
            <div className="flex items-start gap-2">
              <Icon
                icon={MedicalIcons.clinical}
                size="md"
                className="text-clinical-600 flex-shrink-0 mt-0.5"
              />
              <div>
                <h4 className="section-subtitle mb-2">Clinical Rationale</h4>
                <p className="text-sm text-gray-700 leading-relaxed">{rationale}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Risk Factors Section (old format) */}
      {riskFactors && riskFactors.details && riskFactors.details.length > 0 && (
        <div className="card-section">
          <div className="info-panel info-panel-warning">
            <div className="flex items-start gap-2">
              <Icon
                icon={MedicalIcons.warningSolid}
                size="md"
                className="text-warning-600 flex-shrink-0 mt-0.5"
              />
              <div>
                <h4 className="section-subtitle mb-3">Identified Risk Factors</h4>
                <div className="flex flex-wrap gap-2 mb-3">
                  {riskFactors.severe_count > 0 && (
                    <span className="badge badge-critical">{riskFactors.severe_count} Severe</span>
                  )}
                  {riskFactors.moderate_count > 0 && (
                    <span className="badge badge-warning">
                      {riskFactors.moderate_count} Moderate
                    </span>
                  )}
                </div>
                <ul className="space-y-1 text-sm">
                  {riskFactors.details.map((factor, index) => (
                    <li key={index} className="text-gray-700 flex items-start">
                      <span className="mr-2 text-warning-600">•</span>
                      <span className="capitalize">{factor}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recommended Action */}
      <div className="card-section">
        <div className="info-panel border-clinical-500 bg-clinical-50 border-l-4">
          <div className="flex items-start gap-3">
            <ActionIcon action={recommendedActionId} size="xl" className="flex-shrink-0" />
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h4 className="text-lg font-semibold text-gray-900">{actionName}</h4>
                <span className="badge badge-info">Recommended</span>
              </div>
              <p className="text-sm text-gray-700 mb-3">{description}</p>

              {/* Medications Section */}
              {recommendedAction.medications && recommendedAction.medications.length > 0 && (
                <div className="mb-3 p-3 bg-white rounded border border-clinical-200">
                  <div className="flex items-center gap-2 mb-2">
                    <Icon icon={MedicalIcons.medication} size="sm" className="text-clinical-600" />
                    <h5 className="text-sm font-semibold text-gray-800">Pharmacotherapy:</h5>
                  </div>
                  <ul className="space-y-1">
                    {recommendedAction.medications.map((med, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="mr-2 text-clinical-600">•</span>
                        <span>{med}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Details */}
              {recommendedAction.details && (
                <p className="text-sm text-gray-600 leading-relaxed">{recommendedAction.details}</p>
              )}

              {/* Cost and Intensity (old format) */}
              {(cost || intensity) && (
                <div className="flex flex-wrap gap-4 text-sm mt-3 pt-3 border-t border-clinical-200">
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
      </div>

      {/* Intervention Comparison Table (new format) */}
      {allOptions && (
        <div className="card-section">
          <InterventionComparisonTable allOptions={allOptions} />
        </div>
      )}

      {/* Clinical Disclaimer */}
      <div className="mt-6 info-panel info-panel-warning">
        <div className="flex items-start gap-2">
          <Icon
            icon={MedicalIcons.shield}
            size="sm"
            className="text-warning-600 flex-shrink-0 mt-0.5"
          />
          <div className="text-xs text-gray-700">
            <strong>Clinical Decision Support Tool:</strong> This system provides risk-stratified
            recommendations based on validated clinical guidelines and machine learning analysis.
            Recommendations are for informational and educational purposes. All clinical decisions
            should be made in consultation with qualified healthcare providers considering
            patient-specific factors, comorbidities, and preferences. This is a demonstration system
            for educational purposes.
          </div>
        </div>
      </div>
    </div>
  );
}
