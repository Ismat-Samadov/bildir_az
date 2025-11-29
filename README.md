# Credit Scoring Model - German Credit Data

A comprehensive credit scoring analysis and machine learning model built on the German Credit dataset from the UCI Machine Learning Repository.

## 📊 Project Overview

This project performs end-to-end credit risk analysis including:
- Exploratory Data Analysis (EDA)
- Data preprocessing and feature engineering
- Multiple ML model comparison (Logistic Regression, Random Forest, XGBoost)
- Credit score generation (300-850 FICO-style scale)
- Risk categorization and assessment

## 🎯 Key Features

### Models Implemented
- **Logistic Regression** (Best performer - ROC-AUC: 0.800)
- **Random Forest**
- **XGBoost**

### Comprehensive Metrics
- **Accuracy** - Overall correctness
- **Precision** - Positive predictive value
- **Recall** - Sensitivity/True positive rate
- **F1-Score** - Harmonic mean of precision and recall
- **ROC-AUC** - Area under ROC curve
- **Gini Coefficient** - Model discrimination power (2×AUC - 1)
- **KS Statistic** - Kolmogorov-Smirnov test for class separation

### Risk Categories
- **Excellent** (740-850): Very low risk
- **Good** (670-739): Low risk
- **Fair** (580-669): Medium risk
- **Poor** (500-579): High risk
- **Very Poor** (300-499): Very high risk

## 📁 Project Structure

```
scoring/
├── credit_scoring_analysis.ipynb    # Main analysis notebook
├── german_credit_data/
│   ├── german.data                  # Dataset (categorical)
│   ├── german.data-numeric          # Dataset (numeric)
│   ├── german.doc                   # Dataset documentation
│   └── Index                        # File index
├── credit_scoring_results.csv       # Individual credit scores
├── model_comparison.csv             # Model performance metrics
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
└── venv/                           # Virtual environment (not in git)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the repository**

2. **Create a virtual environment**
```bash
python3 -m venv venv
```

3. **Activate the virtual environment**
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Analysis

1. **Start Jupyter Notebook**
```bash
jupyter notebook
```

2. **Open the notebook**
   - Navigate to `credit_scoring_analysis.ipynb`
   - Run all cells (Cell → Run All)

3. **View results**
   - Interactive visualizations in the notebook
   - `credit_scoring_results.csv` - Individual predictions
   - `model_comparison.csv` - Model performance comparison

## 📈 Results Summary

### Best Model: Logistic Regression

| Metric | Value |
|--------|-------|
| Accuracy | 78.5% |
| Precision | 66.0% |
| Recall | 58.3% |
| F1-Score | 61.9% |
| ROC-AUC | 0.800 |
| Gini | 0.600 |
| KS Statistic | 0.552 |

### Credit Score Statistics
- **Mean**: 678.38
- **Range**: 349 - 847
- **Median**: 727.00

### Risk Distribution (Test Set)
- Excellent: 47.5%
- Good: 11.0%
- Fair: 13.5%
- Poor: 13.5%
- Very Poor: 14.5%

## 📊 Dataset Information

**Source**: UCI Machine Learning Repository - German Credit Data

**Records**: 1,000 credit applications

**Features**: 20 attributes including:
- Checking account status
- Credit duration
- Credit history
- Credit amount
- Savings account balance
- Employment status
- Age
- Housing status
- And more...

**Target**: Credit risk (Good/Bad)

## 🔍 Key Insights

1. **Model Performance**: Logistic Regression achieves excellent discrimination with Gini = 0.60 and KS = 0.55
2. **Feature Importance**: Checking account status, credit duration, and credit amount are top predictors
3. **Class Imbalance**: 70% good credit, 30% bad credit - handled with stratified splitting
4. **Practical Application**: Model can effectively rank customers by credit risk

## 📝 Model Interpretation

### Gini Coefficient (0.600)
- Indicates **good model discrimination**
- Range: -1 to 1 (higher is better)
- Interpretation: Model can effectively distinguish between good and bad credit

### KS Statistic (0.552)
- Indicates **excellent class separation**
- Industry benchmark: KS > 0.4 is excellent
- Optimal threshold identified for decision-making

## 🛠️ Technologies Used

- **Python 3.10**
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **scikit-learn** - Machine learning
- **XGBoost** - Gradient boosting
- **matplotlib/seaborn** - Data visualization
- **Jupyter** - Interactive notebooks

## 📄 License

This project uses the German Credit dataset from the UCI Machine Learning Repository, which is freely available for research purposes.

## 🤝 Contributing

Suggestions and improvements are welcome! Feel free to:
- Report issues
- Suggest new features
- Improve documentation
- Enhance model performance

## 📧 Contact

For questions or feedback, please open an issue in the repository.

---

**Note**: This model is for educational and research purposes. For production credit scoring systems, additional validation, regulatory compliance, and fairness testing are required.
