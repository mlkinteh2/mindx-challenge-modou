# MIND X Technical Challenge - Maritime Compliance System
<img width="1835" height="877" alt="image" src="https://github.com/user-attachments/assets/db66383e-5fb8-4237-88a2-598ede2c0e5a" />


## 🚢 Project Overview

This project implements a comprehensive maritime emissions compliance system for the MIND X Technical Challenge. It addresses the transition from simple data visibility to **Algorithmic Intelligence** and **Financialized Compliance** under the FuelEU Maritime regulations (January 2025).

### Key Features

- **Task A**: Compliance Engine with ML-based CO2 prediction and regulatory benchmarking
- **Task B**: Interactive Fleet Arbitrage Dashboard for compliance visualization
- **Task C**: Deep Research Technical Memo with anomaly detection and physical reasoning

---

## 📁 Project Structure

```
mindx-challenge-modou/
├── backend/
│   ├── data/
│   │   └── mindx test dataset.csv
│   ├── models/                      # Trained ML models (generated)
│   ├── compliance_engine.py         # Core compliance logic
│   ├── api.py                       # FastAPI backend service
│   ├── model.ipynb                  # ML model training notebook
│   ├── requirements.txt
│   └── env/                         # Python virtual environment
├── dashboard/
│   ├── index.html                   # Main dashboard UI
│   ├── styles.css                   # Premium styling
│   └── app.js                       # Frontend logic & API integration
├── TaskC_Memo/
│   ├── anomaly_detection.py         # Anomaly analysis script
│   ├── anomaly_analysis.png         # Visualization
│   ├── ng008_anomaly_scatter.png    # Highlighted outlier scatter plot
│   
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Modern web browser
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mindx-challenge-modou
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv env
   
   # Windows
   env\Scripts\activate
   
   # Linux/Mac
   source env/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Train the ML model** (Optional - if models don't exist)
   ```bash
   jupyter notebook model.ipynb
   # Run all cells to train and save the model
   ```

4. **Run the compliance engine**
   ```bash
   python compliance_engine.py
   ```

5. **Start the API server**
   ```bash
   python api.py
   # Server will run on http://localhost:8000
   # API docs: http://localhost:8000/docs
   ```

6. **Open the dashboard**
   ```bash
   # Open dashboard/index.html in your browser
   # Or use a local server:
   cd dashboard
   python -m http.server 3000
   # Visit http://localhost:3000
   ```

---

## 📊 Task A: Compliance Engine

### Features

- **CO2 Emission Prediction**: ML model trained on vessel operational data
- **GHG Intensity Calculation**: `GHG Intensity = CO2 (g) / Distance (nm)`
- **Regulatory Benchmarking**: 2026 target = 5% reduction from fleet average
- **Compliance Balance**: Identifies surplus and deficit vessels
- **Financial Impact**: Calculates penalties at $100/ton excess CO2

### Results

- **Total Vessels**: 120
- **Surplus Vessels**: 51 (below target)
- **Deficit Vessels**: 69 (above target)
- **Fleet Average GHG Intensity**: 78,853.50 gCO₂/mile
- **2026 Target Intensity**: 74,910.82 gCO₂/mile

### API Endpoints

```
GET  /api/compliance/summary       # Fleet compliance summary
GET  /api/compliance               # Full compliance report
GET  /api/vessels                  # List all vessels
GET  /api/vessels/{vessel_id}      # Vessel details
POST /api/pooling                  # Simulate vessel pooling
GET  /api/pooling/optimal          # Get optimal pooling opportunities
POST /api/predict                  # Predict CO2 emissions
```

---

## 🎨 Task B: Fleet Arbitrage Dashboard

### Features

1. **Liability Map**
   - Visual categorization of vessels by penalty risk
   - Interactive charts showing compliance distribution
   - Real-time stats cards with key metrics

2. **Pooling Simulator**
   - Select deficit and surplus vessels
   - Instant calculation of pooling effectiveness
   - Financial savings analysis
   - Optimal pooling recommendations

### Design Highlights

- **Premium UI**: Modern gradient design with smooth animations
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live data from FastAPI backend
- **Interactive Charts**: Chart.js visualizations
- **Smooth UX**: Micro-animations and transitions

### Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Custom CSS with modern design system
- **Charts**: Chart.js
- **API**: Fetch API for backend integration

---

## 🔬 Task C: Technical Memo

### Anomaly Detection Methods

1. **Statistical Outlier Detection (Z-Score)**
   - Identifies vessels with Z-score > 3
   - Analyzes fuel efficiency, CO2 intensity, and fuel consumption

2. **Fuel Consumption vs Distance Analysis**
   - Linear regression by ship type
   - Detects deviations > 50% from expected values

### Key Findings

**Critical Anomaly Identified**: Vessels with abnormally high fuel consumption relative to distance traveled.

**Physical Reasoning**:

1. **Hull Biofouling**
   - Marine organism growth increases friction
   - Can increase fuel consumption by 20-60%
   - Requires regular hull cleaning

2. **Parametric Rolling**
   - Dangerous rolling motion in adverse seas
   - Causes significant speed loss and fuel waste
   - Weather-dependent phenomenon

3. **Engine Degradation**
   - Worn components reduce combustion efficiency
   - Requires maintenance and overhaul

4. **Adverse Weather Conditions**
   - High waves and wind increase resistance
   - May require speed reduction or route deviation

### Visualizations

- Fuel Consumption vs Distance (with anomalies highlighted)
- CO2 Intensity Distribution by Ship Type
- Fuel Efficiency Distribution
- Weather Impact on Fuel Consumption

---

## 🛠️ Technical Details

### Machine Learning Model

- **Algorithm**: Random Forest Regressor (best performing)
- **Features**: Distance, fuel consumption, engine efficiency, ship type, route, month, fuel type, weather
- **Preprocessing**: Label encoding for categorical variables, standard scaling
- **Performance**: High R² score with low RMSE

### Backend Architecture

- **Framework**: FastAPI (Python)
- **Data Processing**: Pandas, NumPy
- **ML Libraries**: Scikit-learn, SciPy
- **Visualization**: Matplotlib, Seaborn
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

### Frontend Architecture

- **State Management**: Vanilla JavaScript with global state object
- **API Integration**: Async/await with Fetch API
- **Error Handling**: Graceful degradation and user feedback
- **Performance**: Lazy loading and efficient rendering

---

## 📈 Results & Impact

### Compliance Optimization

- Identified **51 surplus vessels** that can offset deficits
- Calculated **optimal pooling opportunities** saving up to $50,000+ per pool
- Provided **actionable insights** for fleet managers

### Anomaly Detection

- Detected **multiple outliers** requiring investigation
- Linked anomalies to **physical phenomena** (biofouling, rolling, etc.)
- Enabled **predictive maintenance** and route optimization

### Business Value

- **Reduced Compliance Costs**: Through strategic vessel pooling
- **Improved Efficiency**: By identifying and addressing anomalies
- **Data-Driven Decisions**: Real-time compliance monitoring
- **Regulatory Compliance**: Meeting FuelEU Maritime requirements

---

## 🔮 Future Enhancements

1. **Real-time Data Integration**: Connect to vessel IoT sensors
2. **Advanced ML Models**: Deep learning for better predictions
3. **Route Optimization**: AI-powered route planning
4. **Mobile App**: Native iOS/Android applications
5. **Blockchain Integration**: Transparent compliance tracking
6. **Weather API**: Real-time weather data integration

---

## 📝 License

This project was created for the MIND X Technical Challenge.

---

## 👤 Author

**Modou**
- Challenge: MIND X Technical Test
- Date: January 2026
- Theme: From Digitization to Algorithmic Intelligence

---

## 🙏 Acknowledgments

- MIND X for the challenging and insightful technical test
- Maritime industry for the inspiration
- Open-source community for the amazing tools and libraries

---

## 📞 Contact

For questions or feedback about this project, please reach out through the MIND X recruitment process.

---


**Built with ❤️ for a sustainable maritime future** 🌊

