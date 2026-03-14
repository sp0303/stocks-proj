from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base


class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    stock = Column(String)
    model = Column(String)

    signal = Column(String)

    predicted_price = Column(Float)
    confidence = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)