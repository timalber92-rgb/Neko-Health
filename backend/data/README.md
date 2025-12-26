# Data Module

Data loading and preprocessing for the HealthGuard application.

## Structure

- `load.py` - Data loading utilities for the Cleveland Heart Disease dataset

## Dataset

The Cleveland Heart Disease dataset contains 303 samples with 14 features:

**Features:**
- age: Age in years
- sex: Sex (1 = male, 0 = female)
- cp: Chest pain type (0-3)
- trestbps: Resting blood pressure (mm Hg)
- chol: Serum cholesterol (mg/dl)
- fbs: Fasting blood sugar > 120 mg/dl (1 = true, 0 = false)
- restecg: Resting ECG results (0-2)
- thalach: Maximum heart rate achieved
- exang: Exercise induced angina (1 = yes, 0 = no)
- oldpeak: ST depression induced by exercise
- slope: Slope of peak exercise ST segment (0-2)
- ca: Number of major vessels colored by fluoroscopy (0-3)
- thal: Thalassemia (1-3)
- target: Disease presence (1 = disease, 0 = no disease)

## Data Files

Raw data files should be placed in `data/raw/`:
- `heart.csv` - Original Cleveland Heart Disease dataset

Processed data (if needed) goes in `data/processed/`.

## Usage

```python
from data.load import load_heart_disease_data

X, y = load_heart_disease_data()
```
