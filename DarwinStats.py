import os
import re
from collections import Counter
from datetime import datetime, timedelta

def get_ftp_directory():
    while True:
        ftp_directory = input("Enter the path to the FTP directory: ")
        if os.path.isdir(ftp_directory):
            break
        else:
            print("Invalid path. Please enter a valid directory path.")
    return ftp_directory

def find_target_directories(ftp_directory):
    target_dirs = []
    month_pattern = re.compile(r'\d{4}-\d{2}')

    print(f"Scanning for target directories in {ftp_directory}...")

    for entry in os.listdir(ftp_directory):
        entry_path = os.path.join(ftp_directory, entry)

        # Check for 3-letter DARWIN directories
        if os.path.isdir(entry_path) and len(entry) == 3 and re.match(r'^[A-Z]{3}$', entry):
            quotes_dir = os.path.join(entry_path, "quotes")
            if os.path.isdir(quotes_dir):
                for month_dir in os.listdir(quotes_dir):
                    if month_pattern.match(month_dir):
                        target_dirs.append((os.path.join(quotes_dir, month_dir), entry))

        # Check for 4-letter DARWIN directories under the base 3-letter directory
        former_dir = os.path.join(entry_path, f"_{entry}_former_var10")
        if os.path.isdir(former_dir):
            quotes_dir = os.path.join(former_dir, "quotes")
            if os.path.isdir(quotes_dir):
                for month_dir in os.listdir(quotes_dir):
                    if month_pattern.match(month_dir):
                        target_dirs.append((os.path.join(quotes_dir, month_dir), entry))

    return target_dirs

def list_darwins_in_quotes_dir(quotes_dir, parent_darwin):
    darwins_3 = set()
    darwins_4 = set()

    for file in os.listdir(quotes_dir):
        if file.endswith('.csv.gz'):
            match = re.match(r'^([A-Z]{3,4})\.\d+\.\d+_\d+_\d{4}-\d{2}-\d{2}\.\d+\.csv\.gz$', file)
            if match:
                darwin = match.group(1)
                if len(darwin) == 3:
                    darwins_3.add(darwin)
                elif len(darwin) == 4:
                    darwins_4.add((darwin, parent_darwin))

    return darwins_3, darwins_4

def is_active_darwin(quotes_dir, darwin):
    active = False
    for file in os.listdir(quotes_dir):
        if file.endswith('.csv.gz') and darwin in file:
            file_date_str = re.search(r'\d{4}-\d{2}-\d{2}', file)
            if file_date_str:
                file_date = datetime.strptime(file_date_str.group(), "%Y-%m-%d")
                one_month_ago = datetime.now() - timedelta(days=30)
                if file_date >= one_month_ago:
                    active = True
                    break
    return active

def calculate_occupancy_and_vacancy(letter_counts, active_darwins_per_letter, potential_darwins):
    occupancy = {}
    vacancy = {}
    for letter, count in letter_counts.items():
        active_count = active_darwins_per_letter.get(letter, 0)
        occupancy_rate = (active_count / count * 100) if count > 0 else 0
        potential = potential_darwins.get(letter, 0)
        vacancy_rate = ((potential - count) / potential * 100) if potential > 0 else 0
        occupancy[letter] = {
            'known': count,
            'active': active_count,
            'occupancy_rate': occupancy_rate
        }
        vacancy[letter] = vacancy_rate
    return occupancy, vacancy

def get_all_directories(ftp_directory):
    all_entries = os.listdir(ftp_directory)
    ticker_pattern = re.compile(r'^[A-Z]{3,4}$')
    
    filtered_directories = [
        entry for entry in all_entries
        if os.path.isdir(os.path.join(ftp_directory, entry)) and
        ticker_pattern.match(entry)
    ]
    return filtered_directories

def potential_darwins_per_letter():
    potential_darwins = {}
    for letter in range(ord('A'), ord('Z') + 1):
        char = chr(letter)
        num_3_char = 26 * 26
        num_4_char = 26 * 26 * 26
        potential_darwins[char] = num_3_char + num_4_char
    return potential_darwins

def calculate_total_potential_darwins():
    potential_darwins = potential_darwins_per_letter()
    return sum(potential_darwins.values())

def main():
    ftp_directory = get_ftp_directory()
    target_directories = find_target_directories(ftp_directory)

    if not target_directories:
        print("No target directories found.")
        return

    active_darwins_3 = set()
    active_darwins_4 = set()
    all_darwins_3 = set()
    all_darwins_4 = set()

    for target_dir, parent_darwin in target_directories:
        darwins_3, darwins_4 = list_darwins_in_quotes_dir(target_dir, parent_darwin)
        all_darwins_3.update(darwins_3)
        all_darwins_4.update(darwins_4)
        for darwin in darwins_3:
            if is_active_darwin(target_dir, darwin):
                active_darwins_3.add(darwin)
        for darwin, parent in darwins_4:
            if is_active_darwin(target_dir, darwin):
                active_darwins_4.add((darwin, parent))

    # Count base 3-letter directories as known DARWINs
    for entry in os.listdir(ftp_directory):
        if len(entry) == 3 and re.match(r'^[A-Z]{3}$', entry):
            all_darwins_3.add(entry)

    # Extract the base letters from the DARWINs for letter counts
    letter_counts = Counter(darwin[0] for darwin in all_darwins_3)
    letter_counts.update(darwin[0] for darwin, _ in all_darwins_4)
    active_darwin_letters = [darwin[0] for darwin in active_darwins_3]
    active_darwin_letters += [parent for _, parent in active_darwins_4]
    active_darwins_per_letter = Counter(active_darwin_letters)
    potential_darwins = potential_darwins_per_letter()
    total_darwins = len(all_darwins_3) + len(all_darwins_4)
    total_active_darwins = len(active_darwins_3) + len(active_darwins_4)
    total_potential_darwins = sum(potential_darwins.values())
    total_vacancy = total_potential_darwins - total_darwins
    active_percentage = (total_active_darwins / total_darwins * 100) if total_darwins > 0 else 0
    occupancy_rates, vacancy_rates = calculate_occupancy_and_vacancy(letter_counts, active_darwins_per_letter, potential_darwins)

    # Write active DARWINs to the file
    with open('Active_Darwins.txt', 'w') as f:
        f.write("Active 3-letter DARWINs:\n")
        for darwin in sorted(active_darwins_3):
            f.write(f"{darwin}\n")

        f.write("\nActive 4-letter DARWINs and their parents:\n")
        for darwin, parent in sorted(active_darwins_4):
            f.write(f"{darwin} (Parent: {parent})\n")

    # Write known DARWINs to the file
    with open('Known_Darwins.txt', 'w') as f:
        f.write("Known 3-letter DARWINs:\n")
        for darwin in sorted(all_darwins_3):
            f.write(f"{darwin}\n")

        f.write("\nKnown 4-letter DARWINs and their parents:\n")
        for darwin, parent in sorted(all_darwins_4):
            f.write(f"{darwin} (Parent: {parent})\n")

    # Write statistics to the file
    with open('Darwin_Stats.txt', 'w') as f:
        f.write("Number of Darwins starting with each letter:\n")
        for letter in range(ord('A'), ord('Z') + 1):
            char = chr(letter)
            count = letter_counts.get(char, 0)
            active_count = active_darwins_per_letter.get(char, 0)
            occupancy_rate = occupancy_rates.get(char, {}).get('occupancy_rate', 0)
            vacancy_rate = vacancy_rates.get(char, 0)
            f.write(f"{char}: Known ({count}), Active ({active_count} ({occupancy_rate:.2f}%)), Vacancy Rate ({vacancy_rate:.2f}%)\n")

        f.write(f"\nTotal number of Darwins: {total_darwins}\n")
        f.write(f"Total number of active Darwins: {total_active_darwins}\n")
        f.write(f"Percentage of active Darwins: {active_percentage:.2f}%\n")
        f.write(f"Total number of potential Darwins: {total_potential_darwins}\n")
        f.write(f"Total vacancy: {total_vacancy}\n")

    # Print statistics to the terminal
    print("Number of Darwins starting with each letter:")
    for letter in range(ord('A'), ord('Z') + 1):
        char = chr(letter)
        count = letter_counts.get(char, 0)
        active_count = active_darwins_per_letter.get(char, 0)
        occupancy_rate = occupancy_rates.get(char, {}).get('occupancy_rate', 0)
        vacancy_rate = vacancy_rates.get(char, 0)
        print(f"{char}: Known ({count}), Active ({active_count} ({occupancy_rate:.2f}%)), Vacancy Rate ({vacancy_rate:.2f}%)")

    print(f"\nTotal number of Darwins: {total_darwins}")
    print(f"Total number of active Darwins: {total_active_darwins}")
    print(f"Percentage of active Darwins: {active_percentage:.2f}%")
    print(f"Total number of potential Darwins: {total_potential_darwins}")
    print(f"Total vacancy: {total_vacancy}")

    print("\nThe list of active DARWINs has been written to 'Active_Darwins.txt'.")
    print("The list of known DARWINs has been written to 'Known_Darwins.txt'.")
    print("The statistics have been written to 'Darwin_Stats.txt'.")

if __name__ == "__main__":
    main()
