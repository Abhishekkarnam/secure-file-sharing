from database.models import SystemLog, db

def log_event(user_id, action, status):
    new_log = SystemLog(user_id=user_id, action=action, status=status)
    db.session.add(new_log)
    db.session.commit()