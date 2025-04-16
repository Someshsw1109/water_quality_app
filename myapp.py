import os
import logging
# import datetime # Already imported below
from datetime import datetime # Explicit import is fine
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import numpy as np

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy() # Removed (model_class=Base) - handled by DeclarativeBase inherit

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "developmentkey") # Good for prod if env var set
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # Good for proxy deployment

# --- Configuration ---
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///water_analysis.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300, # Good practice for some DBs
    "pool_pre_ping": True, # Good practice
}
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 # 16MB Max upload size
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# --- Initialize Extensions ---
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirect to 'login' view if @login_required fails

# --- Import Models, Forms, ML AFTER db and app are initialized ---
# (Ensure this order is correct based on your project structure)
from models import User, Analysis
from forms import LoginForm, RegistrationForm, AnalysisForm
from ml_model import analyze_water_sample

# --- User Loader for Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    """Loads user by ID for Flask-Login session management."""
    return db.session.get(User, int(user_id))

# --- Context Processor for Current Year ---
@app.context_processor
def inject_current_year():
    """Injects the current year into all templates."""
    return {'current_year': datetime.now().year}

# --- Helper Functions ---
def allowed_file(filename):
    """Checks if the uploaded file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

# --- Routes ---
@app.route('/')
def index():
    """Homepage: Redirects to dashboard if logged in, otherwise shows index."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success') # Add success flash message
            return redirect(next_page or url_for('dashboard'))
        else: # Keep else aligned with if
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('login.html', form=form, title="Login") # Added title

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('That email address is already registered. Please login or use a different email.', 'warning')
            # No redirect here, let user see the form again with the message
        else:
            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
            try:
                db.session.add(user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback() # Rollback on error
                logger.error(f"Error during registration: {str(e)}")
                flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html', form=form, title="Register") # Added title

@app.route('/logout')
@login_required
def logout():
    """Logs the current user out."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Displays the user's dashboard with analysis history charts."""
    try:
        # Fetch analysis records from DB for the current user
        analyses_db = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.timestamp.desc()).all()

        # Convert SQLAlchemy objects to a list of dictionaries suitable for JSON
        analyses_data = []
        for analysis in analyses_db:
            # --- IMPORTANT ---
            # Add ALL fields needed by your charts here.
            # If your Analysis model doesn't have these fields,
            # you MUST add them or change the charts.
            # Using .get() on analysis.__dict__ can be fragile if fields are missing.
            # Explicitly listing fields is safer.
            data_point = {
                'id': analysis.id,
                'date': analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S') if analysis.timestamp else None, # Format needed by JS new Date()
                'image_path': analysis.image_path, # Maybe useful?
                'copper_concentration': analysis.copper_concentration, # From your analyze route
                'risk_level': analysis.risk_level, # From your analyze route
                'analysis_data': analysis.analysis_data, # From your analyze route

                # --- FIELDS NEEDED BY CHARTS (Add to your Analysis model if missing!) ---
                'location': getattr(analysis, 'location', None), # Use getattr for safety if field might be missing
                'ph': getattr(analysis, 'ph', None),
                'hardness': getattr(analysis, 'hardness', None),
                'solids': getattr(analysis, 'solids', None),
                'chloramines': getattr(analysis, 'chloramines', None),
                'sulfate': getattr(analysis, 'sulfate', None),
                'conductivity': getattr(analysis, 'conductivity', None),
                'organic_carbon': getattr(analysis, 'organic_carbon', None),
                'trihalomethanes': getattr(analysis, 'trihalomethanes', None),
                'turbidity': getattr(analysis, 'turbidity', None),
                'drinkable': getattr(analysis, 'drinkable', None), # Assumes boolean or 0/1
            }
            analyses_data.append(data_point)

        # Pass the processed list of dictionaries to the template
        return render_template('dashboard.html', analyses=analyses_data) # Pass the dictionary list

    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        flash('An error occurred while loading the dashboard data.', 'danger')
        # Decide where to redirect or what to render on error
        # Render dashboard but pass empty list might be best
        return render_template('dashboard.html', analyses=[])


@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    """Handles new analysis submission (image upload)."""
    form = AnalysisForm()
    if form.validate_on_submit():
        file = form.image.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S")
            # Include user ID in filename for uniqueness (optional but good)
            new_filename = f"{current_user.id}-{timestamp_str}-{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

            try:
                file.save(filepath)
                logger.info(f"File saved to {filepath}")

                # --- Call your ML model ---
                result = analyze_water_sample(filepath)
                logger.info(f"Analysis result: {result}")

                # --- Create DB record ---
                #  IMPORTANT: Ensure your Analysis model accepts these fields,
                #  AND add fields here for pH, hardness, etc. if they come from the form.
                analysis = Analysis(
                    user_id=current_user.id,
                    timestamp=datetime.now(), # Add timestamp on creation
                    image_path=filepath, # Store relative path? e.g., os.path.join('uploads', new_filename)
                    copper_concentration=result.get('concentration'), # Use .get() for safety
                    risk_level=result.get('risk_level'),
                    analysis_data=result.get('details'), # Assuming 'details' is JSON-serializable

                    # --- ADD OTHER FIELDS FROM FORM HERE ---
                    # location = form.location.data, # Example
                    # ph = form.ph.data,             # Example
                    # ... etc ...
                )
                db.session.add(analysis)
                db.session.commit()
                logger.info(f"Analysis record created with ID: {analysis.id}")
                flash('Analysis successful!', 'success')
                return redirect(url_for('result', analysis_id=analysis.id))

            except Exception as e:
                db.session.rollback() # Rollback DB changes on error
                logger.error(f"Error during analysis or DB save: {str(e)}", exc_info=True) # Log full traceback
                # Attempt to delete saved file if analysis failed? (Optional)
                if os.path.exists(filepath):
                     try: os.remove(filepath)
                     except OSError: logger.error(f"Could not remove file {filepath} after error.")
                flash(f"An error occurred during analysis. Please try again. Error: {str(e)}", 'danger')
                # No redirect here, show form again

        elif not file:
             flash('No file selected. Please upload an image.', 'warning')
        else: # File present but not allowed type
            flash('Invalid file type. Please upload a JPG, JPEG, or PNG image.', 'danger')

    # Render form on GET request or if validation fails/file error
    return render_template('analyze.html', form=form, title="New Analysis") # Added title

@app.route('/result/<int:analysis_id>')
@login_required
def result(analysis_id):
    """Displays the detailed result of a specific analysis."""
    # Use get_or_404 for cleaner handling of not found
    analysis = db.session.get(Analysis, analysis_id)
    if analysis is None:
         flash(f'Analysis with ID {analysis_id} not found.', 'warning')
         return redirect(url_for('dashboard')) # Or render a 404 page

    # Authorization check: ensure the logged-in user owns this analysis
    if analysis.user_id != current_user.id:
        flash('You are not authorized to view this analysis result.', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('result.html', analysis=analysis, title="Analysis Result") # Added title

# --- Create DB tables if they don't exist ---
# It's often better to use Flask-Migrate for managing schema changes
# but this is okay for initial setup or simple apps.
with app.app_context():
    logger.info("Creating database tables if they don't exist...")
    db.create_all()
    logger.info("Database tables check complete.")

# --- Run the Application ---
if __name__ == '__main__':
    # Consider setting debug=False in production
    app.run(host='0.0.0.0', port=5000, debug=True)