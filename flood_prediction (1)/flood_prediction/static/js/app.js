// Initialize Map
let map;
let marker;
let currentCircle;

// Initialize map on page load
document.addEventListener('DOMContentLoaded', function () {
    initMap();

    // Add event listener to predict button
    document.getElementById('predictBtn').addEventListener('click', predictFlood);

    // Allow Enter key in input fields
    document.getElementById('latitude').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') predictFlood();
    });

    document.getElementById('longitude').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') predictFlood();
    });
});

function initMap() {
    // Create map centered on India
    map = L.map('map').setView([20.5937, 78.9629], 5);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

    // Add click event to map
    map.on('click', function (e) {
        document.getElementById('latitude').value = e.latlng.lat.toFixed(4);
        document.getElementById('longitude').value = e.latlng.lng.toFixed(4);
        updateMarker(e.latlng.lat, e.latlng.lng);
    });

    // Set initial marker
    const initialLat = parseFloat(document.getElementById('latitude').value);
    const initialLon = parseFloat(document.getElementById('longitude').value);
    updateMarker(initialLat, initialLon);
}

function updateMarker(lat, lon, riskLevel = null) {
    // Remove existing marker and circle
    if (marker) {
        map.removeLayer(marker);
    }
    if (currentCircle) {
        map.removeLayer(currentCircle);
    }

    // Determine marker color based on risk level
    let markerColor = '#667eea'; // Default blue
    let iconHtml = '📍';

    if (riskLevel === 'HIGH') {
        markerColor = '#ef4444';
        iconHtml = '🔴';
    } else if (riskLevel === 'MEDIUM') {
        markerColor = '#fbbf24';
        iconHtml = '🟡';
    } else if (riskLevel === 'LOW') {
        markerColor = '#4ade80';
        iconHtml = '🟢';
    }

    // Create custom icon
    const customIcon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="font-size: 30px;">${iconHtml}</div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 30]
    });

    // Add new marker
    marker = L.marker([lat, lon], { icon: customIcon }).addTo(map);

    // Add circle to show analysis area (10km radius)
    currentCircle = L.circle([lat, lon], {
        radius: 10000, // 10 km
        color: markerColor,
        fillColor: markerColor,
        fillOpacity: 0.1,
        weight: 2
    }).addTo(map);

    // Center map on marker
    map.setView([lat, lon], 10);
}

function selectLocation(lat, lon, name) {
    document.getElementById('latitude').value = lat;
    document.getElementById('longitude').value = lon;
    updateMarker(lat, lon);

    // Add popup with location name
    if (marker) {
        marker.bindPopup(`<b>${name}</b><br>Click "Predict" to analyze`).openPopup();
    }
}

async function predictFlood() {
    const lat = parseFloat(document.getElementById('latitude').value);
    const lon = parseFloat(document.getElementById('longitude').value);

    // Validate inputs
    if (isNaN(lat) || isNaN(lon)) {
        alert('Please enter valid coordinates');
        return;
    }

    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
        alert('Invalid coordinates. Latitude must be between -90 and 90, Longitude between -180 and 180');
        return;
    }

    // Show loading, hide results
    document.getElementById('loadingCard').style.display = 'block';
    document.getElementById('resultsCard').style.display = 'none';

    try {
        // Make API request
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // Include session cookies
            body: JSON.stringify({
                latitude: lat,
                longitude: lon
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        // Hide loading
        document.getElementById('loadingCard').style.display = 'none';

        // Display results
        displayResults(data, lat, lon);

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loadingCard').style.display = 'none';
        alert('Failed to get prediction. Make sure the API server is running.');
    }
}

function displayResults(data, lat, lon) {
    // Show results card
    document.getElementById('resultsCard').style.display = 'block';

    // Update risk percentage and gauge
    const percentage = (data.flood_probability * 100).toFixed(1);
    document.getElementById('riskPercentage').textContent = percentage + '%';
    document.getElementById('gaugeFill').style.width = percentage + '%';

    // Update risk level badge
    const riskBadge = document.getElementById('riskLevel');
    riskBadge.textContent = data.risk_level;
    riskBadge.parentElement.className = 'risk-badge';

    if (data.risk_level === 'HIGH') {
        riskBadge.className = 'risk-high';
    } else if (data.risk_level === 'MEDIUM') {
        riskBadge.className = 'risk-medium';
    } else {
        riskBadge.className = 'risk-low';
    }

    // Update features
    if (data.features) {
        document.getElementById('rainfall').textContent = data.features.rainfall_7d_mm.toFixed(2) + ' mm';
        document.getElementById('soilMoisture').textContent = data.features.soil_moisture.toFixed(4) + ' m³/m³';
        document.getElementById('elevation').textContent = data.features.elevation_m.toFixed(2) + ' m';
        document.getElementById('slope').textContent = data.features.slope_deg.toFixed(2) + '°';
    }

    // Update date range
    if (data.date_range) {
        document.getElementById('dateInfo').textContent =
            `${data.date_range.start} to ${data.date_range.end}`;
    }

    // Update marker on map
    updateMarker(lat, lon, data.risk_level);

    // Add popup to marker
    if (marker) {
        const popupContent = `
            <div class="popup-content">
                <h3>Flood Risk Analysis</h3>
                <div class="popup-risk ${data.risk_level === 'HIGH' ? 'risk-high' : data.risk_level === 'MEDIUM' ? 'risk-medium' : 'risk-low'}">
                    ${data.risk_level} RISK
                </div>
                <p style="margin-top: 10px;">Probability: ${percentage}%</p>
            </div>
        `;
        marker.bindPopup(popupContent).openPopup();
    }

    // Scroll to results
    document.getElementById('resultsCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Check if we need to create a notification (probability >= 50%)
    if (data.flood_probability >= 0.5) {
        saveNotification(data, lat, lon);
        showAlertMessage(data.flood_probability, data.risk_level);
    }
}

function saveNotification(data, lat, lon) {
    // Save notification to localStorage
    const notification = {
        timestamp: new Date().toISOString(),
        location: { lat, lon },
        flood_probability: data.flood_probability,
        risk_level: data.risk_level,
        features: data.features,
        data_source: data.data_source || 'GEE (Historical)',
        email_sent: data.email_sent || false
    };

    // Get existing notifications
    const notifications = JSON.parse(localStorage.getItem('floodNotifications') || '[]');

    // Add new notification at the beginning
    notifications.unshift(notification);

    // Keep only last 50 notifications
    if (notifications.length > 50) {
        notifications.splice(50);
    }

    // Save back to localStorage
    localStorage.setItem('floodNotifications', JSON.stringify(notifications));

    // Update notification badge
    updateNotificationBadge();

    console.log('📌 Notification saved:', notification);
}

function showAlertMessage(probability, riskLevel) {
    const percentage = (probability * 100).toFixed(1);
    let emoji = '🔴';
    let color = '#ef4444';

    if (riskLevel === 'MEDIUM') {
        emoji = '🟡';
        color = '#fbbf24';
    }

    // Create alert message element
    const alertDiv = document.createElement('div');
    alertDiv.className = 'flood-alert-popup';
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-left: 5px solid ${color};
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
    `;

    alertDiv.innerHTML = `
        <div style="display: flex; align-items: start;">
            <div style="font-size: 32px; margin-right: 15px;">${emoji}</div>
            <div style="flex: 1;">
                <h3 style="margin: 0 0 10px 0; color: #1e293b;">
                    🚨 FLOOD ALERT
                </h3>
                <p style="margin: 0 0 10px 0; color: #475569;">
                    <strong>${riskLevel} Risk Detected!</strong><br>
                    Flood probability: <strong style="color: ${color};">${percentage}%</strong>
                </p>
                <p style="margin: 0 0 15px 0; color: #64748b; font-size: 14px;">
                    This alert has been saved to your notifications.
                </p>
                <div style="display: flex; gap: 10px;">
                    <a href="/notifications" style="
                        display: inline-block;
                        padding: 8px 16px;
                        background: ${color};
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                        font-size: 14px;
                        font-weight: 600;
                    ">View Notifications</a>
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" style="
                        padding: 8px 16px;
                        background: #e2e8f0;
                        color: #475569;
                        border: none;
                        border-radius: 6px;
                        font-size: 14px;
                        font-weight: 600;
                        cursor: pointer;
                    ">Dismiss</button>
                </div>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #94a3b8;
                padding: 0;
                margin-left: 10px;
            ">×</button>
        </div>
    `;

    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);

    document.body.appendChild(alertDiv);

    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.style.animation = 'slideInRight 0.3s ease-out reverse';
            setTimeout(() => alertDiv.remove(), 300);
        }
    }, 10000);
}

function updateNotificationBadge() {
    const notifications = JSON.parse(localStorage.getItem('floodNotifications') || '[]');
    const badge = document.getElementById('notificationBadge');

    if (notifications.length > 0) {
        badge.textContent = notifications.length;
        badge.style.display = 'block';
    } else {
        badge.style.display = 'none';
    }
}

// Update badge on page load
document.addEventListener('DOMContentLoaded', function () {
    updateNotificationBadge();
});
