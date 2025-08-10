import os
import re
from collections import Counter
from datetime import datetime

def get_ftp_directory():
    """Prompts the user for a directory path."""
    while True:
        ftp_directory = input("Enter the path to the FTP directory: ")
        if os.path.isdir(ftp_directory):
            break
        else:
            print("Invalid path. Please enter a valid directory path.")
    return ftp_directory

def get_darwin_stats(root_dir):
    """Gathers statistics about DARWINs from the given directory."""
    all_darwins = set()
    active_darwins = set()
    current_month_str = datetime.now().strftime('%Y-%m')
    darwin_pattern = re.compile(r'^[A-Z]{3,4}$')

    print(f"Scanning {root_dir} for DARWINs...")
    for darwin_name in os.listdir(root_dir):
        if darwin_pattern.match(darwin_name):
            darwin_path = os.path.join(root_dir, darwin_name)
            if os.path.isdir(darwin_path):
                all_darwins.add(darwin_name)
                
                # Check for activity in the current month
                month_path = os.path.join(darwin_path, "quotes", current_month_str)
                if os.path.isdir(month_path) and os.listdir(month_path):
                    active_darwins.add(darwin_name)

    return all_darwins, active_darwins

def potential_darwins_per_letter():
    """Calculates the potential number of DARWINs per starting letter."""
    potential = {}
    for i in range(26):
        letter = chr(ord('A') + i)
        # Combinations for 3-letter and 4-letter names
        potential[letter] = (26**2) + (26**3)
    return potential

def main():
    """Main function to run the script."""
    ftp_directory = get_ftp_directory()
    all_darwins, active_darwins = get_darwin_stats(ftp_directory)

    if not all_darwins:
        print("No DARWINs found.")
        return

    # Categorize by length
    all_darwins_3 = {d for d in all_darwins if len(d) == 3}
    all_darwins_4 = {d for d in all_darwins if len(d) == 4}
    active_darwins_3 = {d for d in active_darwins if len(d) == 3}
    active_darwins_4 = {d for d in active_darwins if len(d) == 4}

    # Letter-based statistics
    letter_counts = Counter(d[0] for d in all_darwins)
    active_letter_counts = Counter(d[0] for d in active_darwins)
    potential = potential_darwins_per_letter()

    # Totals
    total_known = len(all_darwins)
    total_active = len(active_darwins)
    total_potential = sum(potential.values())
    total_vacancy = total_potential - total_known
    active_percentage = (total_active / total_known * 100) if total_known > 0 else 0
    vacancy_percentage = (total_vacancy / total_potential * 100) if total_potential > 0 else 0

    # --- Output Files ---
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    with open(f'Active_Darwins_{current_date_str}.txt', 'w') as f:
        f.write("Active 3-letter DARWINs:\n")
        for d in sorted(active_darwins_3):
            f.write(f"{d}\n")
        f.write("\nActive 4-letter DARWINs:\n")
        for d in sorted(active_darwins_4):
            f.write(f"{d}\n")

    with open(f'Known_Darwins_{current_date_str}.txt', 'w') as f:
        f.write("Known 3-letter DARWINs:\n")
        for d in sorted(all_darwins_3):
            f.write(f"{d}\n")
        f.write("\nKnown 4-letter DARWINs:\n")
        for d in sorted(all_darwins_4):
            f.write(f"{d}\n")

    with open(f'Darwin_Stats_{current_date_str}.txt', 'w') as f:
        f.write("DARWIN Statistics:\n")
        for i in range(26):
            char = chr(ord('A') + i)
            known = letter_counts.get(char, 0)
            active = active_letter_counts.get(char, 0)
            pot = potential.get(char, 0)
            occupancy_rate = (active / known * 100) if known > 0 else 0
            vacancy_rate = ((pot - known) / pot * 100) if pot > 0 else 0
            f.write(f"{char}: Known ({known}), Active ({active}, {occupancy_rate:.2f}%), Vacancy ({vacancy_rate:.2f}%)\n")
        
        f.write(f"\nTotal Known DARWINs: {total_known}\n")
        f.write(f"Total Active DARWINs: {total_active}\n")
        f.write(f"Active Percentage: {active_percentage:.2f}%")
        f.write(f"Total Potential DARWINs: {total_potential}\n")
        f.write(f"Total Vacancy: {total_vacancy} ({vacancy_percentage:.2f}%)\n")

    print("Processing complete. Statistics files have been generated.")

if __name__ == "__main__":
    main()
