"""
Configuration File
Project settings and constants
"""

from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent

# Data Paths
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
OUTPUTS_DIR = DATA_DIR / 'outputs'

# Model Paths
MODELS_DIR = PROJECT_ROOT / 'models'
MODEL_PATH = MODELS_DIR / 'random_forest_flood_model.pkl'

# Feature Configuration
FEATURE_COLUMNS = [
    'rainfall_7d_mm',
    'soil_moisture',
    'elevation_m',
    'slope_deg'
]

TARGET_COLUMN = 'flood_label'

# GEE Configuration
GEE_PROJECT = 'student-study-app-468414'  # Your GEE Cloud Project
GEE_BUFFER_METERS = 10000  # 10 km buffer around point
GEE_SAFE_DAYS_BACK = 30     # Use data from 30 days ago
GEE_WINDOW_DAYS = 7         # 7-day window for rainfall

# Datasets
CHIRPS_DATASET = 'UCSB-CHG/CHIRPS/DAILY'
ERA5_DATASET = 'ECMWF/ERA5_LAND/DAILY_AGGR'
SRTM_DATASET = 'USGS/SRTMGL1_003'

# Model Hyperparameters
RF_N_ESTIMATORS = 100
RF_MAX_DEPTH = 10
RF_MIN_SAMPLES_SPLIT = 5
RF_MIN_SAMPLES_LEAF = 2
RF_RANDOM_STATE = 42

# Train-Test Split
TEST_SIZE = 0.2
RANDOM_STATE = 42

# API Configuration
API_HOST = '0.0.0.0'
API_PORT = 5000
DEBUG_MODE = True

# Risk Level Thresholds
RISK_THRESHOLDS = {
    'HIGH': 0.7,
    'MEDIUM': 0.4,
    'LOW': 0.0
}

# Email Notification Configuration
EMAIL_NOTIFICATIONS_ENABLED = True  # Set to False to disable email notifications
EMAIL_ALERT_THRESHOLD = 0.5  # Send email if flood probability >= 50%

# SMTP Configuration (Gmail example)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = ''  # Your email address (e.g., 'your_email@gmail.com')
SMTP_PASSWORD = ''  # Your email password or app password
SMTP_FROM_EMAIL = ''  # Sender email (usually same as SMTP_USERNAME)
SMTP_FROM_NAME = 'Flood Prediction System'

# Default recipient email (can be overridden by user settings)
DEFAULT_ALERT_EMAIL = 'Sumithabangaru@gmail.com'  # Email to receive alerts (e.g., 'admin@example.com')

print(f"✓ Configuration loaded from {__file__}")
# Flask session secret
FLASK_SECRET_KEY = "CHANGE_THIS_TO_A_RANDOM_SECRET"
