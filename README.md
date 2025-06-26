## Expense Tracker Setup Instructions

### Requirements
- Python 3.9+
- Virtual environment tool (`venv`)

### Setup Steps
1. Unzip the folder
2. Open Terminal and navigate to the project directory
3. Run:

# Step 1: Create and activate virtual environment
python3 -m venv venv && source venv/bin/activate

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Apply migrations
python3 manage.py migrate

# Step 4: Load seed data (if these files exist)
python3 manage.py loaddata seed_data/seed_categories.json
python3 manage.py loaddata seed_data/seed_expenses.json

# Step 5: Run the server
python3 manage.py runserver