"""
Flask API for Flood Prediction
Provides REST endpoint for flood probability prediction
"""

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))
sys.path.append(str(Path(__file__).parent.parent / 'configs'))

from feature_extraction_gee import initialize_gee, extract_features_for_location, get_safe_date_range
from model_training import load_model
from utils import validate_coordinates, format_prediction_response
from email_notifications import send_flood_alert_email
from database import init_database, create_user, get_user_by_username, get_user_by_email, get_user_by_id, update_last_login, save_prediction
from auth import hash_password, verify_password, validate_registration, validate_login, is_email
import config

# Try to import weather API module (it might not exist in older versions)
try:
    from feature_extraction_weather_api import extract_features_from_weather_api
    WEATHER_API_AVAILABLE = True
except ImportError:
    WEATHER_API_AVAILABLE = False
    print("⚠️ Weather API module not found. Using GEE only.")

app = Flask(__name__, 
            template_folder=str(Path(__file__).parent.parent / 'templates'),
            static_folder=str(Path(__file__).parent.parent / 'static'))

# Secret key for session management (CHANGE THIS IN PRODUCTION!)
app.secret_key = config.FLASK_SECRET_KEY
# Session configuration for better cookie handling
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

# CORS configuration with explicit origin
CORS(app, 
     supports_credentials=True,
     origins=['http://localhost:5000', 'http://127.0.0.1:5000'],
     allow_headers=['Content-Type'],
     methods=['GET', 'POST', 'OPTIONS'])

# Global variables
model = None
gee_initialized = False


def login_required(f):
    """
    Decorator to protect routes that require authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required', 'redirect': '/login'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def load_trained_model():
    """Load the trained ML model"""
    global model
    model_path = Path(__file__).parent.parent / 'models' / 'random_forest_flood_model.pkl'
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    model = load_model(str(model_path))
    print("✓ Model loaded successfully")


def initialize_app():
    """Initialize GEE and load model"""
    global gee_initialized
    
    # Initialize database
    init_database()
    print("✓ Database initialized")
    
    # Initialize GEE with project
    gee_project = 'student-study-app-468414'
    gee_initialized = initialize_gee(project=gee_project)
    
    # Load ML model
    load_trained_model()


@app.route('/')
@login_required
def home():
    """Serve the web UI (protected)"""
    user = get_user_by_id(session['user_id'])
    return render_template('index.html', user=user)


@app.route('/notifications', methods=['GET'])
@login_required
def notifications():
    """Serve the notifications page (protected)"""
    user = get_user_by_id(session['user_id'])
    return render_template('notifications.html', user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'GET':
        # Redirect to home if already logged in
        if 'user_id' in session:
            return redirect(url_for('home'))
        return render_template('register.html')
    
    # POST request - handle registration
    try:
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        retype_password = data.get('retype_password', '')
        
        # Validate input
        valid, errors = validate_registration(username, email, password, retype_password)
        
        if not valid:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        success, message, user_id = create_user(username, email, password_hash)
        
        if not success:
            return jsonify({'success': False, 'errors': {'general': message}}), 400
        
        # Auto-login after registration
        session['user_id'] = user_id
        session['username'] = username
        session['email'] = email
        
        return jsonify({
            'success': True,
            'message': 'Registration successful!',
            'redirect': url_for('home')
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'errors': {'general': str(e)}}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'GET':
        # Redirect to home if already logged in
        if 'user_id' in session:
            return redirect(url_for('home'))
        return render_template('login.html')
    
    # POST request - handle login
    try:
        data = request.get_json() if request.is_json else request.form
        
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')
        
        # Validate input
        valid, errors = validate_login(identifier, password)
        
        if not valid:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Get user by username or email
        if is_email(identifier):
            user = get_user_by_email(identifier.lower())
        else:
            user = get_user_by_username(identifier)
        
        # Check if user exists
        if not user:
            return jsonify({
                'success': False,
                'errors': {'general': 'Invalid username/email or password'}
            }), 401
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({
                'success': False,
                'errors': {'general': 'Invalid username/email or password'}
            }), 401
        
        # Login successful - create session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']
        
        # Update last login
        update_last_login(user['id'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'redirect': url_for('home')
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'errors': {'general': str(e)}}), 500


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/api/status', methods=['GET'])
def api_status():
    """API health check endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'Flood Prediction API',
        'gee_status': 'connected' if gee_initialized else 'disconnected'
    })


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    """
    Predict flood probability for a given location (requires authentication)
    
    Request Body:
    {
        "latitude": 17.385,
        "longitude": 78.486
    }
    
    Response:
    {
        "flood_probability": 0.82,
        "risk_level": "HIGH",
        "confidence": "high",
        "features": {...}
    }
    """
    try:
        # Get logged-in user
        user_id = session['user_id']
        user_email = session['email']
        
        # Parse request
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        # Validate coordinates
        if not validate_coordinates(lat, lon):
            return jsonify({'error': 'Invalid coordinates'}), 400
        
        # Check GEE status
        if not gee_initialized:
            return jsonify({'error': 'GEE not initialized'}), 500
        
        # Get safe date range (avoid real-time data issues)
        start_date, end_date = get_safe_date_range(days_back=30, window_days=7)
        
        # Choose data source based on configuration
        if WEATHER_API_AVAILABLE and hasattr(config, 'USE_WEATHER_API') and config.USE_WEATHER_API and config.WEATHER_API_KEY:
            print(f"\n🌤️ Using Weather API for real-time data...")
            # Extract features using Weather API (real-time)
            features = extract_features_from_weather_api(
                lat, lon, 
                config.WEATHER_API_KEY,
                days_back=getattr(config, 'WEATHER_API_DAYS_BACK', 7)
            )
        else:
            print(f"\n🛰️ Using GEE for historical data...")
            # Extract features from GEE (historical)
            features = extract_features_for_location(lat, lon, start_date, end_date)
        
        # Check if features extraction failed
        if features is None:
            return jsonify({'error': 'Failed to extract features (data unavailable for this location)'}), 500
        
        # Check for None values in features
        if None in features.values():
            return jsonify({'error': 'Failed to extract features (data unavailable)'}), 500
        
        # Prepare features in correct order
        feature_array = [[
            features['rainfall_7d_mm'],
            features['soil_moisture'],
            features['elevation_m'],
            features['slope_deg']
        ]]
        
        # Predict
        probability = model.predict_proba(feature_array)[0][1]
        
        # Format response
        response = format_prediction_response(probability, features)
        
        # Add data source info
        data_source = "Weather API (Real-time)" if (WEATHER_API_AVAILABLE and hasattr(config, 'USE_WEATHER_API') and config.USE_WEATHER_API and config.WEATHER_API_KEY) else "GEE (Historical)"
        response['data_source'] = data_source
        
        # Add date range if using GEE
        if not (WEATHER_API_AVAILABLE and hasattr(config, 'USE_WEATHER_API') and config.USE_WEATHER_API and config.WEATHER_API_KEY):
            response['date_range'] = {'start': start_date, 'end': end_date}
        
        # Save prediction to user's history
        email_sent_flag = False
        
        # Send email notification if probability exceeds threshold
        if hasattr(config, 'EMAIL_NOTIFICATIONS_ENABLED') and config.EMAIL_NOTIFICATIONS_ENABLED:
            email_threshold = getattr(config, 'EMAIL_ALERT_THRESHOLD', 0.5)
            
            if probability >= email_threshold:
                print(f"\n📧 Flood probability ({probability:.1%}) exceeds threshold ({email_threshold:.1%})")
                
                # Use logged-in user's email
                recipient_email = user_email
                
                if recipient_email:
                    # Prepare SMTP config
                    smtp_config = {
                        'enabled': config.EMAIL_NOTIFICATIONS_ENABLED,
                        'server': getattr(config, 'SMTP_SERVER', ''),
                        'port': getattr(config, 'SMTP_PORT', 587),
                        'username': getattr(config, 'SMTP_USERNAME', ''),
                        'password': getattr(config, 'SMTP_PASSWORD', ''),
                        'from_email': getattr(config, 'SMTP_FROM_EMAIL', ''),
                        'from_name': getattr(config, 'SMTP_FROM_NAME', 'Flood Alert System')
                    }
                    
                    # Send email in background (don't block response)
                    try:
                        email_sent_flag = send_flood_alert_email(
                            recipient_email=recipient_email,
                            location_lat=lat,
                            location_lon=lon,
                            flood_probability=probability,
                            risk_level=response['risk_level'],
                            features=features,
                            smtp_config=smtp_config
                        )
                        response['email_sent'] = email_sent_flag
                    except Exception as email_error:
                        print(f"⚠️ Email notification failed: {str(email_error)}")
                        response['email_sent'] = False
                else:
                    print("⚠️ No recipient email configured. Skipping email notification.")
                    response['email_sent'] = False
        
        # Save prediction to database
        save_prediction(
            user_id=user_id,
            latitude=lat,
            longitude=lon,
            flood_probability=probability,
            risk_level=response['risk_level'],
            email_sent=email_sent_flag
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"\n❌ ERROR in /predict endpoint:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Traceback:")
        traceback.print_exc()
        
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n🚀 Starting Flood Prediction API...")
    initialize_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
