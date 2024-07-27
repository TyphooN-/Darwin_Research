import os
import re
import json
from collections import defaultdict

def get_ftp_directory():
    while True:
        ftp_directory = input("Enter the path to the FTP directory: ")
        if os.path.isdir(ftp_directory):
            break
        else:
            print("Invalid path. Please enter a valid directory path.")
    return ftp_directory

def find_market_correlation_files(root_dir):
    market_correlation_files = []
    print("Scanning for MARKET_CORRELATION files...")
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == 'MARKET_CORRELATION':
                market_correlation_files.append(os.path.join(dirpath, filename))
                print(f"Found MARKET_CORRELATION file: {os.path.join(dirpath, filename)}")
    print(f"Total MARKET_CORRELATION files found: {len(market_correlation_files)}")
    return market_correlation_files

def get_darwin_from_path(file_path):
    # Assuming the DARWIN name is the last directory in the path
    return os.path.basename(os.path.dirname(file_path))

def tally_traded_symbols_per_darwin(market_correlation_files):
    symbol_pattern = re.compile(r"'([A-Za-z0-9]+)'")
    darwin_symbols = defaultdict(set)
    
    print("Tallying traded symbols per DARWIN...")
    for i, file_path in enumerate(market_correlation_files, start=1):
        print(f"Processing file {i}/{len(market_correlation_files)}: {file_path}")
        darwin = get_darwin_from_path(file_path)
        with open(file_path, 'r') as file:
            data = json.load(file)
            for record in data:
                for symbol_data in record[2]:
                    symbol = symbol_data[0]
                    darwin_symbols[darwin].add(symbol)
    
    print("Tallying complete.")
    return darwin_symbols

def main():
    root_dir = get_ftp_directory()
    market_correlation_files = find_market_correlation_files(root_dir)
    darwin_symbols = tally_traded_symbols_per_darwin(market_correlation_files)
    
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
