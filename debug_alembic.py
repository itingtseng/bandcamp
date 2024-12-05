from app.models.db import db  # Import your db instance from the app
from app import create_app    # Import your app factory if using Flask

# Create the app and context
app = create_app()
with app.app_context():
    # Query the alembic_version table
    result = db.session.execute("SELECT * FROM alembic_version;")

    # Fetch and print all rows
    for row in result:
        print(row)
