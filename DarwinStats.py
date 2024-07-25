import os
import re
from collections import Counter
from datetime import datetime, timedelta

def get_letter_range():
    while True:
        start_letter = input("Enter the starting letter of the range (A-Z): ").upper()
        end_letter = input("Enter the ending letter of the range (A-Z): ").upper()
        if start_letter.isalpha() and end_letter.isalpha() and start_letter <= end_letter:
            break
        else:
            print("Invalid input. Please enter valid letters in alphabetical order.")
    return start_letter, end_letter

def get_ftp_directory():
    while True:
        ftp_directory = input("Enter the path to the FTP directory: ")
        if os.path.isdir(ftp_directory):
            break
        else:
            print("Invalid path. Please enter a valid directory path.")
    return ftp_directory

def find_target_directories(ftp_directory, start_letter, end_letter):
    current_month = datetime.now().strftime("%Y-%m")
    target_dirs = []

    print(f"Scanning for target directories in {ftp_directory}...")  # Debug print

    for entry in os.listdir(ftp_directory):
        entry_path = os.path.join(ftp_directory, entry)
        print(f"Checking {entry_path}...")  # Debug print

        # Check for 3-letter DARWIN directories within the specified range
        if os.path.isdir(entry_path) and len(entry) == 3 and re.match(r'^[A-Z]{3}$', entry):
            if start_letter <= entry[0] <= end_letter:
                quotes_dir = os.path.join(entry_path, "quotes")
                print(f"Looking for quotes in {quotes_dir}...")  # Debug print
                if os.path.isdir(quotes_dir):
                    month_dir = os.path.join(quotes_dir, current_month)
                    print(f"Checking month directory: {month_dir}...")  # Debug print
                    if os.path.isdir(month_dir):
                        target_dirs.append(month_dir)

                # Check for 4-letter DARWIN directories under the base 3-letter directory
                former_dir = os.path.join(entry_path, f"_{entry}_former_var10")
                print(f"Checking former directory: {former_dir}...")  # Debug print
                if os.path.isdir(former_dir):
                    quotes_dir = os.path.join(former_dir, "quotes")
                    if os.path.isdir(quotes_dir):
                        month_dir = os.path.join(quotes_dir, current_month)
                        print(f"Checking month directory: {month_dir}...")  # Debug print
                        if os.path.isdir(month_dir):
                            target_dirs.append(month_dir)

    return target_dirs

def list_darwins_in_quotes_dir(quotes_dir):
    darwins_3 = set()
    darwins_4 = set()

    print(f"Listing DARWINs in {quotes_dir}...")  # Debug print
    for file in os.listdir(quotes_dir):
        if file.endswith('.csv.gz'):
            match = re.match(r'^([A-Z]{3,4})\.\d+\.\d+_\d+_\d{4}-\d{2}-\d{2}\.\d+\.csv\.gz$', file)
            if match:
                darwin = match.group(1)
                if len(darwin) == 3:
                    darwins_3.add(darwin)
                elif len(darwin) == 4:
                    darwins_4.add(darwin)
    
    return darwins_3, darwins_4

def is_active_darwin(quotes_dir, darwin):
    for file in os.listdir(quotes_dir):
        if file.endswith('.csv.gz') and darwin in file:
            file_date_str = re.search(r'\d{4}-\d{2}-\d{2}', file)
            if file_date_str:
                file_date = datetime.strptime(file_date_str.group(), "%Y-%m-%d")
                one_month_ago = datetime.now() - timedelta(days=30)
                if file_date >= one_month_ago:
                    return True
    return False

def get_filtered_directories(ftp_directory, start_letter, end_letter):
    all_entries = os.listdir(ftp_directory)
    ticker_pattern = re.compile(r'^[A-Z]{3,4}$')
    
    filtered_directories = [
        entry for entry in all_entries
        if os.path.isdir(os.path.join(ftp_directory, entry)) and
        ticker_pattern.match(entry) and
        start_letter <= entry[0] <= end_letter
    ]
    return filtered_directories

def potential_darwins_per_letter(start_letter, end_letter):
    total_potential = {}
    for letter in range(ord(start_letter), ord(end_letter) + 1):
        char = chr(letter)
        num_3_char = 26 * 26
        num_4_char = 26 * 26 * 26
        total_potential[char] = num_3_char + num_4_char
    return total_potential

def calculate_total_potential_darwins(start_letter, end_letter):
    potential_darwins = potential_darwins_per_letter(start_letter, end_letter)
    return sum(potential_darwins.values())

def calculate_occupancy_and_vacancy(letter_counts, active_darwins_per_letter, potential_darwins):
    occupancy = {}
    vacancy = {}
    for letter, count in letter_counts.items():
        active_count = active_darwins_per_letter.get(letter, 0)
        occupancy_rate = (active_count / count * 100) if count > 0 else 0
        potential = potential_darwins.get(letter, 0)
        vacancy_rate = ((potential - count) / potential * 100) if potential > 0 else 0
        occupancy[letter] = {
            'generated': count,
            'active': active_count,
            'occupancy_rate': occupancy_rate
        }
        vacancy[letter] = vacancy_rate
    return occupancy, vacancy

def main():
    ftp_directory = get_ftp_directory()
    start_letter, end_letter = get_letter_range()

    filtered_directories = get_filtered_directories(ftp_directory, start_letter, end_letter)

    target_directories = find_target_directories(ftp_directory, start_letter, end_letter)
    if not target_directories:
        print("No target directories found for the current month.")
        return

    letter_counts = Counter([directory[0] for directory in filtered_directories])
    active_darwins_per_letter = Counter()
    active_darwins = []

    for target_dir in target_directories:
        darwins_3, darwins_4 = list_darwins_in_quotes_dir(target_dir)
        for darwin in darwins_3:
            if darwin in filtered_directories and is_active_darwin(target_dir, darwin):
                active_darwins.append(darwin)
                active_darwins_per_letter[darwin[0]] += 1
        for darwin in darwins_4:
            if darwin in filtered_directories and is_active_darwin(target_dir, darwin):
                active_darwins.append(darwin)
                active_darwins_per_letter[darwin[0]] += 1

    potential_darwins = potential_darwins_per_letter(start_letter, end_letter)
    total_potential_darwins = calculate_total_potential_darwins(start_letter, end_letter)

    total_darwins = sum(letter_counts.values())
    total_active_darwins = len(active_darwins)
    active_percentage = (total_active_darwins / total_darwins * 100) if total_darwins > 0 else 0

    occupancy_rates, vacancy_rates = calculate_occupancy_and_vacancy(letter_counts, active_darwins_per_letter, potential_darwins)

    print("Number of Darwins starting with each letter in the specified range:")
    for letter in range(ord(start_letter), ord(end_letter) + 1):
        char = chr(letter)
        count = letter_counts.get(char, 0)
        active_count = active_darwins_per_letter.get(char, 0)
        occupancy_rate = occupancy_rates.get(char, {}).get('occupancy_rate', 0)
        vacancy_rate = vacancy_rates.get(char, 0)
        print(f"{char}: Generated ({count}), Active ({active_count} ({occupancy_rate:.2f}%)), Vacancy Rate ({vacancy_rate:.2f}%)")

    print(f"\nTotal number of Darwins in the range: {total_darwins}")
    print(f"Total number of active Darwins: {total_active_darwins}")
    print(f"Percentage of active Darwins: {active_percentage:.2f}%")
    print(f"Total number of potential Darwins in the range: {total_potential_darwins}")

    print("\nActive Darwins (with updated quotes within the last month):")
    with open('active_darwins.txt', 'w') as f:
        f.write(", ".join(active_darwins))

    print("The list of active Darwins has been written to 'active_darwins.txt'.")

if __name__ == "__main__":
    main()
