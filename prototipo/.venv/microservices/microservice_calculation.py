from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ScoreInput(BaseModel):
    difficulty: float
    execution: float
    penalties: float

@app.post("/calculate_score/")
async def calculate_score(score_input: ScoreInput):
    # Cálculo del puntaje total
    total_score = score_input.difficulty + score_input.execution - score_input.penalties
    return {"total_score": total_score}
