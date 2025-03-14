import pandas as pd

def find_missing_rows(csv_file1, csv_file2):
    # Read the CSV files into DataFrames
    df1 = pd.read_csv(csv_file1)
    df2 = pd.read_csv(csv_file2)

    # Ensure 'Symbol' column exists in both DataFrames
    if 'Symbol' not in df1.columns or 'Symbol' not in df2.columns:
        raise ValueError("Both CSV files must have a 'Symbol' column.")

    # Find rows in df1 that are not in df2 based on the 'Symbol' column
    missing_in_df2 = df1[~df1['Symbol'].isin(df2['Symbol'])]

    # Find rows in df2 that are not in df1 based on the 'Symbol' column
    missing_in_df1 = df2[~df2['Symbol'].isin(df1['Symbol'])]

    return missing_in_df2, missing_in_df1

def main():
    # Ask for input filenames at runtime
    csv_file1_path = input("Please enter the path to your first CSV file: ")
    csv_file2_path = input("Please enter the path to your second CSV file: ")

    try:
        missing_rows_1_to_2, missing_rows_2_to_1 = find_missing_rows(csv_file1_path, csv_file2_path)
        
        print(f"\nRows in {csv_file1_path} but not in {csv_file2_path} (based on 'Symbol' column):")
        print(missing_rows_1_to_2)
        print("\n")

        print(f"Rows in {csv_file2_path} but not in {csv_file1_path} (based on 'Symbol' column):")
        print(missing_rows_2_to_1)

        # Optionally, save the missing rows to new CSV files
        save_choice = input("Would you like to save these results as new CSV files? (yes/no): ")
        if save_choice.lower() == "yes":
            missing_rows_1_to_2.to_csv('rows_missing_in_second.csv', index=False)
            missing_rows_2_to_1.to_csv('rows_missing_in_first.csv', index=False)
            print("Results saved as rows_missing_in_second.csv and rows_missing_in_first.csv")
        else:
            print("Results not saved.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

