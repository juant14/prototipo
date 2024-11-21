from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ScoreValidationInput(BaseModel):
    difficulty: float
    execution: float
    penalties: float

@app.post("/validate_score/")
async def validate_score(data: ScoreValidationInput):
    # Rango permitido para cada componente
    difficulty_min, difficulty_max = 0.0, 10.0   # Rango típico de dificultad
    execution_min, execution_max = 0.0, 10.0     # Rango típico de ejecución, comienza en 10 y se reduce
    penalties_min = 0.0                          # Penalizaciones sin límite superior en este caso

    # Validación de Dificultad (D-score)
    if not (difficulty_min <= data.difficulty <= difficulty_max):
        return {
            "valid": False,
            "message": f"Dificultad fuera de rango: debe estar entre {difficulty_min} y {difficulty_max}."
        }

    # Validación de Ejecución (E-score)
    if not (execution_min <= data.execution <= execution_max):
        return {
            "valid": False,
            "message": f"Ejecución fuera de rango: debe estar entre {execution_min} y {execution_max}."
        }

    # Validación de Penalizaciones (no puede ser negativa)
    if data.penalties < penalties_min:
        return {
            "valid": False,
            "message": "Penalizaciones fuera de rango: debe ser 0 o mayor."
        }

    # Si todas las validaciones pasan
    return {
        "valid": True,
        "message": "Confirmamos que los resultados están dentro del rango."
    }
