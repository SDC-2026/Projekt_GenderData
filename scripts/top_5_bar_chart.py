import pandas as pd
import plotly.express as px
import os

# 1. Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else '.'
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'final_labeled_data.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'plots')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'top_5_series_stacked.html')

if not os.path.exists(INPUT_FILE):
    INPUT_FILE = 'final_labeled_data.csv'

# Unique Neo-Brutalist Pride Colors Map (Updated with 85% opacity rgba values)
PRIDE_COLORS = {
    'Lesbian': 'rgba(214, 41, 0, 0.85)',
    'Gay': 'rgba(0, 128, 38, 0.85)',
    'Bisexual': 'rgba(0, 56, 168, 0.85)',
    'Transgender': 'rgba(91, 206, 250, 0.85)',
    'Non-binary': 'rgba(252, 244, 52, 0.85)',
    'Pansexual': 'rgba(255, 27, 141, 0.85)',
    'Genderfluid': 'rgba(255, 118, 164, 0.85)',
    'Intersex': 'rgba(255, 216, 0, 0.85)',
    'Asexual': 'rgba(116, 0, 184, 0.85)',
    'Queer': 'rgba(77, 0, 77, 0.85)',
    'Questioning': 'rgba(120, 113, 108, 0.85)'
}

def generate_chart():
    print("=== Starting Top 5 Series Stacked Chart Generation (With Totals) ===")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Data file not found at: {os.path.abspath(INPUT_FILE)}")
        return

    # Load dataset
    df = pd.read_csv(INPUT_FILE)

    # Automatically detect the correct column name for the series
    series_col = None
    for col in ['TV Series', 'Series', 'Show', 'show', 'series', 'Title']:
        if col in df.columns:
            series_col = col
            break
            
    if not series_col:
        print(f"Error: Could not find a column for TV Series. Available columns: {list(df.columns)}")
        return

    # 1. Chronological cleaning (2020-2025)
    df["Year_Clean"] = df["Year"].astype(str).str.extract(r"(\d{4})")
    df["Year_Clean"] = pd.to_numeric(df["Year_Clean"], errors="coerce")

    # 2. Exploding multiple identity labels
    df_labels = df.copy()
    df_labels["Final_Label"] = df_labels["Final_Label"].astype(str).str.split(";")
    df_labels = df_labels.explode("Final_Label")
    df_labels["Final_Label"] = df_labels["Final_Label"].str.strip()

    # 3. Filtering Out Placeholders and restricting years
    df_labels = df_labels[~df_labels["Final_Label"].str.contains("MANUAL", case=False, na=True)]
    df_labels = df_labels.dropna(subset=["Year_Clean", "Final_Label", series_col])
    
    min_year, max_year = 2020, 2025
    df_labels = df_labels[(df_labels["Year_Clean"] >= min_year) & (df_labels["Year_Clean"] <= max_year)]
    df_labels = df_labels[df_labels['Final_Label'].isin(PRIDE_COLORS.keys())]

    # 4. Find the Top 5 Series with the absolute most LGBTQ+ records
    top_series = df_labels.groupby(series_col).size().nlargest(5).index.tolist()
    
    # Filter dataset to keep only these top 5 series
    df_top5 = df_labels[df_labels[series_col].isin(top_series)].copy()

    # 5. Aggregate to get counts per Series and Identity
    df_plot = df_top5.groupby([series_col, 'Final_Label']).size().reset_index(name='Count')

    # Sort series order based on the total count so the largest bar is at the top
    series_totals = df_plot.groupby(series_col)['Count'].sum().sort_values(ascending=True).index
    
    # Base chart creation (Horizontal Stacked Bar)
    fig = px.bar(
        df_plot,
        y=series_col,
        x='Count',
        color='Final_Label',
        orientation='h',
        title='TOP 5 TV SERIES WITH THE MOST LGBTQ+ CHARACTERS',
        labels={series_col: 'TV SERIES', 'Count': 'NUMBER OF CHARACTERS', 'Final_Label': 'IDENTITY'},
        color_discrete_map=PRIDE_COLORS,
        category_orders={
            series_col: list(series_totals),
            'Final_Label': list(PRIDE_COLORS.keys())
        }
    )

    # UNIFIED HOVER TOOLTIP & BRUTALIST BORDERS & TOTAL COUNT DISPLAY
    fig.update_traces(
        marker=dict(
            line=dict(color='#000000', width=2)
        ),
        hovertemplate=(
            "<b>COUNT: %{x} characters</b><extra></extra>"
        )
    )

    # BRUTALIST WEBSITE COHESION LAYOUT
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        
        font=dict(
            family='"Helvetica Neue", Helvetica, Arial, sans-serif',
            size=13,
            color='#000000'
        ),
        
        title=dict(
            font=dict(size=18, color='#000000', weight=900),
            x=0.02,
            y=0.95
        ),
        
        xaxis=dict(
            title=dict(text='NUMBER OF CHARACTERS', font=dict(weight='bold', size=14)),
            showgrid=False,
            showline=True,
            linecolor='#000000',
            linewidth=3,
            tickfont=dict(weight='bold', size=12),
            # Add extra padding on the right side so the total label fits perfectly without clipping
            range=[0, df_plot.groupby(series_col)['Count'].sum().max() + 2]
        ),
        
        yaxis=dict(
            title=dict(text='TV SERIES', font=dict(weight='bold', size=14)),
            showgrid=False,
            showline=True,
            linecolor='#000000',
            linewidth=3,
            tickfont=dict(weight='bold', size=11)
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
        
        height=500,
        margin=dict(l=150, r=40, t=90, b=60),
        barmode='stack'
    )

    # Add total sum text at the end of each stacked horizontal bar
    # (Plotly does not support stacked totals automatically out-of-the-box via text_auto, so we use annotations)
    for series in series_totals:
        total_sum = df_plot[df_plot[series_col] == series]['Count'].sum()
        fig.add_annotation(
            y=series,
            x=total_sum,
            text=f"<b>{total_sum}</b>",
            showarrow=False,
            xanchor='left',
            xshift=10,  # Shifts the number slightly to the right outside the bar border
            font=dict(
                family='"Helvetica Neue", Helvetica, Arial, sans-serif',
                size=14,
                color='#000000'
            )
        )

    # Save and preview chart
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.write_html(OUTPUT_FILE, config={'displayModeBar': False})
    print(f"Stacked brutalist bar chart successfully saved to: {os.path.abspath(OUTPUT_FILE)}")
    fig.show()

if __name__ == "__main__":
    generate_chart()