from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime

app = FastAPI()
Base = declarative_base()

DATABASE_URL = "sqlite:///./budget.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    total_budget = Column(Float, default=0)
    remaining_budget = Column(Float, default=0)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer)
    description = Column(String)
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

class InputData(BaseModel):
    message: str

@app.post("/process-input")
def process_input(data: InputData):
    parts = data.message.split()
    if len(parts) < 3:
        return {"error": "Invalid input format"}
    
    category_id, description, amount = parts[0], parts[1], parts[2]
    amount = float(amount.replace("$", ""))
    
    category = db.query(Category).filter(Category.id == int(category_id)).first()
    if not category:
        return {"error": "Category not found"}
    
    if category.remaining_budget < amount:
        return {"error": "Insufficient budget"}
    
    category.remaining_budget -= amount
    db.add(Transaction(category_id=int(category_id), description=description, amount=amount))
    db.commit()
    return {"remaining_budget": category.remaining_budget}
