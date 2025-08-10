
import os
import re
from collections import defaultdict
from datetime import datetime

def get_ftp_directory():
    """Gets the directory path from the user."""
    while True:
        ftp_directory = input("Enter the path to the FTP directory: ")
        if os.path.isdir(ftp_directory):
            break
        else:
            print("Invalid path. Please enter a valid directory path.")
    return ftp_directory

def find_target_files(root_dir):
    """Finds all the target files to process."""
    target_files = []
    target_filenames = [
        'POSITIONS', 'LOSS_AVERSION', 'LOSS_AVERSION_UNADJUSTED_VAR', 'MARKET_CORRELATION',
        'ORDER_DIVERGENCE', 'TRADE_LOSS_AVERSION', 'TRADES', 'TRADE_UNADJUSTED_LOSS_AVERSION'
    ]
    print("Scanning for target files...")
    for dirpath, _, filenames in os.walk(root_dir):
        darwin_dir = os.path.basename(dirpath)
        if re.match(r'^[A-Z]{3,4}$', darwin_dir):
            for filename in filenames:
                if filename in target_filenames:
                    target_files.append(os.path.join(dirpath, filename))
    print(f"Total target files found: {len(target_files)}")
    return target_files

def get_darwin_from_path(file_path):
    """Extracts the DARWIN name from the file path."""
    return os.path.basename(os.path.dirname(file_path))

def process_files(target_files):
    """Processes files to tally symbols and group them by DARWIN."""
    symbol_pattern = re.compile(r"'([A-Za-z0-9+]+)'")
    darwin_symbols = defaultdict(set)
    symbol_tally = defaultdict(int)

    print("Processing files...")
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
                        symbol_tally[symbol] += 1
    print("Processing complete.")
    return darwin_symbols, symbol_tally

def write_traded_symbols_per_darwin(darwin_symbols, current_date):
    """Writes the traded symbols per DARWIN to a file."""
    output_filename = f"Traded_Symbols_Per_Darwin_{current_date}.txt"
    with open(output_filename, 'w') as file:
        for darwin, symbols in sorted(darwin_symbols.items()):
            file.write(f"DARWIN: {darwin}\n")
            file.write(f"Symbols: {', '.join(sorted(list(symbols)))}\n\n")
    print(f"Results saved to: {output_filename}")

def write_symbol_tally(symbol_tally, current_date):
    """Writes the symbol tally to a file."""
    output_filename = f"Traded_Symbols_{current_date}.txt"
    sorted_tally = sorted(symbol_tally.items(), key=lambda item: item[1], reverse=True)
    with open(output_filename, 'w') as output_file:
        for symbol, count in sorted_tally:
            output_file.write(f"{symbol}: {count}\n")
    print(f"Tally results written to {output_filename}")

def main():
    """Main function to run the script."""
    root_dir = get_ftp_directory()
    target_files = find_target_files(root_dir)
    if not target_files:
        print("No target files found.")
        return

    darwin_symbols, symbol_tally = process_files(target_files)
    current_date = datetime.today().strftime("%Y-%m-%d")

    write_traded_symbols_per_darwin(darwin_symbols, current_date)
    write_symbol_tally(symbol_tally, current_date)

if __name__ == "__main__":
    main()
