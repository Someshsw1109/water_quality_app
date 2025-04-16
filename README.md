# 💧 Water Quality Analysis Web Application

[![Language](https://img.shields.io/badge/Language-Python-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![Frontend](https://img.shields.io/badge/Frontend-Bootstrap_5-purple.svg)](https://getbootstrap.com/)
[![Charts](https://img.shields.io/badge/Charts-Chart.js-red.svg)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) <!-- Add a LICENSE file (e.g., MIT) -->

A Flask-based web application designed to analyze water quality by predicting parameters (initially focused on copper concentration) from uploaded sample images using a machine learning model.

**GitHub Repository:** [https://github.com/aryan-0302/water_quality_app](https://github.com/aryan-0302/water_quality_app)

---

## ✨ Features

*   ✅ **User Authentication:** Secure user registration, login, and logout functionality using Flask-Login.
*   ✅ **Image Upload:** Users can upload images of water samples for analysis.
*   ✅ **Machine Learning Analysis:** Integrates an ML model (`ml_model.py`) to process images and predict water quality parameters (e.g., copper concentration, risk level).
*   ✅ **Interactive Dashboard:** Displays historical analysis results for the logged-in user using dynamic charts (powered by Chart.js) instead of a static table.
*   ✅ **Detailed Results:** Shows specific results for each analysis performed.
*   ✅ **Responsive Design:** Utilizes Bootstrap 5 for a user interface that adapts to different screen sizes.
*   ✅ **Database Storage:** Uses SQLAlchemy to store user information and analysis results (defaults to SQLite).

---

## 📸 Screenshots (Example Placeholders)

*Add screenshots of your application here to showcase the UI!*

**(Example: Dashboard View)**
![Dashboard Screenshot](placeholder_dashboard.png)

**(Example: Analysis Form)**
![Analysis Form Screenshot](placeholder_analyze.png)

**(Example: Result Page)**
![Result Screenshot](placeholder_result.png)

---

## 🛠️ Technology Stack

*   **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Werkzeug
*   **Database:** SQLite (Default), easily configurable for others like PostgreSQL via `DATABASE_URL`.
*   **Frontend:** HTML5, CSS3, JavaScript
*   **UI Framework:** Bootstrap 5
*   **Charting:** Chart.js
*   **ML Model:** (Specify details if possible, e.g., Scikit-learn, TensorFlow, PyTorch - currently abstracted in `ml_model.py`)

---

## 🚀 Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

*   Python 3.8+
*   pip (Python package installer)
*   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/aryan-0302/water_quality_app.git
    cd water_quality_app
    ```

2.  **Create and activate a virtual environment (Recommended):**
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You might need to create a `requirements.txt` file first using `pip freeze > requirements.txt` if you haven't already).*

### Configuration

The application uses environment variables for configuration:

*   `SESSION_SECRET`: A secret key for session management. Set this to a long, random string for production. (A default is provided for development).
*   `DATABASE_URL`: The connection string for your database. Defaults to a local SQLite file (`sqlite:///water_analysis.db`).

You can set these variables directly in your environment or use a `.env` file (you would need to install `python-dotenv` and load it in `myapp.py` for this).

### Database Setup

The application uses Flask-SQLAlchemy. The necessary database tables will be created automatically the first time the application runs, thanks to `db.create_all()` within the application context.

For production or more complex schema changes, consider using Flask-Migrate.

### Running the Application

1.  **Start the Flask development server:**
    ```bash
    python myapp.py
    ```

2.  **Open your web browser** and navigate to `http://127.0.0.1:5000` or `http://localhost:5000`.

---

## Usage

1.  **Register:** Create a new user account.
2.  **Login:** Sign in with your credentials.
3.  **Analyze:** Navigate to "New Analysis", upload an image of a water sample, and submit the form.
4.  **View Results:** You will be redirected to the result page for the specific analysis.
5.  **Dashboard:** Access the dashboard to see a history of your analyses visualized with charts.
6.  **Logout:** End your session securely.

---

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeatureName`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/YourFeatureName`).
6.  Open a Pull Request.

Please ensure your code adheres to basic Python coding standards (PEP 8).

---

## 👥 Contributors

*   **Somesh Raj**
*   **Aryan Agarwal**

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (assuming you add an MIT license file).