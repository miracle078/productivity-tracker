# Productivity and Health Monitoring System

for IX IoT Module

This system integrates Internet of Things (IoT) technologies and advanced data analytics to track and correlate personal productivity metrics (keyboard/mouse activity) with health data obtained from wearable devices through the Google Fit API. The platform provides actionable insights and personalized recommendations to enhance productivity and well-being.

## Features

### **Core Functionality**
- **Keyboard and Mouse Tracker**: Monitors active engagement by logging keystrokes and mouse activity.
- **Google Fit Integration**: Fetches health metrics, including steps, active minutes, calories expended, sleep quality, and heart rate.
- **Real-Time Data Synchronization**: Combines local data from keyboard/mouse logging with health metrics fetched from Google Fit.
- **Visualization Dashboard**: Displays insights on productivity trends and health metrics through an AWS-hosted dashboard.

### **Advanced and Future Features**
- **Data Correlation**: Identifies relationships between productivity and health indicators.
- **Predictive Analytics**: Forecasts productivity trends based on historical data.
- **Anomaly Detection**: Flags unusual deviations in health or productivity patterns for proactive interventions.
- **Personalized Recommendations**: Suggests habit adjustments and breaks based on analyzed data.

## System Architecture

### **Data Sources**
1. **Keyboard and Mouse Logger**
   - Captures user activity in real-time.
   - Logs events to a local SQLite database.

2. **Google Fit API**
   - Retrieves health metrics through secure OAuth 2.0 authentication.
   - Aggregates data on steps, active minutes, sleep quality, heart rate, calories, and activity segments.

### **Data Processing**
- Data is locally cached and preprocessed for consistency.
- Periodic synchronization with AWS ensures real-time updates and unified storage.
- Machine learning algorithms are applied for correlation, time-series analysis, and noise reduction.

### **Visualization Platform**
- Hosted on Amazon EC2 using Flask for backend services.
- Frontend provides interactive dashboards for real-time and historical analysis.
- Containerized using Docker for scalability and security.

## Installation and Setup

### **Local Environment**
1. Clone the repository:
   ```bash
   git clone https://github.com/miracle078/productivity-tracker.git
   cd productivity-tracker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the keyboard/mouse logger locally:
   ```bash
   python agent.py
   ```

### **Google Fit API Setup**
1. Set up credentials in Google Cloud Console:
   - Create a project.
   - Enable the Google Fit API.
   - Download the `credentials.json` file.
2. Authenticate:
   - Run the authentication script to generate a `token.json` file:
     ```bash
     python google_fit_export.py
     ```

3. Fetch health metrics:

These get fetched right after authentication is complete.

### **AWS Deployment**
1. Build and deploy the Flask app:
   ```bash
   docker build -t flask-keyboard-app
   docker run -d -p 5000:5000 flask-keyboard-app
   ```
2. Access the dashboard at `http://<AWS_INSTANCE_PUBLIC_IP>:5000`.

## Usage
- **Keyboard/Mouse Logger**: Runs locally to log activity data in real-time.
- **Health Data Fetching**: Periodically fetches and synchronizes health metrics with AWS.
- **Visualization Dashboard**: Displays insights and enables data export for further analysis.

## Future Enhancements
1. **IoT Sensor Integration**:
   - Add environmental sensors to monitor air quality, lighting, and noise.
2. **Enhanced Analytics**:
   - Incorporate stress and cognitive load metrics.
   - Develop predictive models for long-term productivity planning.
3. **Recommendations and Alerts**:
   - Introduce AI-powered coaching for personalized advice.
   - Add gamification and collaborative productivity features.
4. **Broader Applications**:
   - Extend to educational, healthcare, and athletic performance tracking.

## Security and Privacy
- **End-to-End Encryption**: TLS 1.3 secures data in transit.
- **Anonymization**: All sensitive data is anonymized before cloud synchronization.
- **User Consent Management**: Provides granular control over data sharing.
- **RBAC**: Ensures role-based access to protect sensitive information.

## Troubleshooting
1. **Common Errors**
   - **OAuth Authentication Issues**: Ensure `credentials.json` and `token.json` are correctly configured.
   - **API Rate Limits**: Adjust fetch intervals to comply with Google Fit API policies.

2. **Debugging**
   - Use log files generated by the scripts for error tracing.
   - Test individual components locally to isolate issues.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

For further queries or contributions, feel free to reach out at `cybercentinel@gmail.com` or open an issue in the repository.
