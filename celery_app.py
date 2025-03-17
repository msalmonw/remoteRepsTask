from celery import Celery
from celery.schedules import crontab
import datetime
from database import SessionLocal
from models import Brand, Campaign
from crud import reset_daily_budgets, reset_monthly_budgets, update_campaign_status, update_brand_spend

app = Celery('ad_agency', broker='redis://localhost:6379/0')

app.conf.beat_schedule = {
    'reset-daily-budgets': {
        'task': 'celery_app.reset_daily_budgets_task',
        'schedule': crontab(hour=0, minute=0),  # run at midnight
    },
    'reset-monthly-budgets': {
        'task': 'celery_app.reset_monthly_budgets_task',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),  # run at midnight on the 1st of each month
    },
    'check-budgets': {
        'task': 'celery_app.check_budgets_task',
        'schedule': crontab(minute='*/5'),  # run every 5 minutes, spends can exceed the budget at any time that's why using a frequent check
    },
    'manage-dayparting': {
        'task': 'celery_app.manage_dayparting_task',
        'schedule': crontab(minute='*/15'),  # run every 15 minutes
    },
}

@app.task
def reset_daily_budgets_task():
    """reset daily budgets for all brands"""
    db = SessionLocal()
    try:
        # reset all daily budgets
        brands = reset_daily_budgets(db)
        
        # reactivate campaigns if they were turned off due to daily budget
        # check if monthly budget is not exceeded
        for brand in brands:
            if brand.monthly_spend < brand.monthly_budget:  
                campaigns = brand.campaigns
                for campaign in campaigns:
                    update_campaign_status(db, campaign.id, True)
                    
        return "Daily budgets reset successfully"
    finally:
        db.close()

@app.task
def reset_monthly_budgets_task():
    """reset monthly budgets for all brands"""
    db = SessionLocal()
    try:
        # reset all monthly budgets
        brands = reset_monthly_budgets(db)
        
        # reactivate all campaigns
        for brand in brands:
            campaigns = brand.campaigns
            for campaign in campaigns:
                update_campaign_status(db, campaign.id, True)
                
        return "Monthly budgets reset successfully"
    finally:
        db.close()

@app.task
def check_budgets_task():
    """check budgets for all brands, turn off all campaigns for the brand"""
    db = SessionLocal()
    try:
        brands = db.query(Brand).all()
        for brand in brands:
            daily_budget_exceeded = brand.daily_spend >= brand.daily_budget
            monthly_budget_exceeded = brand.monthly_spend >= brand.monthly_budget
            
            if daily_budget_exceeded or monthly_budget_exceeded:
                # turn off all campaigns for this brand
                campaigns = brand.campaigns
                for campaign in campaigns:
                    update_campaign_status(db, campaign.id, False)
                    
        return "Budget check completed"
    finally:
        db.close()

@app.task
def manage_dayparting_task():
    """check dayparting and activate/deactivate campaigns accordingly"""
    db = SessionLocal()
    try:
        now = datetime.datetime.now().time()
        
        # get only campaigns that use dayparting
        dayparting_campaigns = db.query(Campaign).filter(Campaign.use_dayparting == True).all()
        
        for campaign in dayparting_campaigns:
            # if spends have exceeded the budgets then skip that brand
            brand = campaign.brand
            if brand.daily_spend >= brand.daily_budget or brand.monthly_spend >= brand.monthly_budget:
                continue
                
            # check if current time is within the campaign's active hours
            is_within_hours = False
            if campaign.start_hour <= campaign.end_hour:
                is_within_hours = campaign.start_hour <= now <= campaign.end_hour
            else:
                is_within_hours = now >= campaign.start_hour or now <= campaign.end_hour
                
            update_campaign_status(db, campaign.id, is_within_hours)
                
        return "Dayparting managed successfully"
    finally:
        db.close()

@app.task
def record_campaign_spend(campaign_id: int, amount: float):
    """record spend for a specific campaign and update brand totals"""
    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign and campaign.is_active:
            update_brand_spend(db, campaign.brand_id, amount)
            return f"Recorded {amount} spend for campaign {campaign_id}"
        return f"Campaign {campaign_id} not found or not active"
    finally:
        db.close()