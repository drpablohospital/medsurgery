from app import create_app
from app.models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Hacer usuario_id nullable
    with db.engine.connect() as conn:
        conn.execute(text("ALTER TABLE visitas ALTER COLUMN usuario_id DROP NOT NULL"))
        conn.commit()
    print("OK: usuario_id ahora es nullable")
