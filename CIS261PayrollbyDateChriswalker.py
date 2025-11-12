# payroll_by_dates_fixed.py
# Python 3 — run in a terminal (VS Code / Visual Studio integrated terminal)

from datetime import datetime
import sys

class QuitRequested(Exception):
    """Internal signal used when the user confirms they want to quit."""
    pass

def prompt_yes_no(prompt):
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")

def check_for_end_and_confirm(s):
    """If s equals 'End' (case-insensitive), ask for confirmation and raise QuitRequested if confirmed."""
    if isinstance(s, str) and s.strip().lower() == "end":
        if prompt_yes_no("You entered 'End'. Do you want to quit? (y/n): "):
            raise QuitRequested()
        return True  # user entered End but cancelled quit
    return False  # not End

def read_date(prompt_text):
    """Read a date in mm/dd/yyyy. Accept 'End' (handled by check_for_end_and_confirm)."""
    while True:
        s = input(prompt_text).strip()
        if not s:
            print("Please enter a date.")
            continue
        # check End first
        cancelled_end = False
        try:
            if check_for_end_and_confirm(s):
                cancelled_end = True
        except QuitRequested:
            raise
        if cancelled_end:
            # user typed End then chose to continue; loop back to prompt again
            continue
        # validate date format
        try:
            dt = datetime.strptime(s, "%m/%d/%Y")
            return s  # keep the original string format for display
        except ValueError:
            print("Invalid date. Use mm/dd/yyyy (for example 04/20/2025).")

def input_name():
    while True:
        s = input("Employee name (or type End to finish): ").strip()
        if not s:
            print("Name cannot be blank.")
            continue
        try:
            if check_for_end_and_confirm(s):
                # user typed End then cancelled quit; re-prompt
                continue
        except QuitRequested:
            raise
        return s

def input_hours():
    while True:
        s = input("Total hours worked: ").strip()
        if not s:
            print("Please enter hours.")
            continue
        try:
            if check_for_end_and_confirm(s):
                continue
        except QuitRequested:
            raise
        try:
            hours = float(s)
            if hours < 0:
                print("Hours must be non-negative.")
                continue
            return hours
        except ValueError:
            print("Enter a valid number for hours.")

def input_hourly_rate():
    while True:
        s = input("Hourly rate: ").strip()
        if not s:
            print("Please enter hourly rate.")
            continue
        try:
            if check_for_end_and_confirm(s):
                continue
        except QuitRequested:
            raise
        try:
            rate = float(s)
            if rate < 0:
                print("Hourly rate must be non-negative.")
                continue
            return rate
        except ValueError:
            print("Enter a valid number for hourly rate.")

def input_tax_rate():
    while True:
        s = input("Income tax rate (percent, e.g. 15 for 15%): ").strip()
        if not s:
            print("Please enter a tax rate.")
            continue
        try:
            if check_for_end_and_confirm(s):
                continue
        except QuitRequested:
            raise
        try:
            pct = float(s)
            if not (0 <= pct <= 100):
                print("Tax rate must be between 0 and 100.")
                continue
            return pct / 100.0
        except ValueError:
            print("Enter a valid percentage for tax rate.")

def calculate_pay(hours, rate, tax_rate):
    gross = hours * rate
    tax = gross * tax_rate
    net = gross - tax
    return gross, tax, net

def display_employee_record(rec):
    print("-" * 72)
    print(f"From: {rec['from_date']}  To: {rec['to_date']}")
    print(f"Name: {rec['name']}")
    print(f"Hours: {rec['hours']:.2f}  Rate: ${rec['rate']:.2f}  Gross: ${rec['gross']:.2f}")
    print(f"Tax Rate: {rec['tax_rate']*100:.2f}%  Income Tax: ${rec['tax']:.2f}  Net Pay: ${rec['net']:.2f}")
    print("-" * 72)

def summarize_and_display_totals(records):
    totals = {"count": 0, "total_hours": 0.0, "total_gross": 0.0, "total_tax": 0.0, "total_net": 0.0}
    print("\nPayroll Results:\n")
    for rec in records:
        display_employee_record(rec)
        totals["count"] += 1
        totals["total_hours"] += rec["hours"]
        totals["total_gross"] += rec["gross"]
        totals["total_tax"] += rec["tax"]
        totals["total_net"] += rec["net"]

    print("\n" + "=" * 72)
    print("Totals:")
    print(f"Total employees processed: {totals['count']}")
    print(f"Total hours worked      : {totals['total_hours']:.2f}")
    print(f"Total gross pay         : ${totals['total_gross']:.2f}")
    print(f"Total income taxes      : ${totals['total_tax']:.2f}")
    print(f"Total net pay           : ${totals['total_net']:.2f}")
    print("=" * 72)
    return totals

def main():
    print("Payroll Entry by Date Range (type End at any prompt to request quit)\n")
    records = []
    try:
        while True:
            # Part 1: dates called first
            from_date = read_date("From date (mm/dd/yyyy): ")
            to_date = read_date("To date (mm/dd/yyyy): ")

            name = input_name()
            hours = input_hours()
            rate = input_hourly_rate()
            tax_rate = input_tax_rate()

            gross, tax, net = calculate_pay(hours, rate, tax_rate)
            records.append({
                "from_date": from_date,
                "to_date": to_date,
                "name": name,
                "hours": hours,
                "rate": rate,
                "tax_rate": tax_rate,
                "gross": gross,
                "tax": tax,
                "net": net
            })

            print(f"\nRecord added for {name}. Enter next employee or type End to quit.\n")

    except QuitRequested:
        print("\nQuit confirmed by user. Proceeding to totals.")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Proceeding to totals.")
    finally:
        if records:
            summarize_and_display_totals(records)
        else:
            print("No employee data entered. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    main()
