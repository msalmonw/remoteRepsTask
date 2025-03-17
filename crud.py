from sqlalchemy.orm import Session
from models import Brand, Campaign
from datetime import time

'''
crud functions for brands and campaigns

including some extra utils in addition to the methods speciifically mentioned in the requirements

'''
def get_all_brands(db: Session):
    return db.query(Brand).all()

def get_brand_by_id(db: Session, brand_id: int):
    return db.query(Brand).filter(Brand.id == brand_id).first()

def get_campaigns_by_brand_id(db: Session, brand_id: int):
    return db.query(Campaign).filter(Campaign.brand_id == brand_id).all()

def get_active_campaigns(db: Session):
    return db.query(Campaign).filter(Campaign.is_active == True).all()

def create_brand(db: Session, name: str, daily_budget: float, monthly_budget: float):
    brand = Brand(name=name, daily_budget=daily_budget, monthly_budget=monthly_budget)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

def create_campaign(db: Session, name: str, brand_id: int, use_dayparting: bool = False, 
                   start_hour: time = None, end_hour: time = None):
    campaign = Campaign(
        name=name, 
        brand_id=brand_id,
        use_dayparting=use_dayparting,
        start_hour=start_hour,
        end_hour=end_hour
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign

def update_campaign_status(db: Session, campaign_id: int, is_active: bool):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign:
        campaign.is_active = is_active
        db.commit()
        return campaign
    
    return None

def reset_daily_budgets(db: Session):
    brands = db.query(Brand).all()
    for brand in brands:
        brand.daily_spend = 0.0
    
    db.commit()
    return brands

def reset_monthly_budgets(db: Session):
    brands = db.query(Brand).all()
    for brand in brands:
        brand.monthly_spend = 0.0
        brand.daily_spend = 0.0
    
    db.commit()
    return brands

def update_brand_spend(db: Session, brand_id: int, amount: float):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if brand:
        brand.daily_spend += amount
        brand.monthly_spend += amount
        db.commit()
        db.refresh(brand)
        
        # Check if budgets are exceeded and deactivate campaigns if needed
        daily_budget_exceeded = brand.daily_spend >= brand.daily_budget
        monthly_budget_exceeded = brand.monthly_spend >= brand.monthly_budget
        
        if daily_budget_exceeded or monthly_budget_exceeded:
            campaigns = brand.campaigns
            for campaign in campaigns:
                update_campaign_status(db, campaign.id, False)
                
    return brand