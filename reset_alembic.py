from app.models.db import db
from app import create_app

app = create_app()
with app.app_context():
    # Clear the alembic_version table
    db.session.execute("DELETE FROM alembic_version;")
    db.session.commit()
    print("alembic_version table reset successfully.")
