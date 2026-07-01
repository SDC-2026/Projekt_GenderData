import pandas as pd
import os


# =========================================================
# PATHS
# =========================================================

script_path = os.path.abspath(__file__)

project_root = os.path.dirname(
    os.path.dirname(script_path)
)

processed_dir = os.path.join(
    project_root,
    "data",
    "processed"
)

auto_file = os.path.join(
    processed_dir,
    "labeled_data.csv"
)

manual_file = os.path.join(
    processed_dir,
    "manual_review_completed.csv"
)

final_file = os.path.join(
    processed_dir,
    "labeled_data.csv"
)


# =========================================================
# LOAD FILES
# =========================================================

auto_df = pd.read_csv(auto_file)

manual_df = pd.read_csv(
    manual_file,
    sep=";"
)

# =========================================================
# REMOVE MANUAL PLACEHOLDERS
# =========================================================

auto_clean = auto_df[
    auto_df["Final_Label"]
    != "[MANUAL_REVIEW_REQUIRED]"
]


# =========================================================
# MERGE DATA
# =========================================================

final_df = pd.concat(
    [auto_clean, manual_df],
    ignore_index=True
)


# =========================================================
# SAVE FINAL DATASET
# =========================================================

final_df.to_csv(
    final_file,
    index=False,
    encoding="utf-8-sig"
)

print("\nFinal dataset created:")
print(final_file)

print(f"\nTotal rows: {len(final_df)}")