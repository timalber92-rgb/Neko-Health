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

// Action definitions matching backend
const ACTIONS = [
  {
    id: 0,
    name: "Monitor Only",
    icon: "👁️",
    description: "Quarterly checkups with no active intervention",
  },
  {
    id: 1,
    name: "Lifestyle Intervention",
    icon: "🏃",
    description: "Diet and exercise program with regular monitoring",
  },
  {
    id: 2,
    name: "Single Medication",
    icon: "💊",
    description: "Single medication (e.g., statin or beta-blocker)",
  },
  {
    id: 3,
    name: "Combination Therapy",
    icon: "💊🏃",
    description: "Medication plus supervised lifestyle program",
  },
  {
    id: 4,
    name: "Intensive Treatment",
    icon: "🏥",
    description: "Multiple medications with intensive lifestyle management",
  },
];

// Metric labels for display
const METRIC_LABELS = {
  trestbps: "Blood Pressure (mm Hg)",
  chol: "Cholesterol (mg/dl)",
  thalach: "Max Heart Rate (bpm)",
  oldpeak: "ST Depression (mm)",
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

      {/* Recommended Action */}
      <div className="p-6 bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg border-2 border-primary-500 mb-6">
        <div className="flex items-start">
          <div className="text-4xl mr-4">{recommendedAction.icon}</div>
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-primary-700 mb-2">
              {action_name}
            </h3>
            <p className="text-gray-700 mb-3">{description}</p>
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
          <strong>Note:</strong> This is an AI-powered recommendation based on
          reinforcement learning. Always consult with healthcare professionals
          before making medical decisions.
        </p>
      </div>
    </div>
  );
}
