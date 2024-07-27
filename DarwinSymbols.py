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

def get_darwin_from_path(file_path):
    # Assuming the DARWIN name is the last directory in the path
    return os.path.basename(os.path.dirname(file_path))

def tally_traded_symbols_per_darwin(positions_files):
    symbol_pattern = re.compile(r"'([A-Za-z0-9+]+)'")
    darwin_symbols = defaultdict(set)
    
    print("Tallying traded symbols per DARWIN...")
    for i, file_path in enumerate(positions_files, start=1):
        print(f"Processing file {i}/{len(positions_files)}: {file_path}")
        darwin = get_darwin_from_path(file_path)
        with open(file_path, 'r') as file:
            for line in file:
                matches = symbol_pattern.findall(line)
                for match in matches:
                    symbols = match.split('+')
                    for symbol in symbols:
                        darwin_symbols[darwin].add(symbol)
    
    print("Tallying complete.")
    return darwin_symbols

def main():
    root_dir = get_ftp_directory()
    positions_files = find_positions_files(root_dir)
    darwin_symbols = tally_traded_symbols_per_darwin(positions_files)
    
    # Print the results
    print("Traded Symbols per DARWIN:")
    for darwin, symbols in darwin_symbols.items():
        print(f"{darwin}: {', '.join(symbols)}")

    # Write the results to a file
    with open("Traded_Symbols_Per_Darwin.txt", 'w') as output_file:
        for darwin, symbols in darwin_symbols.items():
            output_file.write(f"{darwin}: {', '.join(symbols)}\n")
    
    print("Results written to Traded_Symbols_Per_Darwin.txt")

if __name__ == "__main__":
    main()
