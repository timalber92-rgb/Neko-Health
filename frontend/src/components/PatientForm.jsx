/**
 * PatientForm Component
 *
 * Interactive form for entering patient clinical data (13 features).
 * Includes validation, tooltips, and example data presets.
 */

import { useState } from 'react';

// Example patient data for quick testing
const EXAMPLE_PATIENTS = {
  healthy: {
    name: 'Healthy Patient',
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
    name: 'Moderate Risk Patient',
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
  high: {
    name: 'High Risk Patient',
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
    help: 'Patient age in years',
  },
  {
    name: 'sex',
    label: 'Sex',
    type: 'select',
    options: [
      { value: 0, label: 'Female' },
      { value: 1, label: 'Male' },
    ],
    help: 'Biological sex',
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
    help: 'Type of chest pain experienced',
  },
  {
    name: 'trestbps',
    label: 'Resting Blood Pressure',
    type: 'number',
    min: 50,
    max: 250,
    step: 1,
    unit: 'mm Hg',
    help: 'Resting blood pressure on admission to hospital',
  },
  {
    name: 'chol',
    label: 'Serum Cholesterol',
    type: 'number',
    min: 100,
    max: 600,
    step: 1,
    unit: 'mg/dl',
    help: 'Serum cholesterol level',
  },
  {
    name: 'fbs',
    label: 'Fasting Blood Sugar',
    type: 'select',
    options: [
      { value: 0, label: '≤ 120 mg/dl (Normal)' },
      { value: 1, label: '> 120 mg/dl (Elevated)' },
    ],
    help: 'Fasting blood sugar level',
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
    help: 'Resting electrocardiographic results',
  },
  {
    name: 'thalach',
    label: 'Maximum Heart Rate',
    type: 'number',
    min: 50,
    max: 250,
    step: 1,
    unit: 'bpm',
    help: 'Maximum heart rate achieved during exercise test',
  },
  {
    name: 'exang',
    label: 'Exercise Induced Angina',
    type: 'select',
    options: [
      { value: 0, label: 'No' },
      { value: 1, label: 'Yes' },
    ],
    help: 'Exercise induced chest pain',
  },
  {
    name: 'oldpeak',
    label: 'ST Depression',
    type: 'number',
    min: 0,
    max: 10,
    step: 0.1,
    unit: 'mm',
    help: 'ST depression induced by exercise relative to rest',
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
    help: 'Slope of peak exercise ST segment',
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
    help: 'Number of major vessels colored by fluoroscopy',
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
    help: 'Thalassemia blood disorder status',
  },
];

export default function PatientForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState(EXAMPLE_PATIENTS.moderate.data);
  const [errors, setErrors] = useState({});

  const handleChange = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: parseFloat(value) }));
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
    setErrors({});
  };

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Patient Information</h2>
        <p className="text-gray-600">Enter clinical measurements for cardiovascular risk assessment</p>
      </div>

      {/* Example Data Buttons */}
      <div className="mb-6 flex flex-wrap gap-2">
        <span className="text-sm font-medium text-gray-700 mr-2">Quick Load:</span>
        {Object.entries(EXAMPLE_PATIENTS).map(([key, { name }]) => (
          <button
            key={key}
            type="button"
            onClick={() => loadExample(key)}
            className="btn btn-secondary text-sm"
            disabled={loading}
          >
            {name}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {FIELD_CONFIG.map((field) => (
            <div key={field.name} className="flex flex-col">
              <label htmlFor={field.name} className="label">
                {field.label}
                {field.unit && <span className="text-gray-500 ml-1">({field.unit})</span>}
              </label>

              {field.type === 'select' ? (
                <select
                  id={field.name}
                  value={formData[field.name] ?? ''}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  className="input"
                  disabled={loading}
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
                  className="input"
                  disabled={loading}
                />
              )}

              {field.help && (
                <p className="text-xs text-gray-500 mt-1">{field.help}</p>
              )}

              {errors[field.name] && (
                <p className="text-xs text-red-600 mt-1">{errors[field.name]}</p>
              )}
            </div>
          ))}
        </div>

        <div className="flex justify-end pt-4 border-t">
          <button
            type="submit"
            className="btn btn-primary px-8"
            disabled={loading}
          >
            {loading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing...
              </span>
            ) : (
              'Analyze Risk'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
