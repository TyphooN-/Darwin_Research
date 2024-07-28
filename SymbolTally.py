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

def find_target_files(root_dir, target_files):
    found_files = []
    print(f"Scanning for target files: {', '.join(target_files)}...")
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename in target_files:
                found_files.append(os.path.join(dirpath, filename))
                print(f"Found {filename} file: {os.path.join(dirpath, filename)}")
    print(f"Total target files found: {len(found_files)}")
    return found_files

def tally_traded_symbols(target_files):
    symbol_pattern = re.compile(r"'([A-Za-z0-9+]+)'")
    symbol_tally = defaultdict(int)
    
    print("Tallying traded symbols...")
    for i, file_path in enumerate(target_files, start=1):
        print(f"Processing file {i}/{len(target_files)}: {file_path}")
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
    target_files = [
        'POSITIONS', 'LOSS_AVERSION', 'LOSS_AVERSION_UNADJUSTED_VAR',
        'MARKET_CORRELATION', 'ORDER_DIVERGENCE', 'TRADE_LOSS_AVERSION',
        'TRADES', 'TRADE_UNADJUSTED_LOSS_AVERSION'
    ]
    
    root_dir = get_ftp_directory()
    found_files = find_target_files(root_dir, target_files)
    symbol_tally = tally_traded_symbols(found_files)
    
    # Sort the results by count in descending order
    sorted_tally = sorted(symbol_tally.items(), key=lambda item: item[1], reverse=True)
    
    # Print the results
    print("Traded Symbols Tally:")
    for symbol, count in sorted_tally:
        print(f"{symbol}: {count}")

    # Write the results to a file
    with open("Traded_Symbols.txt", 'w') as output_file:
        for symbol, count in sorted_tally:
            output_file.write(f"{symbol}: {count}\n")
    
    print("Results written to Traded_Symbols.txt")

if __name__ == "__main__":
    main()
