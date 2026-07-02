import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "capacity.db")

def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS endpoint_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        collected_at TEXT,
        hostname TEXT,
        hostname_key TEXT,
        colaborador TEXT,
        departamento_time TEXT,
        cargo TEXT,
        id_experweb TEXT,
        status TEXT,
        last_seen TEXT,
        operating_system TEXT,
        cpu_name TEXT,
        cpu_size TEXT,
        ram TEXT,
        disk TEXT,
        system_model TEXT,
        system_manufacturer TEXT,
        action1_user TEXT,
        reboot_required TEXT,
        free_physical_memory_gb REAL,
        number_of_processes INTEGER,
        health_score INTEGER,
        health_status TEXT
        health_score INTEGER,
        health_reasons TEXT        
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alert_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        hostname TEXT,
        hostname_key TEXT,
        colaborador TEXT,
        departamento_time TEXT,
        alert_type TEXT,
        severity TEXT,
        message TEXT,
        health_score INTEGER,
        notification_sent INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()