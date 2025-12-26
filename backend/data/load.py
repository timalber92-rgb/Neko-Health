"""
Data Loading and Preprocessing Module for HealthGuard

This module handles the complete data pipeline for the UCI Heart Disease dataset:
- Downloading raw data from UCI repository
- Cleaning and handling missing values
- Feature preprocessing and normalization
- Train/validation/test splitting with stratification
"""

import logging
from pathlib import Path
from typing import Tuple
from urllib.request import urlretrieve

import pandas as pd
from sklearn.model_selection import train_test_split

# StandardScaler removed - Logistic Regression works with raw features

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
FEATURE_NAMES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "target",
]

# Determine the absolute path to the data directory
CURRENT_DIR = Path(__file__).parent
RAW_DATA_DIR = CURRENT_DIR / "raw"
PROCESSED_DATA_DIR = CURRENT_DIR / "processed"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

RAW_DATA_PATH = RAW_DATA_DIR / "heart_disease.csv"
TRAIN_DATA_PATH = PROCESSED_DATA_DIR / "train.csv"
VAL_DATA_PATH = PROCESSED_DATA_DIR / "val.csv"
TEST_DATA_PATH = PROCESSED_DATA_DIR / "test.csv"
SCALER_PATH = PROCESSED_DATA_DIR / "scaler.pkl"


def download_data() -> Path:
    """
    Download the UCI Heart Disease dataset from the repository.

    Downloads the Cleveland heart disease dataset and saves it as a CSV file
    with proper column names. If the file already exists, skips downloading.

    Returns:
        Path: Path to the downloaded CSV file

    Raises:
        Exception: If download fails or network issues occur
    """
    try:
        if RAW_DATA_PATH.exists():
            logger.info(f"Data already exists at {RAW_DATA_PATH}, skipping download")
            return RAW_DATA_PATH

        logger.info(f"Downloading data from {DATA_URL}")
        urlretrieve(DATA_URL, RAW_DATA_PATH.with_suffix(".data"))

        # Load the data and add column names
        df = pd.read_csv(RAW_DATA_PATH.with_suffix(".data"), header=None, names=FEATURE_NAMES, na_values="?")

        # Save as CSV
        df.to_csv(RAW_DATA_PATH, index=False)
        logger.info(f"Data downloaded and saved to {RAW_DATA_PATH}")
        logger.info(f"Dataset shape: {df.shape}")

        # Clean up the .data file
        RAW_DATA_PATH.with_suffix(".data").unlink()

        return RAW_DATA_PATH

    except Exception as e:
        logger.error(f"Failed to download data: {str(e)}")
        raise


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw heart disease dataset.

    Handles missing values, converts data types, and performs basic
    data quality checks. Missing values are imputed with column medians
    for numeric features.

    Args:
        df: Raw DataFrame with potential missing values and type issues

    Returns:
        pd.DataFrame: Cleaned DataFrame with no missing values

    Raises:
        ValueError: If DataFrame is empty or has unexpected structure
    """
    logger.info("Starting data cleaning process")

    if df.empty:
        raise ValueError("Input DataFrame is empty")

    if len(df.columns) != len(FEATURE_NAMES):
        raise ValueError(f"Expected {len(FEATURE_NAMES)} columns, got {len(df.columns)}")

    # Log initial data quality
    initial_missing = df.isnull().sum().sum()
    logger.info(f"Initial missing values: {initial_missing}")

    # Create a copy to avoid modifying the original
    df_clean = df.copy()

    # Handle missing values by replacing with column median
    # This preserves the distribution better than mean for skewed data
    for col in df_clean.columns:
        if df_clean[col].isnull().any():
            missing_count = df_clean[col].isnull().sum()
            median_value = df_clean[col].median()
            df_clean[col].fillna(median_value, inplace=True)
            logger.info(f"Imputed {missing_count} missing values in '{col}' " f"with median: {median_value:.2f}")

    # Convert target to binary classification
    # Original: 0 = no disease, 1-4 = disease presence (severity levels)
    # New: 0 = no disease, 1 = disease present
    df_clean["target"] = (df_clean["target"] > 0).astype(int)
    logger.info(f"Converted target to binary classification. " f"Class distribution:\n{df_clean['target'].value_counts()}")

    # Ensure all numeric columns are proper numeric types
    for col in df_clean.columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    # Final check for any remaining missing values
    final_missing = df_clean.isnull().sum().sum()
    if final_missing > 0:
        logger.warning(f"Still have {final_missing} missing values after cleaning")
    else:
        logger.info("No missing values remaining after cleaning")

    # Log basic statistics
    logger.info(f"Cleaned data shape: {df_clean.shape}")
    logger.info(f"Feature ranges:\n{df_clean.describe()}")

    return df_clean


def preprocess_data(
    df: pd.DataFrame, test_size: float = 0.15, val_size: float = 0.15, random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Preprocess the cleaned data: normalize features and create train/val/test splits.

    Features are NOT scaled (Random Forest doesn't require normalization).
    Data is split into train (70%), validation (15%), and test (15%) sets
    with stratification to maintain class balance.

    Args:
        df: Cleaned DataFrame ready for preprocessing
        test_size: Proportion of data for test set (default: 0.15)
        val_size: Proportion of data for validation set (default: 0.15)
        random_state: Random seed for reproducibility (default: 42)

    Returns:
        Tuple containing:
            - train_df: Training set DataFrame
            - val_df: Validation set DataFrame
            - test_df: Test set DataFrame

    Raises:
        ValueError: If split sizes are invalid or data is insufficient
    """
    logger.info("Starting data preprocessing")

    # Validate split sizes
    total_split = test_size + val_size
    if total_split >= 1.0:
        raise ValueError(f"test_size ({test_size}) + val_size ({val_size}) " f"must be less than 1.0")

    # Separate features and target
    X = df.drop("target", axis=1)
    y = df["target"]

    logger.info(f"Feature matrix shape: {X.shape}")
    logger.info(f"Target distribution: {y.value_counts().to_dict()}")

    # First split: separate test set
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)

    # Second split: separate validation from training
    # Adjust val_size to account for already-removed test set
    adjusted_val_size = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=adjusted_val_size, random_state=random_state, stratify=y_temp
    )

    logger.info(f"Train set size: {len(X_train)} ({len(X_train)/len(df)*100:.1f}%)")
    logger.info(f"Validation set size: {len(X_val)} ({len(X_val)/len(df)*100:.1f}%)")
    logger.info(f"Test set size: {len(X_test)} ({len(X_test)/len(df)*100:.1f}%)")

    # Verify stratification worked
    logger.info(f"Train set class balance: {y_train.value_counts(normalize=True).to_dict()}")
    logger.info(f"Val set class balance: {y_val.value_counts(normalize=True).to_dict()}")
    logger.info(f"Test set class balance: {y_test.value_counts(normalize=True).to_dict()}")

    # Random Forest doesn't require feature scaling - use raw values
    # This simplifies intervention simulation and makes the model more interpretable
    logger.info("Using raw feature values (no scaling needed for Random Forest)")

    # Create DataFrames with original column names and raw values
    train_df = pd.DataFrame(X_train, columns=X.columns)
    train_df["target"] = y_train.values

    val_df = pd.DataFrame(X_val, columns=X.columns)
    val_df["target"] = y_val.values

    test_df = pd.DataFrame(X_test, columns=X.columns)
    test_df["target"] = y_test.values

    logger.info("Preprocessing complete")

    return train_df, val_df, test_df


def save_processed_data(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
    """
    Save processed datasets to disk.

    Saves train/val/test CSVs for later use during model training.

    Args:
        train_df: Training set DataFrame
        val_df: Validation set DataFrame
        test_df: Test set DataFrame

    Raises:
        IOError: If files cannot be written to disk
    """
    try:
        train_df.to_csv(TRAIN_DATA_PATH, index=False)
        logger.info(f"Saved training data to {TRAIN_DATA_PATH}")

        val_df.to_csv(VAL_DATA_PATH, index=False)
        logger.info(f"Saved validation data to {VAL_DATA_PATH}")

        test_df.to_csv(TEST_DATA_PATH, index=False)
        logger.info(f"Saved test data to {TEST_DATA_PATH}")

        logger.info("No scaler needed for Random Forest (using raw features)")

    except Exception as e:
        logger.error(f"Failed to save processed data: {str(e)}")
        raise


def load_processed_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load pre-processed data for model training and evaluation.

    Loads the train, validation, and test sets. If processed data doesn't
    exist, runs the full pipeline to create it.

    Returns:
        Tuple containing:
            - train_df: Training set DataFrame
            - val_df: Validation set DataFrame
            - test_df: Test set DataFrame

    Raises:
        FileNotFoundError: If processed files don't exist and raw data cannot be found
        IOError: If files cannot be read
    """
    # Check if all processed files exist
    required_files = [TRAIN_DATA_PATH, VAL_DATA_PATH, TEST_DATA_PATH]
    all_exist = all(f.exists() for f in required_files)

    if not all_exist:
        logger.warning("Processed data not found. Running full pipeline...")
        run_pipeline()

    try:
        train_df = pd.read_csv(TRAIN_DATA_PATH)
        logger.info(f"Loaded training data: {train_df.shape}")

        val_df = pd.read_csv(VAL_DATA_PATH)
        logger.info(f"Loaded validation data: {val_df.shape}")

        test_df = pd.read_csv(TEST_DATA_PATH)
        logger.info(f"Loaded test data: {test_df.shape}")

        logger.info("Using raw features (no scaler needed for Random Forest)")

        return train_df, val_df, test_df

    except Exception as e:
        logger.error(f"Failed to load processed data: {str(e)}")
        raise


def run_pipeline() -> None:
    """
    Execute the complete data pipeline from download to processed output.

    This is the main orchestrator function that:
    1. Downloads raw data from UCI repository
    2. Cleans and handles missing values
    3. Preprocesses features and creates splits
    4. Saves processed data and scaler to disk

    Can be run standalone or called by load_processed_data() if needed.

    Raises:
        Exception: If any step in the pipeline fails
    """
    logger.info("=" * 60)
    logger.info("STARTING HEALTHGUARD DATA PIPELINE")
    logger.info("=" * 60)

    try:
        # Step 1: Download data
        logger.info("\n[STEP 1/4] Downloading raw data...")
        raw_path = download_data()

        # Step 2: Load and clean data
        logger.info("\n[STEP 2/4] Loading and cleaning data...")
        df_raw = pd.read_csv(raw_path)
        df_clean = clean_data(df_raw)

        # Step 3: Preprocess data
        logger.info("\n[STEP 3/4] Preprocessing and splitting data...")
        train_df, val_df, test_df = preprocess_data(df_clean)

        # Step 4: Save processed data
        logger.info("\n[STEP 4/4] Saving processed data...")
        save_processed_data(train_df, val_df, test_df)

        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"\nProcessed files saved to: {PROCESSED_DATA_DIR}")
        logger.info(f"- Training set: {TRAIN_DATA_PATH.name}")
        logger.info(f"- Validation set: {VAL_DATA_PATH.name}")
        logger.info(f"- Test set: {TEST_DATA_PATH.name}")
        logger.info("- No scaler needed (Random Forest uses raw features)")

    except Exception as e:
        logger.error(f"\nPIPELINE FAILED: {str(e)}")
        raise


if __name__ == "__main__":
    # Run the complete pipeline when executed as a script
    run_pipeline()

    # Demonstrate loading the processed data
    logger.info("\n" + "=" * 60)
    logger.info("TESTING DATA LOADING")
    logger.info("=" * 60)
    train_df, val_df, test_df = load_processed_data()

    logger.info("\nData successfully loaded and ready for model training!")
    logger.info(f"Training samples: {len(train_df)}")
    logger.info(f"Validation samples: {len(val_df)}")
    logger.info(f"Test samples: {len(test_df)}")
    logger.info(f"Features: {list(train_df.columns[:-1])}")
