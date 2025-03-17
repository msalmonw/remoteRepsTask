"""
Test all required functionalities
"""
from datetime import datetime
from database import SessionLocal
from models import Brand, Campaign
from celery_app import (
    reset_daily_budgets_task,
    reset_monthly_budgets_task,
    check_budgets_task,
    manage_dayparting_task,
    record_campaign_spend
)

def get_brand_status(db, brand_id):
    """Get and print the current status of a brand and its campaigns"""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    campaigns = db.query(Campaign).filter(Campaign.brand_id == brand_id).all()
    
    print(f"\nBrand: {brand.name}")
    print(f"  Daily Budget: ${brand.daily_budget:.2f}, Daily Spend: ${brand.daily_spend:.2f}")
    print(f"  Monthly Budget: ${brand.monthly_budget:.2f}, Monthly Spend: ${brand.monthly_spend:.2f}")
    
    print("  Campaigns:")
    for campaign in campaigns:
        status = "ACTIVE" if campaign.is_active else "INACTIVE"
        if campaign.use_dayparting:
            print(f"    - {campaign.name} ({status}): Dayparting {campaign.start_hour}-{campaign.end_hour}")
        else:
            print(f"    - {campaign.name} ({status})")
    
    return brand, campaigns

def test_record_spend():
    """Test recording spend for campaigns"""
    print("\n=== TESTING CAMPAIGN SPEND RECORDING ===")
    db = SessionLocal()
    
    try:
        # Get FashionCo (brand_id=1) status before recording spend
        print("Status before recording spend:")
        brand, campaigns = get_brand_status(db, 1)
        
        # Record spend for the first campaign
        campaign_id = campaigns[0].id
        amount = 200.0
        print(f"\nRecording ${amount:.2f} spend for campaign ID {campaign_id}...")
        record_campaign_spend(campaign_id, amount)
        
        # Get status after recording spend
        print("\nStatus after recording spend:")
        brand, campaigns = get_brand_status(db, 1)
        
        # Record more spend to approach daily budget
        remaining = brand.daily_budget - brand.daily_spend
        print(f"\nRecording ${remaining - 50:.2f} more spend (approaching daily budget)...")
        record_campaign_spend(campaign_id, remaining - 50)
        
        # Get status after approaching daily budget
        print("\nStatus after approaching daily budget:")
        brand, campaigns = get_brand_status(db, 1)
        
        # Record spend to exceed daily budget
        print(f"\nRecording ${100:.2f} more spend (exceeding daily budget)...")
        record_campaign_spend(campaign_id, 100)
        
        # Get status after exceeding daily budget
        print("\nStatus after exceeding daily budget:")
        brand, campaigns = get_brand_status(db, 1)
        
        print("\nSpend recording test completed.")
    finally:
        db.close()

def test_budget_check():
    """Test the budget checking task"""
    print("\n=== TESTING BUDGET CHECK TASK ===")
    db = SessionLocal()
    
    try:
        # Get TechGadgets (brand_id=2) status before testing
        print("Status before testing budget check:")
        brand, campaigns = get_brand_status(db, 2)
        
        # Update brand spend to exceed daily budget
        print(f"\nManually setting daily spend to exceed budget...")
        brand.daily_spend = brand.daily_budget + 50
        db.commit()
        
        # Run budget check task
        print("\nRunning budget check task...")
        check_budgets_task.delay()
        
        # Get status after budget check
        print("\nStatus after budget check:")
        brand, campaigns = get_brand_status(db, 2)
        
        print("\nBudget check test completed.")
    finally:
        db.close()

def test_daily_budget_reset():
    """Test the daily budget reset task"""
    print("\n=== TESTING DAILY BUDGET RESET TASK ===")
    db = SessionLocal()
    
    try:
        # Get all brands before reset
        print("Status before daily budget reset:")
        for brand_id in [1, 2, 3]:
            get_brand_status(db, brand_id)
        
        # Run daily budget reset task
        print("\nRunning daily budget reset task...")
        reset_daily_budgets_task.delay()
        
        # Get status after daily budget reset
        print("\nStatus after daily budget reset:")
        for brand_id in [1, 2, 3]:
            get_brand_status(db, brand_id)
        
        print("\nDaily budget reset test completed.")
    finally:
        db.close()

def test_monthly_budget_reset():
    """Test the monthly budget reset task"""
    print("\n=== TESTING MONTHLY BUDGET RESET TASK ===")
    db = SessionLocal()
    
    try:
        # Manually set monthly spend for GourmetFood (brand_id=3)
        brand = db.query(Brand).filter(Brand.id == 3).first()
        brand.monthly_spend = brand.monthly_budget + 100
        db.commit()
        
        # Get status before monthly reset
        print("Status before monthly budget reset:")
        get_brand_status(db, 3)
        
        # Run monthly budget reset task
        print("\nRunning monthly budget reset task...")
        reset_monthly_budgets_task.delay()
        
        # Get status after monthly reset
        print("\nStatus after monthly budget reset:")
        get_brand_status(db, 3)
        
        print("\nMonthly budget reset test completed.")
    finally:
        db.close()

def test_dayparting():
    """Test the dayparting management task"""
    print("\n=== TESTING DAYPARTING MANAGEMENT TASK ===")
    db = SessionLocal()
    
    try:
        # Get current time
        current_time = datetime.now().time()
        print(f"Current time: {current_time}")
        
        # Get status before dayparting
        print("\nStatus before dayparting management:")
        for brand_id in [2, 3]:
            get_brand_status(db, brand_id)
        
        # Run dayparting task
        print("\nRunning dayparting management task...")
        manage_dayparting_task.delay()
        
        # Get status after dayparting
        print("\nStatus after dayparting management:")
        for brand_id in [2, 3]:
            get_brand_status(db, brand_id)
        
        print("\nDayparting test completed.")
    finally:
        db.close()

def run_all_tests():
    print("STARTING AD AGENCY TASK TESTS")
    
    test_record_spend()
    test_budget_check()
    test_daily_budget_reset()
    test_monthly_budget_reset()
    test_dayparting()
    
    print("TESTS COMPLETED")

if __name__ == "__main__":
    run_all_tests()