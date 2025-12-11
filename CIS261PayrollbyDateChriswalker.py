# Created by Christopher Walker
# CIS 261 - Python Programming
# Employee Payroll System with Date Range and File Storage

from datetime import datetime
import sys
import os

DATA_FILENAME = "employees.txt"

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

def read_date(prompt_text, allow_all=False):
    """Read a date in mm/dd/yyyy. Accept 'End' (handled by check_for_end_and_confirm).
       If allow_all is True, the user may enter 'All' (case-insensitive) which will be returned as 'All'."""
    while True:
        s = input(prompt_text).strip()
        if not s:
            print("Please enter a date or 'All'.")
            continue
        # allow All if requested
        if allow_all and s.strip().lower() == "all":
            return "All"
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

def write_record_to_file(rec, filename=DATA_FILENAME):
    """Append a pipe-delimited record to the data file.
       Format: from_date|to_date|name|hours|rate|tax_rate_percent
       tax_rate_percent is stored as a plain percent (e.g., 15.0 for 15%)."""
    line = f"{rec['from_date']}|{rec['to_date']}|{rec['name']}|{rec['hours']}|{rec['rate']}|{rec['tax_rate']*100}\n"
    # Ensure directory exists if a path is provided (safe default)
    # (If filename includes directories, create them; otherwise this is a no-op)
    dirpath = os.path.dirname(os.path.abspath(filename))
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    with open(filename, "a", newline="") as f:
        f.write(line)

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

def run_report_from_file(filename=DATA_FILENAME):
    """Prompt user for a From Date or 'All', then read the file and display matching records and totals."""
    print("\n--- Generate report from stored records ---")
    # allow 'All' as an option
    try:
        requested_from = read_date("Enter From Date to run report for (mm/dd/yyyy) or type All: ", allow_all=True)
    except QuitRequested:
        print("Quit requested while entering report date. Aborting report.")
        return

    if not os.path.exists(filename):
        print(f"No data file found ({filename}). No records to display.")
        return

    matched_records = []
    totals = {"count": 0, "total_hours": 0.0, "total_gross": 0.0, "total_tax": 0.0, "total_net": 0.0}

    with open(filename, "r", newline="") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) != 6:
                print(f"Skipping malformed line {lineno}: {line}")
                continue
            from_date_str, to_date_str, name, hours_str, rate_str, tax_rate_percent_str = parts
            # If user requested All or the from date matches, process
            if requested_from != "All" and from_date_str != requested_from:
                continue
            # Convert numeric fields
            try:
                hours = float(hours_str)
                rate = float(rate_str)
                tax_rate_percent = float(tax_rate_percent_str)
            except ValueError:
                print(f"Skipping line with invalid numeric data at {lineno}: {line}")
                continue
            tax_rate = tax_rate_percent / 100.0
            gross, tax, net = calculate_pay(hours, rate, tax_rate)
            rec = {
                "from_date": from_date_str,
                "to_date": to_date_str,
                "name": name,
                "hours": hours,
                "rate": rate,
                "tax_rate": tax_rate,
                "gross": gross,
                "tax": tax,
                "net": net
            }
            # Update totals dictionary inside the loop as requested
            totals["count"] += 1
            totals["total_hours"] += hours
            totals["total_gross"] += gross
            totals["total_tax"] += tax
            totals["total_net"] += net

            matched_records.append(rec)

    if matched_records:
        print(f"\nFound {totals['count']} matching record(s).\n")
        for rec in matched_records:
            display_employee_record(rec)
        print("\n" + "=" * 72)
        print("Totals (from dictionary):")
        print(f"Total employees processed: {totals['count']}")
        print(f"Total hours worked      : {totals['total_hours']:.2f}")
        print(f"Total gross pay         : ${totals['total_gross']:.2f}")
        print(f"Total income taxes      : ${totals['total_tax']:.2f}")
        print(f"Total net pay           : ${totals['total_net']:.2f}")
        print("=" * 72)
    else:
        print("No matching records found for the requested date.")

# ---------------------------
# Menu and orchestration code
# ---------------------------

def show_title_menu():
    print("\nEmployee Payroll System")
    print("-----------------------")
    print("1 - Add Employees")
    print("2 - Generate Report (by From Date or All)")
    print("Q - Quit")

def add_employees_menu():
    """Interactive loop to add employees from the menu. Returns to menu on completion or on QuitRequested."""
    session_records = []
    try:
        while True:
            # Use the same prompts as before
            from_date = read_date("From date (mm/dd/yyyy): ")
            to_date = read_date("To date (mm/dd/yyyy): ")

            name = input_name()
            hours = input_hours()
            rate = input_hourly_rate()
            tax_rate = input_tax_rate()

            gross, tax, net = calculate_pay(hours, rate, tax_rate)
            rec = {
                "from_date": from_date,
                "to_date": to_date,
                "name": name,
                "hours": hours,
                "rate": rate,
                "tax_rate": tax_rate,
                "gross": gross,
                "tax": tax,
                "net": net
            }

            # Append to in-memory session list and write to file
            session_records.append(rec)
            write_record_to_file(rec)
            print(f"\nRecord added for {name} and saved to file.")

            cont = input("Add another employee? (y/n): ").strip().lower()
            if cont != "y":
                break
    except QuitRequested:
        # If user confirmed quit during entry, re-raise so caller can handle quitting
        raise
    return session_records

def main():
    print("Payroll Entry by Date Range (type End at any prompt to request quit)\n")
    while True:
        show_title_menu()
        choice = input("\nEnter your choice (1, 2, or Q): ").strip().lower()
        if choice == "1":
            try:
                session_records = add_employees_menu()
                if session_records:
                    print("\nSession summary (records entered during this menu action):")
                    summarize_and_display_totals(session_records)
            except QuitRequested:
                # Confirm quit at top-level
                if prompt_yes_no("\nQuit requested. Do you want to exit the program entirely? (y/n): "):
                    print("Exiting program. Goodbye!")
                    sys.exit(0)
                else:
                    print("Returning to main menu.")
                    continue
        elif choice == "2":
            try:
                run_report_from_file()
            except QuitRequested:
                if prompt_yes_no("\nQuit requested. Do you want to exit the program entirely? (y/n): "):
                    print("Exiting program. Goodbye!")
                    sys.exit(0)
                else:
                    print("Returning to main menu.")
                    continue
        elif choice == "q":
            if prompt_yes_no("Are you sure you want to quit? (y/n): "):
                print("Exiting program. Goodbye!")
                sys.exit(0)
            else:
                continue
        else:
            print("Invalid choice. Please enter 1, 2, or Q.")

if __name__ == "__main__":
    main()
