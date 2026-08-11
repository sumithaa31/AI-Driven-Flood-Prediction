# 🌊 AI-Driven Flood Prediction System

> **Academic Project**: Satellite-based flood risk prediction using Google Earth Engine, Machine Learning, Flask, and ArcGIS

---

## 📋 Project Overview

This system predicts flood probability for any geographic location using:
- **Google Earth Engine (GEE)** for satellite data extraction
- **Machine Learning (Random Forest)** for flood risk prediction  
- **Flask API** for serving predictions
- **Interactive Web UI** with Leaflet.js mapping
- **ArcGIS Integration** for professional spatial visualization

---

## 🏗️ Project Structure

```
flood-prediction/
├── data/
│   ├── raw/              # Training datasets (CSV from manual creation)
│   ├── processed/        # Cleaned datasets
│   └── outputs/          # Prediction results & ArcGIS exports
│       └── arcgis/       # GeoJSON, Shapefiles, CSV for ArcGIS
│
├── models/               # Trained ML model (.pkl)
│   └── random_forest_flood_model.pkl
│
├── src/
│   ├── feature_extraction_gee.py   # GEE satellite data fetching
│   ├── model_training.py           # ML training utilities
│   ├── train_model.py              # Model training script
│   ├── arcgis_export.py            # Export to ArcGIS formats
│   ├── generate_arcgis_predictions.py  # Batch predictions
│   └── utils.py                    # Helper functions
│
├── api/
│   └── flask_app.py      # REST API server
│
├── static/               # Web UI assets
│   ├── css/style.css     # UI styling
│   └── js/app.js         # Frontend logic
│
├── templates/
│   └── index.html        # Interactive web interface
│
├── docs/
│   ├── ARCGIS_INTEGRATION.md   # ArcGIS import guide
│   ├── PROJECT_SUMMARY.md      # Complete project overview
│   └── PRESENTATION_GUIDE.md   # Demo & presentation help
│
├── tests/
│   └── test_api.py       # API testing suite
│
├── configs/
│   └── config.py         # Project configuration
│
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## 🛰️ Features Extracted

| Feature | Source Dataset | Description |
|---------|---------------|-------------|
| **Rainfall** | CHIRPS Daily | 7-day cumulative precipitation (mm) |
| **Soil Moisture** | ERA5-Land | Surface soil moisture (0-7 cm layer) |
| **Elevation** | SRTM DEM | Average terrain elevation (m) |
| **Slope** | SRTM (derived) | Average terrain slope (degrees) |

---

## 🚀 Installation & Setup

### Quick Setup (Windows - Automated):
```bash
# 1. Double-click: setup.bat
# 2. Follow the on-screen instructions
# 3. Authenticate with your Google account

# Then run the server:
# Double-click: start_server.bat
```

### Manual Setup:

### 1. Clone/Copy Project
```bash
# Copy all files EXCEPT:
# - venv/ folder
# - __pycache__/ folders
# - .zencoder/, .zenflow/ folders
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Authenticate Google Earth Engine
```bash
earthengine authenticate
# Follow browser prompts to log in with YOUR Google account
```

**📖 Detailed deployment instructions:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 📊 Usage

### Option 1: Web Interface (Recommended)

1. **Start the Flask server:**
```bash
python api/flask_app.py
```

2. **Open browser:**
```
http://localhost:5000
```

3. **Get predictions:**
- Click anywhere on the map
- Or use quick location buttons (Mumbai, Delhi, etc.)
- View results with risk gauge and detailed features

### Option 2: Command Line API

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"latitude": 17.385, "longitude": 78.486}'
```

**Response:**
```json
{
  "flood_probability": 0.026,
  "risk_level": "LOW",
  "confidence": "high",
  "features": {
    "rainfall_7d_mm": 0.92,
    "soil_moisture": 0.2049,
    "elevation_m": 523.64,
    "slope_deg": 3.07
  }
}
```

### Option 3: ArcGIS Integration

Generate predictions for mapping in ArcGIS Online/Pro/Desktop:

```bash
# Generate predictions for major Indian cities (10 locations)
python src/generate_arcgis_predictions.py

# Generate predictions for specific state
python src/generate_arcgis_predictions.py --region telangana
python src/generate_arcgis_predictions.py --region maharashtra

# Generate predictions for all available regions
python src/generate_arcgis_predictions.py --all
```

**Output formats:**
- `flood_risk_*.geojson` - For ArcGIS Online/Pro
- `flood_risk_*.shp` - For ArcGIS Desktop/Pro
- `flood_risk_*.csv` - For quick import with XY coordinates
- `flood_risk_*_layer.json` - Symbology reference

**Import to ArcGIS:**
1. Upload generated files to ArcGIS Online or open in ArcGIS Pro
2. Symbolize by `risk_level` field (HIGH/MEDIUM/LOW)
3. Create professional flood risk maps

📖 **Detailed guide:** See [docs/ARCGIS_INTEGRATION.md](docs/ARCGIS_INTEGRATION.md)

---

## 🗺️ ArcGIS Visualization

The system exports predictions in multiple GIS formats:

| Format | Extension | Best For |
|--------|-----------|----------|
| GeoJSON | `.geojson` | ArcGIS Online, ArcGIS Pro |
| Shapefile | `.shp` | ArcGIS Desktop/Pro (native) |
| CSV | `.csv` | Quick import with coordinates |
| Layer JSON | `_layer.json` | Symbology definition |

**Features included in exports:**
- Location name
- Latitude/Longitude (WGS84)
- Flood probability (0-1)
- Risk level (HIGH/MEDIUM/LOW)
- All input features (rainfall, soil moisture, elevation, slope)

---

## 📈 Model Performance & Training Data

**Algorithm:** Random Forest Classifier
- **Test Accuracy:** 95.6%
- **ROC-AUC Score:** 0.998
- **F1-Score:** 0.96

**Feature Importance:**
1. Slope: 45.78%
2. Elevation: 45.22%
3. Soil Moisture: 6.19%
4. Rainfall: 2.81%

**Training Data:** 1250 samples (1000 train, 250 test)
- 50 locations across India
- 25 time windows (2020-2024 monsoon seasons)
- Balanced classes (625 flood, 625 non-flood)

---

## 🎯 Implementation Phases

- [x] **Phase 1**: Project setup & structure
- [x] **Phase 2**: Data exploration & preprocessing (1250 samples analyzed)
- [x] **Phase 3**: ML model training (Random Forest, 95.6% accuracy)
- [x] **Phase 4**: GEE Python integration (authenticated & tested)
- [x] **Phase 5**: Flask API development (REST endpoints)
- [x] **Phase 6**: Interactive web UI (Leaflet.js map)
- [x] **Phase 7**: ArcGIS integration (GeoJSON/Shapefile export)

**🎉 PROJECT STATUS: COMPLETE** (All 7 phases finished!)

---

## 🔧 Technologies

| Component | Technology |
|-----------|-----------|
| Satellite Data | Google Earth Engine |
| ML Framework | scikit-learn, XGBoost |
| Backend | Flask + Python 3.x |
| Visualization | ArcGIS, Matplotlib, Seaborn |
| Data Processing | Pandas, NumPy |

---

## 📝 Key Constraints

✅ **DO:**
- Use safe historical date ranges (30+ days back)
- Extract features identically for training & prediction
- Handle missing GEE data gracefully

❌ **DON'T:**
- Use real-time "today" satellite data (latency issues)
- Send raw images to ML model
- Mix feature extraction logic between training & prediction

---

## 👨‍💻 Author

**Final Year Project** - AI-Driven Flood Prediction System  
Academic/Non-commercial use only

---

## 📄 License

Educational use only. Not for commercial deployment.

---

## 🆘 Support

For issues:
1. Check GEE authentication: `earthengine authenticate`
2. Verify dataset paths in `configs/config.py`
3. Ensure all dependencies installed: `pip install -r requirements.txt`
4. For ArcGIS import help: See [docs/ARCGIS_INTEGRATION.md](docs/ARCGIS_INTEGRATION.md)

---

## 🎓 Project Deliverables

✅ **Complete System:**
1. Trained Random Forest model (95.6% accuracy)
2. Google Earth Engine integration (CHIRPS, ERA5, SRTM)
3. Flask REST API with JSON responses
4. Interactive web interface with Leaflet.js mapping
5. ArcGIS export functionality (GeoJSON, Shapefile, CSV)
6. Batch prediction generator for spatial mapping
7. Comprehensive documentation

✅ **Key Features:**
- Click-to-predict on interactive map
- Real-time satellite data extraction
- Risk classification (LOW/MEDIUM/HIGH)
- Professional GIS visualization support
- Academic project report ready

---

**🏆 Final Status**: All phases complete! System ready for academic presentation and demonstration.

**📅 Completion Date**: January 2026  
**🎯 Purpose**: Final Year Academic Project
