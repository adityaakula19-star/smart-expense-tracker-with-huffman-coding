import csv
import os
from datetime import datetime

from database import dashboard_summary, list_transactions


REPORT_DIR = "reports"


def ensure_report_dir():
    os.makedirs(REPORT_DIR, exist_ok=True)


def generate_csv_report(user_id: int, username: str) -> str:
    ensure_report_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORT_DIR, f"{username}_expense_report_{timestamp}.csv")
    rows = list_transactions(user_id)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Type", "Category", "Amount", "Date", "Description"])
        writer.writerows(rows)

    return path


def generate_txt_report(user_id: int, username: str) -> str:
    ensure_report_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORT_DIR, f"{username}_expense_summary_{timestamp}.txt")
    summary = dashboard_summary(user_id)
    rows = list_transactions(user_id)

    with open(path, "w", encoding="utf-8") as file:
        file.write(f"Smart Expense Tracker Report\n")
        file.write(f"User: {username}\n")
        file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        file.write("Summary\n")
        file.write(f"Total Income: Rs. {summary['total_income']:.2f}\n")
        file.write(f"Total Expenses: Rs. {summary['total_expense']:.2f}\n")
        file.write(f"Current Balance: Rs. {summary['balance']:.2f}\n")
        file.write(f"This Month Spending: Rs. {summary['monthly_spending']:.2f}\n\n")
        file.write("Category-wise Expenses\n")
        for category, amount in summary["categories"]:
            file.write(f"{category} - Rs. {amount:.2f}\n")

        file.write("\nTransactions\n")
        for row in rows:
            transaction_id, transaction_type, category, amount, entry_date, description = row
            file.write(
                f"{transaction_id}. {entry_date} | {transaction_type} | {category} | "
                f"Rs. {amount:.2f} | {description}\n"
            )

    return path
