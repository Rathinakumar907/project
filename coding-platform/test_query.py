
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend import models, schemas
import json

def test_query():
    db = SessionLocal()
    output = []
    try:
        output.append(f"ProblemResponse Config orm_mode: {getattr(schemas.ProblemResponse.Config, 'orm_mode', 'MISSING')}")
        
        problems = db.query(models.Problem).all()
        output.append(f"Found {len(problems)} problems")
        for p in problems:
            output.append(f"Problem: {p.title}")
            try:
                # Use from_orm correctly for Pydantic V1/V2 compatibility check
                if hasattr(schemas.ProblemResponse, 'model_validate'):
                    # Pydantic V2
                    resp = schemas.ProblemResponse.model_validate(p, from_attributes=True)
                else:
                    # Pydantic V1
                    resp = schemas.ProblemResponse.from_orm(p)
                output.append(f"Serialized: {resp.json()}")
            except Exception as e:
                output.append(f"Serialization failed for {p.title}: {e}")
                import traceback
                output.append(traceback.format_exc())
    except Exception as e:
        output.append(f"Query level error: {e}")
        import traceback
        output.append(traceback.format_exc())
    finally:
        db.close()
    
    with open('error_log.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

if __name__ == "__main__":
    test_query()
