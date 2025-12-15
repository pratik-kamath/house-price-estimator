# 🏡 House Price Estimator with Explainability (Sydney, AU)

This project predicts property prices in the Sydney real estate market using machine learning, based on scraped data from public real estate listings. It also includes SHAP-based model explainability to understand how different features (location, size, etc.) influence price.

## 🔧 Features

- **Data Source**: [NSW Valuer General](https://www.valuergeneral.nsw.gov.au/__psi/yearly/20XX.zip) (Replace `20XX` with the year, e.g., `2023`)
- Cleans and preprocesses real estate data
- Trains a regression model (XGBoost or CatBoost)
- Uses SHAP to explain predictions
- Web app frontend to input property details and get predictions + explanations
- Deployable via Docker

## 🧪 Stack

- **Python 3.10+**
- `BeautifulSoup`, `Selenium` – Web scraping
- `pandas`, `numpy` – Data preprocessing
- `XGBoost`, `CatBoost` – Regression models
- `SHAP` – Model explainability
- `Streamlit` / `FastAPI` – Web interface
- `Docker` – Deployment
- `matplotlib`, `seaborn` – Data visualization

## 🚀 How to Run

```bash
git clone https://github.com/your-username/house-price-estimator.git
cd house-price-estimator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
