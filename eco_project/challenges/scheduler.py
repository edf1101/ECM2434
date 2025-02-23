"""
This sets up the scheduler for the challenges
"""
from apscheduler.schedulers.background import BackgroundScheduler

# Global scheduler instance
scheduler = BackgroundScheduler()
