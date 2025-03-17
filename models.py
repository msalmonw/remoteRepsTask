from sqlalchemy import Column, Integer, String, Float, Boolean, Time, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

#the brand and the campaign model, where we have one-to-many relationship between a brand and its campaigns
class Brand(Base):
    __tablename__ = 'brands'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    daily_budget = Column(Float, nullable=False)
    monthly_budget = Column(Float, nullable=False)
    daily_spend = Column(Float, default=0.0)
    monthly_spend = Column(Float, default=0.0)
    
    campaigns = relationship("Campaign", back_populates="brand")


class Campaign(Base):
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    use_dayparting = Column(Boolean, default=False)
    start_hour = Column(Time, nullable=True)
    end_hour = Column(Time, nullable=True)
    
    brand = relationship("Brand", back_populates="campaigns")