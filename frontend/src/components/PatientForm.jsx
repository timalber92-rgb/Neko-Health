/**
 * PatientForm Component
 *
 * Professional clinical data entry form for cardiovascular risk assessment.
 * Features: 13 clinical parameters, validation, example patient profiles
 */

import { useState } from 'react';
import { Icon, MedicalIcons } from '../utils/icons.jsx';
import clsx from 'clsx';

// Example patient profiles for quick testing
const EXAMPLE_PATIENTS = {
  healthy: {
    mrn: 'MRN-2847563',
    initials: 'J.C.',
    riskCategory: 'Low Risk',
    age: '45y',
    summary: 'Healthy vitals, active lifestyle, no significant risk factors',
    data: {
      age: 45,
      sex: 1,
      cp: 1,
      trestbps: 120,
      chol: 180,
      fbs: 0,
      restecg: 0,
      thalach: 170,
      exang: 0,
      oldpeak: 0.5,
      slope: 2,
      ca: 0,
      thal: 3,
    },
  },
  moderate: {
    mrn: 'MRN-3951847',
    initials: 'R.M.',
    riskCategory: 'Moderate Risk',
    age: '63y',
    summary: 'Elevated cholesterol (233 mg/dL), HTN (145/90), T2DM',
    data: {
      age: 63,
      sex: 1,
      cp: 3,
      trestbps: 145,
      chol: 233,
      fbs: 1,
      restecg: 0,
      thalach: 150,
      exang: 0,
      oldpeak: 2.3,
      slope: 2,
      ca: 0,
      thal: 6,
    },
  },
  high: {
    mrn: 'MRN-4762091',
    initials: 'W.T.',
    riskCategory: 'High Risk',
    age: '58y',
    summary: 'Multiple risk factors: HTN, hyperlipidemia, 1-vessel CAD',
    data: {
      age: 58,
      sex: 1,
      cp: 2,
      trestbps: 140,
      chol: 230,
      fbs: 0,
      restecg: 0,
      thalach: 150,
      exang: 0,
      oldpeak: 1.5,
      slope: 2,
      ca: 1,
      thal: 6,
    },
  },
};

// Field definitions with validation and help text
const FIELD_CONFIG = [
  {
    name: 'age',
    label: 'Age',
    type: 'number',
    min: 0,
    max: 120,
    step: 1,
    unit: 'years',
    help: 'Risk increases with age as arteries stiffen and plaque accumulates over time (critical after 45 for men, 55 for women)',
  },
  {
    name: 'sex',
    label: 'Sex',
    type: 'select',
    options: [
      { value: 0, label: 'Female' },
      { value: 1, label: 'Male' },
    ],
    help: "Men have higher early risk due to lower estrogen; women's risk rises after menopause when estrogen protection decreases",
  },
  {
    name: 'cp',
    label: 'Chest Pain Type',
    type: 'select',
    options: [
      { value: 1, label: 'Type 1 - Typical Angina' },
      { value: 2, label: 'Type 2 - Atypical Angina' },
      { value: 3, label: 'Type 3 - Non-Anginal Pain' },
      { value: 4, label: 'Type 4 - Asymptomatic' },
    ],
    help: 'Typical angina (pressure/tightness during exertion, relieved by rest) strongly suggests blocked arteries reducing oxygen to heart',
  },
  {
    name: 'trestbps',
    label: 'Resting Blood Pressure',
    type: 'number',
    min: 50,
    max: 250,
    step: 1,
    unit: 'mm Hg',
    help: 'High pressure damages artery walls, promoting plaque buildup (Normal: <120, Elevated: 120-129, High: ≥130)',
  },
  {
    name: 'chol',
    label: 'Serum Cholesterol',
    type: 'number',
    min: 100,
    max: 600,
    step: 1,
    unit: 'mg/dl',
    help: 'Excess cholesterol deposits in artery walls, forming plaques that narrow vessels and restrict blood flow (high: ≥240)',
  },
  {
    name: 'fbs',
    label: 'Fasting Blood Sugar',
    type: 'select',
    options: [
      { value: 0, label: '≤ 120 mg/dl (Normal)' },
      { value: 1, label: '> 120 mg/dl (Elevated)' },
    ],
    help: 'High blood sugar damages blood vessels and nerves over time, accelerating atherosclerosis (>120 indicates diabetes risk)',
  },
  {
    name: 'restecg',
    label: 'Resting ECG',
    type: 'select',
    options: [
      { value: 0, label: 'Normal' },
      { value: 1, label: 'ST-T Wave Abnormality' },
      { value: 2, label: 'Left Ventricular Hypertrophy' },
    ],
    help: 'Abnormalities reveal heart strain from working harder (hypertrophy) or insufficient blood flow causing electrical changes',
  },
  {
    name: 'thalach',
    label: 'Maximum Heart Rate',
    type: 'number',
    min: 50,
    max: 250,
    step: 1,
    unit: 'bpm',
    help: "Lower maximum rate during stress test suggests heart can't pump efficiently due to weak muscle or blocked arteries",
  },
  {
    name: 'exang',
    label: 'Exercise Induced Angina',
    type: 'select',
    options: [
      { value: 0, label: 'No' },
      { value: 1, label: 'Yes' },
    ],
    help: "Pain during exertion indicates narrowed arteries can't deliver enough oxygen when heart demands increase during activity",
  },
  {
    name: 'oldpeak',
    label: 'ST Depression',
    type: 'number',
    min: 0,
    max: 10,
    step: 0.1,
    unit: 'mm',
    help: 'ECG dip during exercise shows heart muscle not getting enough oxygen (ischemia). Greater depression = more severe blockage',
  },
  {
    name: 'slope',
    label: 'ST Segment Slope',
    type: 'select',
    options: [
      { value: 1, label: 'Upsloping' },
      { value: 2, label: 'Flat' },
      { value: 3, label: 'Downsloping' },
    ],
    help: 'ECG pattern shape at peak exercise. Downsloping/flat indicates heart struggling to get oxygen; upsloping is healthier response',
  },
  {
    name: 'ca',
    label: 'Major Vessels',
    type: 'select',
    options: [
      { value: 0, label: '0 vessels' },
      { value: 1, label: '1 vessel' },
      { value: 2, label: '2 vessels' },
      { value: 3, label: '3 vessels' },
    ],
    help: 'Fluoroscopy reveals blocked coronary arteries. More blocked vessels = less blood reaching heart muscle = higher risk',
  },
  {
    name: 'thal',
    label: 'Thalassemia',
    type: 'select',
    options: [
      { value: 3, label: 'Normal' },
      { value: 6, label: 'Fixed Defect' },
      { value: 7, label: 'Reversible Defect' },
    ],
    help: 'Nuclear scan shows heart perfusion. Fixed defects indicate permanent damage (scar); reversible means blockage reduces blood flow',
  },
];

export default function PatientForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState(EXAMPLE_PATIENTS.moderate.data);
  const [errors, setErrors] = useState({});
  const [selectedPatient, setSelectedPatient] = useState('moderate');

  const handleChange = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: parseFloat(value) }));
    // Clear selected patient when manually editing
    setSelectedPatient(null);
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};

    FIELD_CONFIG.forEach((field) => {
      const value = formData[field.name];

      if (value === undefined || value === null || value === '') {
        newErrors[field.name] = 'This field is required';
        return;
      }

      if (field.type === 'number') {
        if (value < field.min || value > field.max) {
          newErrors[field.name] = `Must be between ${field.min} and ${field.max}`;
        }
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const loadExample = (exampleKey) => {
    setFormData(EXAMPLE_PATIENTS[exampleKey].data);
    setSelectedPatient(exampleKey);
    setErrors({});
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="section-title">
          <Icon icon={MedicalIcons.clinical} size="md" className="text-clinical-600" />
          Patient Clinical Data
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Enter clinical measurements for cardiovascular risk assessment
        </p>
      </div>

      {/* Example Patient Profiles */}
      <div className="card-section">
        <h4 className="section-subtitle">Quick Load Sample Profiles</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {Object.entries(EXAMPLE_PATIENTS).map(([key, patient]) => {
            const isSelected = selectedPatient === key;
            const riskLevel =
              key === 'healthy' ? 'normal' : key === 'moderate' ? 'warning' : 'critical';

            return (
              <button
                key={key}
                type="button"
                onClick={() => loadExample(key)}
                disabled={loading}
                className={clsx(
                  'p-3 border rounded text-left transition-all disabled:opacity-50 disabled:cursor-not-allowed',
                  isSelected
                    ? 'border-clinical-500 bg-clinical-50 shadow-sm ring-1 ring-clinical-200'
                    : 'border-gray-200 bg-white hover:border-clinical-300 hover:shadow-sm'
                )}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon icon={MedicalIcons.user} size="sm" className="text-gray-500" />
                    <div>
                      <div className="font-semibold text-sm text-gray-900">{patient.initials}</div>
                      <div className="text-xs text-gray-500">{patient.age}</div>
                    </div>
                  </div>
                  {isSelected && (
                    <Icon
                      icon={MedicalIcons.successSolid}
                      size="sm"
                      className="text-clinical-600"
                    />
                  )}
                </div>
                <div className={`badge badge-${riskLevel} mb-2`}>{patient.riskCategory}</div>
                <p className="text-xs text-gray-600 leading-relaxed">{patient.summary}</p>
                <div className="text-xs text-gray-500 mt-2 font-mono">{patient.mrn}</div>
              </button>
            );
          })}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="card-section">
          <h4 className="section-subtitle flex items-center gap-2">
            <Icon icon={MedicalIcons.document} size="sm" className="text-gray-500" />
            Clinical Parameters
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {FIELD_CONFIG.map((field) => {
              const hasError = errors[field.name];

              return (
                <div key={field.name} className="flex flex-col">
                  <label htmlFor={field.name} className="label">
                    {field.label}
                    {field.unit && (
                      <span className="text-gray-500 font-normal ml-1 text-xs">({field.unit})</span>
                    )}
                  </label>

                  {field.type === 'select' ? (
                    <select
                      id={field.name}
                      value={formData[field.name] ?? ''}
                      onChange={(e) => handleChange(field.name, e.target.value)}
                      className={clsx('input', hasError && 'input-error')}
                      disabled={loading}
                      aria-invalid={hasError ? 'true' : 'false'}
                      aria-describedby={hasError ? `${field.name}-error` : undefined}
                    >
                      <option value="">Select...</option>
                      {field.options.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      id={field.name}
                      type={field.type}
                      min={field.min}
                      max={field.max}
                      step={field.step}
                      value={formData[field.name] ?? ''}
                      onChange={(e) => handleChange(field.name, e.target.value)}
                      className={clsx('input', hasError && 'input-error')}
                      disabled={loading}
                      aria-invalid={hasError ? 'true' : 'false'}
                      aria-describedby={hasError ? `${field.name}-error` : undefined}
                    />
                  )}

                  {field.help && (
                    <div className="help-text flex items-start gap-1">
                      <Icon
                        icon={MedicalIcons.infoSolid}
                        size="xs"
                        className="text-info-500 flex-shrink-0 mt-0.5"
                      />
                      <span>{field.help}</span>
                    </div>
                  )}

                  {hasError && (
                    <div className="error-text" id={`${field.name}-error`} role="alert">
                      <Icon icon={MedicalIcons.error} size="xs" className="flex-shrink-0" />
                      <span>{errors[field.name]}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex justify-end pt-4 border-t border-gray-200">
          <button
            type="submit"
            className="btn btn-primary px-8 flex items-center gap-2"
            disabled={loading}
          >
            {loading ? (
              <>
                <svg
                  className="animate-spin h-4 w-4 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <span>Analyzing Patient Data...</span>
              </>
            ) : (
              <>
                <Icon icon={MedicalIcons.chart} size="sm" />
                <span>Calculate Risk Assessment</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
