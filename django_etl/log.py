import datetime


def log_migration(model_name, count):
    now = datetime.datetime.now().isoformat()
    print(f"[{now}] Migrated {count} rows for {model_name}")
