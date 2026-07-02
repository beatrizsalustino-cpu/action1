import os
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from app.collector import collect

load_dotenv()

interval_seconds = int(os.getenv("UPDATE_INTERVAL", "600"))

scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", seconds=interval_seconds)
def scheduled_collect():
    print("Iniciando coleta agendada...")
    collect()


if __name__ == "__main__":
    print(f"Scheduler iniciado. Coleta a cada {interval_seconds} segundos.")
    collect()
    scheduler.start()