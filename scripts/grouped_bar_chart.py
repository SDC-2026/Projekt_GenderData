import pandas as pd
import plotly.express as px
import os

# Path configuration for running across different environments
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else '.'
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'final_labeled_data.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'plots')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'absolute_identities_bar.html')

# Check if the input file exists in the current directory as a fallback
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = 'final_labeled_data.csv'

# Updated High-Contrast Pride Colors Map
PRIDE_COLORS = {
    'Gay': '#008026',          # Rainbow Green
    'Lesbian': '#d62900',      # Lesbian Orange
    'Bisexual': '#0038a8',     # Bi Flag Dark Blue
    'Transgender': '#5bcefa',  # Trans Light Blue
    'Non-binary': '#fcf434',   # Non-binary Bright Yellow
    'Pansexual': '#ff1b8d',    # Pansexual Hot Pink
    'Genderfluid': '#FF76A4',  # Genderfluid Pink/Rose
    'Intersex': '#ffd800',     # Intersex Gold
    'Asexual': '#7400b8',      # Asexual Purple
    'Queer': '#4d004d',        # Queer Dark Violet
    'Questioning': '#78716c'   # Neutral Gray
}

def generate_chart():
    """
    Main execution pipeline: loads data, cleans year of release, 
    explodes multi-identity labels, and builds a single overall absolute bar chart 
    showing the exact character count for each separate identity (2020–2025).
    """
    print("=== Starting Overall Identity Bar Chart Generation ===")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Data file not found at: {os.path.abspath(INPUT_FILE)}")
        return

    # Load dataset
    df = pd.read_csv(INPUT_FILE)
    print(f"Successfully loaded {len(df)} raw records.")

    # 1. Chronological cleaning (extracting first 4 digits of the year)
    df["Year_Clean"] = df["Year"].astype(str).str.extract(r"(\d{4})")
    df["Year_Clean"] = pd.to_numeric(df["Year_Clean"], errors="coerce")

    # 2. Exploding multiple identity labels into separate rows
    df_labels = df.copy()
    df_labels["Final_Label"] = df_labels["Final_Label"].astype(str).str.split(";")
    df_labels = df_labels.explode("Final_Label")
    df_labels["Final_Label"] = df_labels["Final_Label"].str.strip()

    # 3. Filtering out placeholders and missing records
    df_labels = df_labels[~df_labels["Final_Label"].str.contains("MANUAL", case=False, na=True)]
    df_labels = df_labels.dropna(subset=["Year_Clean", "Final_Label"])
    df_labels["Year_Clean"] = df_labels["Year_Clean"].astype(int)

    # 4. Restricting the analysis to 2020-2025 release years
    min_year, max_year = 2020, 2025
    df_labels = df_labels[(df_labels["Year_Clean"] >= min_year) & (df_labels["Year_Clean"] <= max_year)]
    print(f"Filtered {len(df_labels)} exploded records for visualization within range [{min_year}-{max_year}].")

    # Create output directory if it does not exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ==========================================
    # DATA PREPARATION FOR ABSOLUTE COUNT CHART
    # ==========================================
    # Compute absolute count per separate identity
    df_plot = df_labels.groupby('Final_Label').size().reset_index(name='Count')
    
    # Filter to only include identities that are defined in our color map
    df_plot = df_plot[df_plot['Final_Label'].isin(PRIDE_COLORS.keys())]

    # Sort values descending by absolute count for better visualization layout
    df_plot = df_plot.sort_values(by='Count', ascending=False)

    # ==========================================
    # BAR CHART VISUALIZATION
    # ==========================================
    fig = px.bar(
        df_plot,
        x='Final_Label',
        y='Count',
        color='Final_Label',
        title='Absolute Count of LGBTQ+ Identities in TV Series (2020–2025)',
        labels={
            'Final_Label': 'Identity', 
            'Count': 'Absolute Count'
        },
        color_discrete_map=PRIDE_COLORS
    )

    # Customizing the hover tooltip to display clean English text without extra tags
    fig.update_traces(
        hovertemplate=(
            "<b>Identity: %{x}</b><br>"
            "Absolute Count: %{y} characters<extra></extra>"
        )
    )

    # Configure axes and layout
    fig.update_layout(
        xaxis=dict(
            title_text='LGBTQ+ Identity'
        ),
        yaxis=dict(
            title_text='Number of Characters',
            range=[0, df_plot['Count'].max() + 5]  # Adjust ceiling dynamically
        ),
        height=600,
        margin=dict(l=50, r=50, t=80, b=50),
        showlegend=False  # Disabled legend since identity labels are fully readable on the X-axis
    )

    # Save and preview chart
    fig.write_html(OUTPUT_FILE)
    print(f"Bar chart successfully saved to: {os.path.abspath(OUTPUT_FILE)}")
    fig.show()

if __name__ == "__main__":
    generate_chart()