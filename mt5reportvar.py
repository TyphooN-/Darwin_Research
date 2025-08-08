import pandas as pd
import sys
import os

def calculate_notional_var():
    """
    Processes an Excel trade report by adding a 'Notional_VaR' column to each
    section (Positions, Orders, Deals), preserving all original data.
    The output filename is generated dynamically from the input filenames.
    """
    try:
        # --- Get User Input for files ---
        file1 = input("Enter the path for the first file (CSV or Excel): ")
        file2 = input("Enter the path for the second file (CSV or Excel): ")

        if file1.lower().endswith('.csv') and file2.lower().endswith('.xlsx'):
            symbols_file = file1
            trades_file = file2
        elif file1.lower().endswith('.xlsx') and file2.lower().endswith('.csv'):
            symbols_file = file2
            trades_file = file1
        else:
            print("Error: You must provide one '.csv' file and one '.xlsx' file.")
            sys.exit(1)

        # --- Create Dynamic Output Filename ---
        symbols_basename = os.path.splitext(os.path.basename(symbols_file))[0]
        trades_basename = os.path.splitext(os.path.basename(trades_file))[0]
        output_file = f"{trades_basename}-{symbols_basename}.csv"

        # --- Read Symbol VaR Data ---
        print(f"Reading symbols from {symbols_file}...")
        var_df = pd.read_csv(symbols_file, delimiter=';')
        known_symbols = set(var_df['Symbol'].unique())
        var_map = var_df.set_index('Symbol')['VaR_1_Lot'].to_dict()
        print(f"Successfully loaded VaR data for {len(var_map)} symbols.")

        # --- Read Entire Excel Sheet, preserving all data ---
        print(f"Reading all data from {trades_file}...")
        df = pd.read_excel(trades_file, header=None)
        print(f"Successfully loaded {len(df)} rows.")

        # --- Add the new column, initially empty ---
        notional_var_col_idx = len(df.columns)
        df[notional_var_col_idx] = None
        total_processed_count = 0

        # --- Find all header rows and process each section ---
        header_indices = []
        for r_idx, row in df.iterrows():
            row_values = [str(cell).strip().lower() for cell in row.values]
            if 'symbol' in row_values and 'volume' in row_values:
                header_indices.append(r_idx)
        
        if not header_indices:
            print("Error: Could not automatically find any header rows with both 'Symbol' and 'Volume'.")
            sys.exit(1)

        print(f"Found {len(header_indices)} sections to process (Positions, Deals, Orders).")

        # Process each section defined by a header
        for i, header_idx in enumerate(header_indices):
            # Add header to the new column
            df.iloc[header_idx, notional_var_col_idx] = 'Notional VaR'

            start_row = header_idx + 1
            end_row = header_indices[i + 1] if i + 1 < len(header_indices) else len(df)
            
            header_row = [str(cell).strip().lower() for cell in df.iloc[header_idx]]
            symbol_col_idx = header_row.index('symbol')
            volume_col_idx = header_row.index('volume')

            print(f"Processing section starting at row {header_idx + 2}...")
            section_processed_count = 0

            for idx in range(start_row, end_row):
                if idx >= len(df): break
                row = df.iloc[idx]
                symbol = str(row.iloc[symbol_col_idx])
                
                if symbol in known_symbols:
                    # Handle volumes like '1 / 1' in Orders section
                    volume_val = str(row.iloc[volume_col_idx]).split('/')[0].strip()
                    volume = pd.to_numeric(volume_val, errors='coerce')
                    
                    if pd.notna(volume):
                        notional_var = var_map[symbol] * volume
                        df.iloc[idx, notional_var_col_idx] = notional_var
                        section_processed_count += 1
            
            print(f"  -> Calculated VaR for {section_processed_count} trades.")
            total_processed_count += section_processed_count

        print(f"\nSuccessfully calculated VaR for {total_processed_count} total trades across all sections.")

        # --- Save the entire, modified DataFrame to CSV ---
        print(f"Saving the complete, updated report to {output_file}...")
        df.to_csv(output_file, index=False, header=False)

        print(f"\nProcess completed successfully!")
        print(f"The new report is available at: {output_file}")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    calculate_notional_var()