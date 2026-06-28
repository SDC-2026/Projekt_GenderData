import pandas as pd
import plotly.express as px
import os

# Path configuration for running across different environments
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else '.'
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'final_labeled_data.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'plots')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'relative_identities_line.html')

# Check if the input file exists in the current directory as a fallback
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = 'final_labeled_data.csv'

# Color palette updated to 85% opacity RGBA values matching the neobrutalist theme
PRIDE_COLORS = {
    'Lesbian': 'rgba(234, 88, 12, 0.85)',               # Warm orange-red
    'Gay': 'rgba(5, 150, 105, 0.85)',                   # Emerald green
    'Bisexual & Pansexual': 'rgba(217, 70, 239, 0.85)',  # Vibrant fuchsia
    'Trans & Non-Binary': 'rgba(56, 189, 248, 0.85)',    # Light blue
    'Asexual': 'rgba(124, 58, 237, 0.85)',               # Violet
    'Queer / Questioning': 'rgba(236, 72, 153, 0.85)',   # Pink
    'Other / Unknown': 'rgba(148, 163, 184, 0.85)'        # Gray
}

def simplify_identity(label):
    if pd.isna(label):
        return 'Other / Unknown'
    
    label_clean = str(label).strip().lower()
    
    if any(x in label_clean for x in ['transgender', 'trans', 'non-binary', 'genderfluid', 'intersex']):
        return 'Trans & Non-Binary'
        
    if any(x in label_clean for x in ['bisexual', 'pansexual', 'demisexual', 'fluid']):
        return 'Bisexual & Pansexual'
    elif 'lesbian' in label_clean:
        return 'Lesbian'
    elif 'gay' in label_clean:
        return 'Gay'
    elif 'asexual' in label_clean:
        return 'Asexual'
    elif 'queer' in label_clean or 'questioning' in label_clean:
        return 'Queer / Questioning'
        
    return 'Other / Unknown'

def generate_chart():
    print("=== Starting Line Chart Generation ===")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Data file not found at: {os.path.abspath(INPUT_FILE)}")
        return

    # Load dataset
    df = pd.read_csv(INPUT_FILE)
    print(f"Successfully loaded {len(df)} raw records.")

    # 1. Chronological cleaning
    df["Year_Clean"] = df["Year"].astype(str).str.extract(r"(\d{4})")
    df["Year_Clean"] = pd.to_numeric(df["Year_Clean"], errors="coerce")

    # 2. Exploding multiple identity labels
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
    
    df_labels['Simplified_Label'] = df_labels['Final_Label'].apply(simplify_identity)
    print(f"Filtered {len(df_labels)} exploded records within range [{min_year}-{max_year}].")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Data preparation
    df_totals = df_labels.groupby('Year_Clean').size().reset_index(name='Total_Count')
    df_counts = df_labels.groupby(['Year_Clean', 'Simplified_Label']).size().reset_index(name='Count')
    
    df_plot = pd.merge(df_counts, df_totals, on='Year_Clean')
    df_plot['Percentage'] = (df_plot['Count'] / df_plot['Total_Count']) * 100
    df_plot = df_plot.sort_values(by=['Year_Clean', 'Simplified_Label'])

    # Base chart creation (title stripped for Quarto embedding)
    fig = px.line(
        df_plot,
        x='Year_Clean',
        y='Percentage',
        color='Simplified_Label',
        title=None,
        labels={
            'Year_Clean': 'YEAR OF RELEASE', 
            'Percentage': 'PERCENTAGE SHARE (%)', 
            'Simplified_Label': 'IDENTITY'
        },
        color_discrete_map=PRIDE_COLORS,
        markers=True,
        custom_data=['Count']
    )

    # UNIFIED HOVER TOOLTIP & BRUTALIST STYLING FOR LINES AND MARKERS
    fig.update_traces(
        line=dict(width=4),                      # Thicker, bolder lines
        marker=dict(
            symbol='square',                     # Harsh brutalist square markers
            size=10,
            line=dict(color='#000000', width=2)  # High-contrast black outlines
        ),
        hovertemplate=(
            "<b>PERCENTAGE: %{y:.1f}%</b><br>"
            "<b>TOTAL CHARACTERS: %{customdata[0]}</b><extra></extra>"
        )
    )

    # NEO-BRUTALIST WEB DESIGN COHESION
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        
        font=dict(
            family='"Helvetica Neue", Helvetica, Arial, sans-serif',
            size=13,
            color='#000000'
        ),
        
        xaxis=dict(
            title=dict(text='YEAR OF RELEASE', font=dict(weight='bold', size=14)),
            tickvals=list(range(min_year, max_year + 1)),
            tickmode='array',
            showgrid=False,
            showline=True,
            linecolor='#000000',
            linewidth=3,
            tickfont=dict(weight='bold', size=12)
        ),
        
        yaxis=dict(
            title=dict(text='PERCENTAGE SHARE', font=dict(weight='bold', size=14)),
            ticksuffix="%",
            range=[0, max(df_plot['Percentage'].max() + 5, 50)],
            showgrid=False,
            showline=True,
            linecolor='#000000',
            linewidth=3,
            tickfont=dict(weight='bold', size=12)
        ),
        
        hoverlabel=dict(
            bgcolor='#ffffff',
            bordercolor='#000000',
            font=dict(
                family='"Helvetica Neue", Helvetica, Arial, sans-serif',
                size=13,
                color='#000000',
                weight='bold'
            )
        ),
        
        legend=dict(
            title=dict(text='IDENTITY', font=dict(weight='bold')),
            font=dict(weight='bold', size=11),
            bgcolor='rgba(256,256,256,0.9)',
            bordercolor='#000000',
            borderwidth=2
        ),
        
        height=600,
        # Reduced top margin from 90 to 25 to match other headless plots
        margin=dict(l=65, r=50, t=25, b=60)
    )

    # Save and preview chart
    fig.write_html(OUTPUT_FILE, config={'displayModeBar': False})
    print(f"Line chart successfully saved to: {os.path.abspath(OUTPUT_FILE)}")
    fig.show()

if __name__ == "__main__":
    generate_chart()