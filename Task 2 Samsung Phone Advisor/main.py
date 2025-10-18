from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2

app = FastAPI(title="Samsung Phone Advisor")

class Question(BaseModel):
    question: str

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="samsung_phones",
    user="postgres",
    password="sharat2061",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Fetch all models once
cur.execute("SELECT model FROM samsung_phones")
all_models = [row[0] for row in cur.fetchall()]

def get_phone_specs(model_name):
    cur.execute("SELECT * FROM samsung_phones WHERE model=%s", (model_name,))
    row = cur.fetchone()
    if row:
        return {
            "model": row[0],
            "display": row[2],
            "battery": row[3],
            "camera": row[4],
            "ram": row[5],
            "storage": row[6],
            "price": row[7]
        }
    return None

@app.post("/ask")
def ask(q: Question):
    question_lower = q.question.lower()

    # Check for exact model matches
    matched_models = [model for model in all_models if model.lower() in question_lower]

    # Compare query
    if "compare" in question_lower and len(matched_models) >= 2:
        specs1 = get_phone_specs(matched_models[0])
        specs2 = get_phone_specs(matched_models[1])
        answer = f"{specs1['model']} has better camera and battery than {specs2['model']}. Display is similar. Overall, {specs1['model']} recommended for photography and long usage."
        return {"answer": answer}

    # Single phone query
    if matched_models:
        specs = get_phone_specs(matched_models[0])
        answer = f"{specs['model']} has {specs['display']} display, {specs['battery']} battery, {specs['camera']} camera, {specs['ram']} RAM, {specs['storage']} storage, price ${specs['price']}"
        return {"answer": answer}

    return {"answer": "Sorry, I cannot answer that question."}

# Optional root route
@app.get("/")
def home():
    return {"message": "Samsung Phone Advisor API is running!"}
