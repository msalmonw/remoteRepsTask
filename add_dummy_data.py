from datetime import time
from database import SessionLocal, init_db
from crud import create_brand, create_campaign

def setup_test_data():
    """Create test brands and campaigns in the database"""
    print("Initializing database...")
    init_db()
    db = SessionLocal()
    
    try:
        print("Creating test brands...")
        brand1 = create_brand(db, "FashionCo", daily_budget=500.0, monthly_budget=12000.0)
        brand2 = create_brand(db, "TechGadgets", daily_budget=800.0, monthly_budget=20000.0)
        brand3 = create_brand(db, "GourmetFood", daily_budget=300.0, monthly_budget=8000.0)
        
        print(f"Created brand: {brand1.name}, ID: {brand1.id}")
        print(f"Created brand: {brand2.name}, ID: {brand2.id}")
        print(f"Created brand: {brand3.name}, ID: {brand3.id}")
        
        print("\nCreating regular campaigns for FashionCo...")
        campaign1 = create_campaign(db, "Summer Sale", brand1.id)
        campaign2 = create_campaign(db, "New Arrivals", brand1.id)
        
        print(f"Created campaign: {campaign1.name}, ID: {campaign1.id}")
        print(f"Created campaign: {campaign2.name}, ID: {campaign2.id}")
        
        print("\nCreating dayparting campaigns for TechGadgets...")
        
        campaign3 = create_campaign(
            db, "Business Hours Promo", brand2.id,
            use_dayparting=True, start_hour=time(9, 0), end_hour=time(17, 0)
        )
        
        campaign4 = create_campaign(
            db, "Evening Special", brand2.id,
            use_dayparting=True, start_hour=time(18, 0), end_hour=time(23, 0)
        )
        
        print(f"Created campaign: {campaign3.name}, ID: {campaign3.id}, Hours: 9:00-17:00")
        print(f"Created campaign: {campaign4.name}, ID: {campaign4.id}, Hours: 18:00-23:00")
        
        print("\nCreating overnight campaign for GourmetFood...")
        campaign5 = create_campaign(
            db, "Late Night Snacks", brand3.id,
            use_dayparting=True, start_hour=time(22, 0), end_hour=time(6, 0)
        )
        
        campaign6 = create_campaign(db, "Healthy Breakfast", brand3.id)
        
        print(f"Created campaign: {campaign5.name}, ID: {campaign5.id}, Hours: 22:00-6:00")
        print(f"Created campaign: {campaign6.name}, ID: {campaign6.id}")
        
        print("\nSetup complete. Database populated with test data.")
        
    finally:
        db.close()

if __name__ == "__main__":
    setup_test_data()