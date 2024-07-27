import os
import re
from collections import defaultdict

def get_ftp_directory():
    while True:
        ftp_directory = input("Enter the path to the FTP directory: ")
        if os.path.isdir(ftp_directory):
            break
        else:
            print("Invalid path. Please enter a valid directory path.")
    return ftp_directory

def find_positions_files(root_dir):
    positions_files = []
    print("Scanning for POSITIONS files...")
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == 'POSITIONS':
                positions_files.append(os.path.join(dirpath, filename))
                print(f"Found POSITIONS file: {os.path.join(dirpath, filename)}")
    print(f"Total POSITIONS files found: {len(positions_files)}")
    return positions_files

def tally_traded_symbols(positions_files):
    symbol_pattern = re.compile(r"'([A-Za-z0-9+]+)'")
    symbol_tally = defaultdict(int)
    
    print("Tallying traded symbols...")
    for i, file_path in enumerate(positions_files, start=1):
        print(f"Processing file {i}/{len(positions_files)}: {file_path}")
        with open(file_path, 'r') as file:
            for line in file:
                matches = symbol_pattern.findall(line)
                for match in matches:
                    symbols = match.split('+')
                    for symbol in symbols:
                        symbol_tally[symbol] += 1
    
    print("Tallying complete.")
    return symbol_tally

def main():
    root_dir = get_ftp_directory()
    positions_files = find_positions_files(root_dir)
    symbol_tally = tally_traded_symbols(positions_files)
    
    # Print the results
    print("Traded Symbols Tally:")
    for symbol, count in symbol_tally.items():
        print(f"{symbol}: {count}")

    # Write the results to a file
    with open("Traded_Symbols.txt", 'w') as output_file:
        for symbol, count in symbol_tally.items():
            output_file.write(f"{symbol}: {count}\n")
    
    print("Results written to Traded_Symbols.txt")

if __name__ == "__main__":
    main()
