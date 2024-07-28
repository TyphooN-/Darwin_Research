import os
import re
import csv
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
    darwin_symbols = {}

    for idx, file_path in enumerate(files):
        print(f"Processing file {idx + 1}/{len(files)}: {file_path}")
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    timestamp = int(row[0])
                    num_periods = float(row[1])
                    period_data = eval(row[2])  # Evaluating the string representation of the list
                    for period in period_data:
                        for instrument_data in period:
                            instrument_id = instrument_data[0]
                            if instrument_id not in darwin_symbols:
                                darwin_symbols[instrument_id] = 0
                            darwin_symbols[instrument_id] += 1
                except (ValueError, IndexError, SyntaxError) as e:
                    print(f"Error processing line in file {file_path}: {e}")
    return darwin_symbols

def main():
    root_dir = get_ftp_directory()
    market_correlation_files = find_market_correlation_files(root_dir)
    darwin_symbols = tally_traded_symbols_per_darwin(market_correlation_files)
    
    # Print the results
    print("Correlated Symbols per DARWIN:")
    for darwin, symbols in darwin_symbols.items():
        print(f"{darwin}: {', '.join(symbols)}")

    # Write the results to a file
    with open("Correlated_Symbols_Per_Darwin.txt", 'w') as output_file:
        for darwin, symbols in darwin_symbols.items():
            output_file.write(f"{darwin}: {', '.join(symbols)}\n")
    
    print("Results written to Correlated_Symbols_Per_Darwin.txt")

if __name__ == "__main__":
    main()
