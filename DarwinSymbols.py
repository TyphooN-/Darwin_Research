import os
import re
from collections import defaultdict
from datetime import datetime  # Added import for datetime

def get_ftp_directory():
    while True:
        ftp_directory = input("Enter the path to the FTP directory: ")
        if os.path.isdir(ftp_directory):
            break
        else:
            print("Invalid path. Please enter a valid directory path.")
    return ftp_directory

def find_target_files(root_dir):
    target_files = []
    target_filenames = [
        'POSITIONS', 'LOSS_AVERSION', 'LOSS_AVERSION_UNADJUSTED_VAR', 'MARKET_CORRELATION',
        'ORDER_DIVERGENCE', 'TRADE_LOSS_AVERSION', 'TRADES', 'TRADE_UNADJUSTED_LOSS_AVERSION'
    ]
    print("Scanning for target files...")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Check if this directory corresponds to a DARWIN (3 or 4 letters)
        darwin_dir = os.path.basename(dirpath)
        if re.match(r'^[A-Z]{3,4}$', darwin_dir):
            for filename in filenames:
                if filename in target_filenames:
                    target_files.append(os.path.join(dirpath, filename))
                    print(f"Found {filename} file: {os.path.join(dirpath, filename)}")
    print(f"Total target files found: {len(target_files)}")
    return target_files

def get_darwin_from_path(file_path):
    # Assuming the DARWIN name is the last directory in the path
    return os.path.basename(os.path.dirname(file_path))

def tally_traded_symbols_per_darwin(target_files):
    symbol_pattern = re.compile(r"'([A-Za-z0-9+]+)'")
    darwin_symbols = defaultdict(set)
    
    print("Tallying traded symbols per DARWIN...")
    for i, file_path in enumerate(target_files, start=1):
        print(f"Processing file {i}/{len(target_files)}: {file_path}")
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
    target_files = find_target_files(root_dir)
    if not target_files:
        print("No target files found.")
        return
    
    darwin_symbols = tally_traded_symbols_per_darwin(target_files)
    
    # Generate the output filename with the current date
    current_date = datetime.today().strftime("%Y-%m-%d")
    output_filename = f"Traded_Symbols_Per_Darwin_{current_date}.txt"
    
    # Write results to file
    with open(output_filename, 'w') as file:
        for darwin, symbols in darwin_symbols.items():
            file.write(f"DARWIN: {darwin}\n")
            file.write(f"Symbols: {', '.join(symbols)}\n\n")
    
    print(f"Results saved to: {output_filename}")

if __name__ == "__main__":
    main()

