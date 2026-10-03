from app.database import SessionLocal
from app.detection.engine import run_detection


db = SessionLocal()

result = run_detection(
    db=db,
    source_ip="10.0.0.99",
    username="testuser"
)

print(result)

db.close()