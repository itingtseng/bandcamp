from app import db, create_app

# Initialize Flask app
app = create_app()

# Use application context
with app.app_context():
    try:
        # Inspect database tables
        table_names = db.inspect(db.engine).get_table_names()
        print("Database Tables:", table_names)

        # Inspect schema for a specific table
        table_name = 'cards'
        schema_info = db.engine.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}';
        """).fetchall()
        print(f"Schema for table '{table_name}':", schema_info)

    except Exception as e:
        print(f"Error occurred: {e}")
