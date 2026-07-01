import os
import pandas as pd

def main():
    script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(script_path))
    
    file_path = os.path.join(project_root, "data", "processed", "final_labeled_data.csv")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print("Fixing row alignment and restoring semicolon delimiters in Final_Label...")
    
    try:
        # Define the exact 7 original columns
        correct_columns = ["Year", "Series", "Network", "Character", "Actor", "Notes", "Final_Label"]
        
        # Load data safely by skipping structurally broken lines
        df = pd.read_csv(file_path, sep=",", encoding="utf-8-sig", on_bad_lines='skip')
        
        # Ensure the columns match our expected structure
        df.columns = correct_columns[:df.shape[1]] if df.shape[1] < len(correct_columns) else correct_columns
        
        # FIX FOR THE VISUALIZATION: 
        # Convert comma-separated labels back to semicolons so the network chart doesn't create gray nodes
        if 'Final_Label' in df.columns:
            # We look for common labels and fix formatting if Excel replaced semicolons with commas
            def fix_delimiters(val):
                if pd.isna(val): 
                    return val
                val_str = str(val).strip()
                # If there are commas but no semicolons, Excel likely converted them
                if "," in val_str and ";" not in val_str:
                    # Temporary placeholder to protect existing multi-word labels if needed,
                    # but standardizing to semicolon split is safest for your network script
                    items = [i.strip() for i in val_str.split(',') if i.strip()]
                    return "; ".join(items)
                return val_str

            df['Final_Label'] = df['Final_Label'].apply(fix_delimiters)
        
        # Save it back cleanly as a standard comma-separated CSV file
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print("Success! Structure repaired and Final_Label formatting restored to semicolons.")
        
    except Exception as e:
        print(f"An error occurred during recovery: {e}")

if __name__ == "__main__":
    main()