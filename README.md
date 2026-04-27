# CarDekho-Predict 🚗

**VahanValue** — A Used Car Price Predictor using Machine Learning

Predicts resale prices for used cars in India with a modern web interface and REST API backend.

## 🎯 Overview

This is a **100% Python** machine learning application that predicts used car resale prices based on vehicle characteristics. Built for a college PSDL project, it combines:

- **Streamlit** for an interactive multi-page UI
- **Flask** REST API backend with ML model
- **scikit-learn** RandomForestRegressor for predictions
- **SQLite** for user authentication and prediction history
- **Pandas & NumPy** for data processing

### Tech Stack

```
┌─────────────────────────┐         ┌──────────────────────────┐
│  Streamlit (UI)         │─HTTP──→ │  Flask Backend           │
│  app.py :8081           │         │  backend/app.py:8000     │
└─────────────────────────┘         │  - RandomForest ML       │
                                    │  - SQLite (app.db)       │
                                    │  - Authentication        │
                                    └──────────────────────────┘
                                             ↓
                                      cardekho.csv
                                      (15,411 rows)
```

## 📊 Features

- **🔐 User Authentication** - Secure login system with SQLite storage
- **📈 Price Prediction** - Real-time car price predictions
- **🔍 Compare Cars** - Compare prices across different models
- **📉 Market Analysis** - Visualize market trends with Plotly
- **📋 Prediction History** - Track all your past predictions
- **📱 Responsive Dashboard** - Modern, interactive web interface

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- pip or uv package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/S14BF/CarDekho-Predict.git
   cd CarDekho-Predict
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install individual packages:
   ```bash
   pip install flask flask-cors numpy pandas plotly requests scikit-learn streamlit
   ```

### Running the Application

#### Terminal 1: Start Flask Backend (API Server)
```bash
cd backend
python app.py
```
Backend runs on: `http://localhost:8000`

#### Terminal 2: Start Streamlit Frontend (UI)
```bash
streamlit run app.py --server.port=8081
```
Frontend runs on: `http://localhost:8081`

## 📁 Project Structure

```
CarDekho-Predict/
├── app.py                          # Streamlit frontend (multi-page UI)
├── backend/
│   ├── app.py                      # Flask API server
│   ├── cardekho.csv                # Training dataset (15,411 cars)
│   ├── app.db                      # SQLite database (auto-created)
│   └── requirements.txt            # Backend dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── lib/                            # Shared libraries & API specs
│   ├── api-client-react/           # React API client
│   ├── api-spec/                   # OpenAPI specification
│   ├── api-zod/                    # Zod type definitions
│   └── db/                         # Database schema
├── pyproject.toml                  # Python project metadata
└── README.md                       # This file
```

## 📊 Dataset

- **Source**: CarDekho (Indian used car marketplace)
- **Rows**: 15,411 cars
- **Features**: Brand, model, year, price, mileage, fuel type, transmission, etc.
- **Location**: `backend/cardekho.csv`

## 🤖 Machine Learning Model

- **Algorithm**: RandomForestRegressor (scikit-learn)
- **Training Samples**: 12,328
- **Performance**: 
  - R² Score: **0.9367** (93.67% accuracy)
  - Mean Absolute Error: **₹99,574**

## 🔌 API Endpoints

### Backend API (Flask)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Predict car price |
| GET | `/health` | API health check |
| POST | `/auth/login` | User login |
| POST | `/auth/register` | Create new user |
| GET | `/history` | Get user's prediction history |

## 🛠️ Configuration

### Streamlit Config
Edit `.streamlit/config.toml` to customize:
- Server settings
- UI theme
- Font and layout

### Flask Config
Edit `backend/app.py` to modify:
- CORS settings
- Database path
- Debug mode

## 📝 Usage Example

1. **Open the app**: http://localhost:8081
2. **Login/Register** with your credentials
3. **Navigate to Predict** page
4. **Enter car details**:
   - Brand, Model, Year
   - Mileage, Fuel Type, Transmission
   - Number of Owners, etc.
5. **Get instant price prediction**
6. **View prediction history** anytime

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change Streamlit port
streamlit run app.py --server.port=8082

# Change Flask port (edit backend/app.py)
if __name__ == '__main__':
    app.run(port=8001)
```

### Database Issues
```bash
# Reset database
rm backend/app.db
# App will auto-create on next run
```

### Dependency Issues
```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

## 📦 Dependencies

- **flask** (3.0.3) - Web framework
- **numpy** (1.26.4) - Numerical computing
- **pandas** (2.2.2) - Data manipulation
- **scikit-learn** (1.5.1) - ML algorithms
- **streamlit** (1.56.0+) - UI framework
- **plotly** (6.7.0+) - Interactive charts



## 📄 License

This project is provided as-is for educational purposes.

## 🤝 Contributing

Feel free to fork this project and submit pull requests with improvements!

## 📧 Contact

For questions or issues, please open a GitHub issue or contact the maintainer.

---


