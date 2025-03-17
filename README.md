# remoteRepsTask
 
## How to Run

1. Install requirements: `pip install -r requirments.txt`
2. Install and Run Redis: https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/
   Note: If you are on Windows then install Redis on WSL. You will be able to connect to redis from the host machine as well if you prefer not to develop on WSL.
4. Initialize database and add dummy data: `python add_dummy_data.py`
5. Start celery worker: `celery -A celery_app worker --loglevel=info`
6. Test by manually triggering celery tasks: `pythhon test_usage.py`
7. Test by automating the tasks: `celery -A celery_app beat --loglevel=info`


## Flow of the Program

### Campaign Spend Updates
  When an ad campaign spends money, it updates the brand’s total daily and monthly spend.
  If a brand exceeds its budget, all its campaigns are paused.

### Budget Reset Tasks
  Daily budgets reset at midnight (reset_daily_budgets_task).
  Monthly budgets reset on the 1st of the month (reset_monthly_budgets_task).
  Campaigns are re-enabled if they are within the budget.

### Automatic Budget Checking
  Runs every 5 minutes (check_budgets_task).
  If a brand’s budget is exceeded, all its campaigns are paused.

### Dayparting (Time-Based Campaign Control)
  Runs every 15 minutes (manage_dayparting_task).
  If a campaign has a scheduled active time, it only runs within that window.


## Assumptions and Simplifications Made

1. Using sqlite instead of a proper database for simplicity
2. Simplified database models. We can add more models for complete loggings for spendings etc. for each specific campaign

   



