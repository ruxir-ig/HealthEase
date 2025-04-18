# HealthEase - AI Driven Healthcare Innovation

![HealthEase Logo](logo.png)

## Overview

HealthEase is a comprehensive AI-powered healthcare platform designed to empower individuals in their health journey. The application leverages cutting-edge artificial intelligence to help users understand medical research, analyze symptoms preliminarily, and track wellness goals effectively.

## Features

### 🔍 Research Analyzer
- Upload and analyze medical research papers (PDF format)
- Get AI-generated summaries and key findings
- Make complex medical literature more accessible

### 🩺 Symptom Analyzer
- Input symptoms and receive preliminary AI analysis
- Get severity assessments and possible conditions
- Receive personalized recommendations for next steps
- All analyses are stored for future reference

### ❤️‍🩹 Wellness Tracker
- Monitor vital health metrics
- Track fitness goals and progress
- Visualize health trends over time
- Stay proactive about your health

## Technology Stack

- **Backend**: Python, Streamlit
- **Database**: MongoDB
- **AI/ML**: Integrated AI services for research analysis and symptom assessment
- **Authentication**: Custom authentication system

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/HealthEase.git
   cd HealthEase
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Setup your environment variables:
   Create a `.streamlit/secrets.toml` file in the root directory with the following variables:
   ```
   MONGODB_URI="your_mongodb_connection_string"
   SECRET_KEY="your_secret_key"
   API_KEY="your_ai_service_api_key (if applicable)"
   ```

4. Run the application:
   ```
   streamlit run app.py
   ```

## Project Structure

```
app.py               # Main application entry point
logo.png             # Application logo
requirements.txt     # Python dependencies
config/              # Configuration settings
utils/
  ├── auth.py            # Authentication functions
  ├── database.py        # Database operations
  ├── research_analyzer.py # Research paper analysis
  ├── symptom_analyzer.py  # Symptom analysis
  └── wellness_tracker.py  # Wellness tracking
```

## User Roles

- **Patients**: Access to all features - Research Analyzer, Symptom Analyzer, and Wellness Tracker
- **Doctors**: Access to Research Analyzer and Wellness Tracker
- **Researchers**: Full access to all platform features

## Security

- Secure authentication system
- Encrypted password storage
- Protected user health data

## Disclaimer

The AI insights provided by HealthEase are informational only and not a substitute for professional medical advice. Always consult a qualified healthcare provider for any health concerns or before making any decisions related to your health or treatment.

## Future Enhancements

- Mobile application development
- Integration with wearable devices
- Expanded medical research database
- Telehealth consultation features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For support or inquiries, please contact: krishnanaicker2005@gmail.com