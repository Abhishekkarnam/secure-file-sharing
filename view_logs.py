from app import create_app
from database.models import SystemLog


def main():
    app = create_app()

    with app.app_context():
        logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).all()

        if not logs:
            print("No logs found.")
            return

        print(f"{'ID':<5} {'USER':<20} {'STATUS':<12} {'TIMESTAMP':<25} ACTION")
        print("-" * 90)

        for log in logs:
            timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "-"
            print(
                f"{log.id:<5} "
                f"{str(log.user_id or '-'):<20} "
                f"{str(log.status or '-'):<12} "
                f"{timestamp:<25} "
                f"{log.action or '-'}"
            )


if __name__ == "__main__":
    main()
