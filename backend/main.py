from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel

app = FastAPI()

# Abilita CORS per sviluppo locale (React su localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Anomaly(BaseModel):
    date: str
    league: str
    match: str
    anomaly: str
    source: str

# Dummy data per demo
matches = [
    Anomaly(
        date="2025-09-10",
        league="2nd Div. Bulgaria",
        match="FC Minori - Real X",
        anomaly="6 titolari assenti, crisi stipendi",
        source="https://esempio.com/news1"
    ),
    Anomaly(
        date="2025-09-11",
        league="Serie C Brasile",
        match="ABC - DEF",
        anomaly="Allenatore esonerato, squadra in sciopero",
        source="https://esempio.com/news2"
    ),
]

@app.get("/anomalies", response_model=List[Anomaly])
def get_anomalies(date: str = None):
    if date:
        return [m for m in matches if m.date == date]
    return matches
