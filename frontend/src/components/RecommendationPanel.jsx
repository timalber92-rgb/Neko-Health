/**
 * RecommendationPanel Component
 *
 * Displays RL-based intervention recommendations:
 * - Recommended action with explanation
 * - Expected outcomes and risk reduction
 * - Comparison of current vs optimized health metrics
 * - Interactive simulation of alternative interventions
 */

import { useState } from "react";
import { simulateIntervention } from "../api/client";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// Action definitions with specific medications
const ACTIONS = [
  {
    id: 0,
    name: "Monitor Only",
    icon: "👁️",
    description: "Quarterly checkups with no active intervention",
    medications: [],
    details:
      "Regular cardiovascular check-ups every 3 months. No active medications prescribed.",
  },
  {
    id: 1,
    name: "Lifestyle Intervention",
    icon: "🏃",
    description: "Diet and exercise program with regular monitoring",
    medications: [],
    details:
      "Structured exercise program (150 min/week moderate activity), Mediterranean diet, smoking cessation support.",
  },
  {
    id: 2,
    name: "Single Medication",
    icon: "💊",
    description: "Single medication targeting cholesterol or blood pressure",
    medications: [
      "Statin (e.g., Atorvastatin 10-20mg) OR Beta-blocker (e.g., Metoprolol 50mg)",
    ],
    details:
      "Single medication to manage either cholesterol or blood pressure, combined with lifestyle counseling.",
  },
  {
    id: 3,
    name: "Combination Therapy",
    icon: "💊🏃",
    description: "Multiple medications plus supervised lifestyle program",
    medications: [
      "Statin (e.g., Atorvastatin 40mg)",
      "ACE Inhibitor (e.g., Lisinopril 10mg) OR Beta-blocker",
    ],
    details:
      "Combination of cholesterol-lowering and blood pressure medication, plus supervised lifestyle program.",
  },
  {
    id: 4,
    name: "Intensive Treatment",
    icon: "🏥",
    description: "Multiple medications with intensive lifestyle management",
    medications: [
      "High-dose Statin (e.g., Atorvastatin 80mg)",
      "ACE Inhibitor OR ARB",
      "Beta-blocker",
      "Antiplatelet (e.g., Aspirin 81mg)",
    ],
    details:
      "Multiple medications targeting cholesterol, blood pressure, and blood clotting, with intensive lifestyle coaching and cardiology follow-up.",
  },
];

// Metric labels and descriptions for display
const METRIC_LABELS = {
  trestbps: "Blood Pressure (mm Hg)",
  chol: "Cholesterol (mg/dl)",
  thalach: "Max Heart Rate (bpm)",
  oldpeak: "ST Depression (mm)",
};

const METRIC_DESCRIPTIONS = {
  trestbps:
    "High pressure damages artery walls over time, promoting plaque buildup",
  chol: "Excess cholesterol forms plaques that narrow arteries and restrict blood flow",
  thalach:
    "Lower rates may indicate reduced cardiac capacity or blocked arteries",
  oldpeak:
    "Higher values show more severe oxygen deprivation to heart muscle during exertion",
};

function MetricComparison({ simulation }) {
  if (!simulation) return null;

  const {
    current_metrics,
    optimized_metrics,
    current_risk,
    expected_risk,
    risk_reduction,
  } = simulation;

  // Prepare data for chart
  const chartData = Object.keys(current_metrics).map((key) => ({
    metric: METRIC_LABELS[key] || key,
    current: parseFloat(current_metrics[key].toFixed(2)),
    optimized: parseFloat(optimized_metrics[key].toFixed(2)),
  }));

  return (
    <div className="mt-6">
      <h4 className="text-lg font-semibold text-gray-800 mb-3">
        Health Metrics Comparison
      </h4>

      <ResponsiveContainer width="100%" height={250}>
        <BarChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 80 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="metric" angle={-45} textAnchor="end" height={100} />
          <YAxis />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
            }}
          />
          <Legend />
          <Bar
            dataKey="current"
            fill="#94a3b8"
            name="Current"
            radius={[8, 8, 0, 0]}
          />
          <Bar
            dataKey="optimized"
            fill="#0ea5e9"
            name="After Intervention"
            radius={[8, 8, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Risk Reduction Summary */}
      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="p-4 bg-gray-50 rounded-lg text-center">
          <div className="text-2xl font-bold text-gray-700">
            {current_risk.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Current Risk</div>
        </div>
        <div className="p-4 bg-blue-50 rounded-lg text-center">
          <div className="text-2xl font-bold text-primary-600">
            {expected_risk.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Expected Risk</div>
        </div>
        <div className="p-4 bg-green-50 rounded-lg text-center">
          <div className="text-2xl font-bold text-success-600">
            -{risk_reduction.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Risk Reduction</div>
        </div>
      </div>

      {/* Metric Descriptions */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h5 className="text-sm font-semibold text-gray-800 mb-2">
          Understanding Key Metrics:
        </h5>
        <div className="space-y-2">
          {Object.keys(current_metrics).map((key) => (
            <div key={key} className="text-xs text-gray-700">
              <span className="font-semibold">{METRIC_LABELS[key]}:</span>{" "}
              {METRIC_DESCRIPTIONS[key]}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function QValueChart({ qValues }) {
  if (!qValues) return null;

  // Convert Q-values object to array for chart
  const chartData = Object.entries(qValues).map(([action, value]) => ({
    action,
    qValue: parseFloat(value.toFixed(3)),
  }));

  return (
    <div className="mt-6">
      <h4 className="text-lg font-semibold text-gray-800 mb-3">
        Action Q-Values
      </h4>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 80 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="action" angle={-45} textAnchor="end" height={100} />
          <YAxis />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
            }}
          />
          <Bar
            dataKey="qValue"
            fill="#0ea5e9"
            name="Q-Value"
            radius={[8, 8, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-500 mt-2 text-center">
        Higher Q-values indicate better expected long-term outcomes
      </p>
    </div>
  );
}

export default function RecommendationPanel({ recommendation, patientData }) {
  const [simulation, setSimulation] = useState(null);
  const [simulatingAction, setSimulatingAction] = useState(null);
  const [simulatedActionId, setSimulatedActionId] = useState(null);
  const [error, setError] = useState(null);

  if (!recommendation) return null;

  const {
    action,
    action_name,
    description,
    cost,
    intensity,
    current_risk,
    expected_final_risk,
    expected_risk_reduction,
    q_values,
    rationale,
    risk_factors,
  } = recommendation;

  const recommendedAction = ACTIONS[action];

  const handleSimulate = async (actionId) => {
    setSimulatingAction(actionId);
    setError(null);

    try {
      const result = await simulateIntervention(patientData, actionId);
      setSimulation(result);
      setSimulatedActionId(actionId); // Track which action was simulated
    } catch (err) {
      setError(err.message);
      console.error("Simulation failed:", err);
    } finally {
      setSimulatingAction(null);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Recommended Intervention
      </h2>

      {/* Clinical Rationale Section */}
      {rationale && (
        <div className="mb-6 p-5 bg-blue-50 border-l-4 border-primary-500 rounded-r-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-2 flex items-center">
            <span className="mr-2">🩺</span>
            Clinical Assessment
          </h3>
          <p className="text-gray-700 leading-relaxed">{rationale}</p>
        </div>
      )}

      {/* Risk Factors Section */}
      {risk_factors &&
        risk_factors.details &&
        risk_factors.details.length > 0 && (
          <div className="mb-6 p-5 bg-amber-50 border-l-4 border-warning-500 rounded-r-lg">
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
              <span className="mr-2">⚠️</span>
              Identified Risk Factors
            </h3>
            <div className="flex flex-wrap gap-2 mb-3">
              {risk_factors.severe_count > 0 && (
                <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold">
                  {risk_factors.severe_count} Severe
                </span>
              )}
              {risk_factors.moderate_count > 0 && (
                <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-semibold">
                  {risk_factors.moderate_count} Moderate
                </span>
              )}
            </div>
            <ul className="space-y-1">
              {risk_factors.details.map((factor, index) => (
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
            <h3 className="text-2xl font-bold text-primary-700 mb-2">
              {action_name}
            </h3>
            <p className="text-gray-700 mb-3">{description}</p>

            {/* Medications Section */}
            {recommendedAction.medications &&
              recommendedAction.medications.length > 0 && (
                <div className="mb-3 p-3 bg-white rounded-lg border border-primary-200">
                  <h4 className="text-sm font-semibold text-gray-800 mb-2">
                    💊 Medications:
                  </h4>
                  <ul className="space-y-1">
                    {recommendedAction.medications.map((med, index) => (
                      <li
                        key={index}
                        className="text-sm text-gray-700 flex items-start"
                      >
                        <span className="mr-2 text-primary-600">•</span>
                        <span>{med}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            {/* Details */}
            {recommendedAction.details && (
              <p className="text-sm text-gray-600 mb-3 italic">
                {recommendedAction.details}
              </p>
            )}

            <div className="flex flex-wrap gap-4 text-sm">
              <div>
                <span className="font-semibold text-gray-700">Cost:</span>{" "}
                <span className="text-gray-600">{cost}</span>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Intensity:</span>{" "}
                <span className="text-gray-600">{intensity}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Expected Outcomes */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-800 mb-3">
          Expected Outcomes
        </h4>
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg text-center">
            <div className="text-2xl font-bold text-gray-700">
              {current_risk.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Current Risk</div>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg text-center border-2 border-primary-500">
            <div className="text-2xl font-bold text-primary-600">
              {expected_final_risk.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Expected Risk</div>
          </div>
          <div className="p-4 bg-green-50 rounded-lg text-center">
            <div className="text-2xl font-bold text-success-600">
              -{expected_risk_reduction.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Risk Reduction</div>
          </div>
        </div>
      </div>

      {/* Q-Values Chart */}
      {q_values && <QValueChart qValues={q_values} />}

      {/* Alternative Interventions */}
      <div className="mt-6">
        <h4 className="text-lg font-semibold text-gray-800 mb-3">
          Explore Alternative Interventions
        </h4>
        <p className="text-sm text-gray-600 mb-4">
          Click on any intervention to simulate its effect on health metrics
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {ACTIONS.map((act) => {
            const isRecommended = act.id === action;
            const isSimulated = act.id === simulatedActionId;
            const isSimulating = act.id === simulatingAction;

            return (
              <button
                key={act.id}
                onClick={() => handleSimulate(act.id)}
                disabled={simulatingAction !== null}
                className={`p-4 rounded-lg border-2 transition-all text-left ${
                  isSimulated
                    ? "border-green-500 bg-green-50 ring-2 ring-green-300"
                    : isRecommended
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-200 bg-white hover:border-primary-300 hover:bg-gray-50"
                } ${isSimulating ? "opacity-50 cursor-wait" : "cursor-pointer"}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">{act.icon}</span>
                    <span className="font-semibold text-gray-800 text-sm">
                      {act.name}
                    </span>
                  </div>
                  {isSimulated && !isSimulating && (
                    <span className="text-xs font-semibold text-green-600 bg-green-100 px-2 py-1 rounded">
                      Viewing
                    </span>
                  )}
                  {isRecommended && !isSimulated && (
                    <span className="text-xs font-semibold text-primary-600 bg-primary-100 px-2 py-1 rounded">
                      AI Recommended
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-600">{act.description}</p>
                {isSimulating && (
                  <div className="mt-2 text-xs text-primary-600 font-semibold">
                    Simulating...
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Simulation Results */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">Error: {error}</p>
        </div>
      )}

      {simulation && simulatedActionId !== null && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-lg font-semibold text-gray-800">
              Simulation Results: {ACTIONS[simulatedActionId].name}
            </h4>
            <span className="text-sm text-gray-600">
              {ACTIONS[simulatedActionId].icon}
            </span>
          </div>
          <MetricComparison simulation={simulation} />
        </div>
      )}

      {/* Information Box */}
      <div className="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
        <p className="text-sm text-gray-700">
          <strong>Note:</strong> These recommendations are based on established
          clinical guidelines and AI risk assessment. This is a demonstration
          system - always consult with healthcare professionals before making
          medical decisions.
        </p>
      </div>
    </div>
  );
}
