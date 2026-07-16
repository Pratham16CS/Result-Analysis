# Result Analysis System 📊

An interactive, full-stack Streamlit web application designed to automate academic performance analysis. This system consolidates multiple statistical processes—such as outlier detection, pass/fail computations, grade profiling, percentile mappings, and professional Excel reporting—into a single, unified interface.

The application evolved from a collection of standalone command-line Python scripts into a robust, interactive utility for educators and class coordinators.

---

## 🌟 Features

### 📁 1. Data Upload & Cleaning
- **Multi-format Support:** Seamlessly upload `.csv`, `.xlsx`, and `.xls` files.
- **Interactive Previews:** Filter and display specific columns dynamically.
- **Imputation Tools:** Handle missing records by dropping them or imputing them with mean/mode strategies.
- **Outlier Detection:** Automatically detect outliers using the Interquartile Range (IQR) method, with options to keep, cap, or remove them.

### 📈 2. Basic Analysis
- **Summary Statistics:** View instantly calculated mean, median, standard deviation, and quartile breakdowns.
- **Interactive Distributions:** Visual representations of mark distributions with annotated mean/median lines.
- **Custom Pass/Fail Sliders:** Dynamically set custom passing thresholds and maximum marks to observe pass percentages, averages, and pass/fail distribution pie charts.
- **Top & Bottom Performers:** Automatically ranks and highlights the top 5 and bottom 5 student performers for any selected subject.

### 🔬 3. Advanced Analysis
- **Subject-Wise Comparison:** Compare mark spreads across multiple subjects side-by-side using Seaborn boxplots.
- **Correlation Matrix:** Compute and visualize cross-subject correlation with a masked heatmap to discover core performance trends.
- **Customizable Grading Profile:** Define your own grade boundaries (A, B, C, D, F) using interactive sliders and display the corresponding grade counts and averages.
- **Percentile Curves:** Map academic performance on a continuous percentile distribution graph.

### 📄 4. Professional Report Generation
- **Composite Reports:** Generate consolidated tables tracking subject-by-subject results, overall totals, and final percentages.
- **Formatted Excel Exports:** Export highly polished, multi-sheet Excel workbooks generated with `xlsxwriter` containing:
  - **`Detailed Report`**: Full student grades and status.
  - **`Summary`**: Aggregated pass rates and averages.
  - **`Statistics`**: Descriptive statistics per subject.
  - **`Charts`**: Automatically embedded interactive Excel pie charts plotting overall pass/fail metrics.

---

## 🛠️ System Prerequisites

Ensure you have Python installed (v3.10+ recommended).

### 1. Project Dependencies
The application relies on the following Python packages:
- `streamlit`
- `pandas`
- `matplotlib`
- `seaborn`
- `numpy`
- `openpyxl`
- `xlsxwriter`

---

## 💻 Command Prompt & Setup Instructions

Open your terminal or command prompt and execute the following commands to configure and launch the system:

### Step 1: Clone or Navigate to Your Project Directory
```bash
# Navigate to the directory containing your project files
cd path/to/your/result_analysis_project
```

### Step 2: Create a Virtual Environment (Recommended)
Creating a virtual environment ensures dependencies do not conflict with other Python projects on your machine.

**On Windows:**
```cmd
# Create virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
# Create virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### Step 3: Install Required Packages
Install all necessary libraries using `pip`:
```bash
pip install streamlit pandas matplotlib seaborn numpy openpyxl xlsxwriter
```

### Step 4: Run the Streamlit Application
Start the server and launch the app in your local browser:
```bash
streamlit run main.py
```

*Note: If the app does not open automatically, copy and paste the `Local URL` (typically `http://localhost:8501`) shown in your terminal into any web browser.*

---

## 📋 Sample Input Format Guide
For optimal performance, your uploaded Excel or CSV file should contain:
1. One column dedicated to Student IDs or Names (e.g., `Name` or `Roll`).
2. Numerical score columns for each subject (e.g., `Physics`, `Chemistry`, `Maths`).

---

*Developed to simplify academic progress tracking and deliver instant, boardroom-ready statistical insights.*
