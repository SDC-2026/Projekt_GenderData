import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# 1. Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else '.'
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'final_labeled_data.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'plots')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'identity_pictogram_v2.html')

if not os.path.exists(INPUT_FILE):
    INPUT_FILE = 'final_labeled_data.csv'

# Exact High-Contrast Pride Colors Map matched with Intersectional Identity Network
PRIDE_COLORS = {
    'Gay': '#008026',
    'Lesbian': '#d62900',
    'Bisexual': '#0038a8',
    'Transgender': '#5bcefa',
    'Non-binary': '#fcf434',
    'Pansexual': '#ff1b8d',
    'Genderfluid': '#FF76A4',
    'Intersex': '#ffd800',
    'Asexual': '#7400b8',
    'Queer': '#4d004d',
    'Questioning': '#78716c'
}

def hex_to_rgba(hex_str, alpha=0.85):
    hex_str = hex_str.lstrip('#')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def generate_chart():
    print("=== Starting Vector Identity Pictogram Generation (v2) ===")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Data file not found at: {os.path.abspath(INPUT_FILE)}")
        return

    # Load dataset
    df = pd.read_csv(INPUT_FILE)

    # Clean and filter years (2020-2025)
    df["Year_Clean"] = df["Year"].astype(str).str.extract(r"(\d{4})")
    df["Year_Clean"] = pd.to_numeric(df["Year_Clean"], errors="coerce")

    df_labels = df.copy()
    df_labels["Final_Label"] = df_labels["Final_Label"].astype(str).str.split(";")
    df_labels = df_labels.explode("Final_Label")
    df_labels["Final_Label"] = df_labels["Final_Label"].str.strip()

    df_labels = df_labels[~df_labels["Final_Label"].str.contains("MANUAL", case=False, na=True)]
    df_labels = df_labels.dropna(subset=["Year_Clean", "Final_Label"])
    
    min_year, max_year = 2020, 2025
    df_labels = df_labels[(df_labels["Year_Clean"] >= min_year) & (df_labels["Year_Clean"] <= max_year)]

    # Get absolute counts and sort
    df_plot = df_labels.groupby('Final_Label').size().reset_index(name='Count')
    df_plot = df_plot[df_plot['Final_Label'].isin(PRIDE_COLORS.keys())]
    df_plot = df_plot.sort_values(by='Count', ascending=False)

    fig = go.Figure()

    # Grid configuration
    ITEMS_PER_ROW = 5  
    VERTICAL_STEP = 1.9  

    for x_idx, row in enumerate(df_plot.itertuples()):
        label = row.Final_Label
        count = row.Count
        color_rgba = hex_to_rgba(PRIDE_COLORS[label], alpha=0.85)

        x_body = []
        y_body = []
        
        x_head = []
        y_head = []
        
        for i in range(count):
            row_num = i // ITEMS_PER_ROW
            col_num = i % ITEMS_PER_ROW
            
            base_x = x_idx + (col_num - (ITEMS_PER_ROW - 1) / 2) * 0.15
            base_y = row_num * VERTICAL_STEP
            
            x_body.append(base_x)
            y_body.append(base_y)
            
            x_head.append(base_x)
            y_head.append(base_y + 1.35)

        # 1. DRAW BODIES (Triangle-Up)
        fig.add_trace(go.Scatter(
            x=x_body,
            y=y_body,
            mode='markers',
            name=label,
            marker=dict(
                symbol='triangle-up',
                size=18,
                color=color_rgba,
                line=dict(color='#000000', width=1.5)
            ),
            hoverinfo='text',
            hovertext=[f"<b>IDENTITY: {label.upper()}</b><br>TOTAL CHARACTERS: {count}"] * len(x_body),
            showlegend=False
        ))

        # 2. DRAW HEADS (Circle)
        fig.add_trace(go.Scatter(
            x=x_head,
            y=y_head,
            mode='markers',
            name=label,
            marker=dict(
                symbol='circle',
                size=8,
                color=color_rgba,
                line=dict(color='#000000', width=1.5)
            ),
            hoverinfo='text',
            hovertext=[f"<b>IDENTITY: {label.upper()}</b><br>TOTAL CHARACTERS: {count}"] * len(x_head),
            showlegend=False
        ))

    # Calculate max rows for Y-axis scaling
    max_count = df_plot['Count'].max()
    max_y_val = (max_count // ITEMS_PER_ROW) * VERTICAL_STEP

    # Layout configuration
    fig.update_layout(
        title=dict(
            text="ABSOLUTE COUNT OF LGBTQ+ IDENTITIES",
            font=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', size=18, color='#000000', weight=900),
            x=0.02,
            y=0.95
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        
        xaxis=dict(
            title=dict(text='LGBTQ+ IDENTITY', font=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', weight='bold', size=14)),
            tickmode='array',
            tickvals=list(range(len(df_plot))),
            ticktext=[l.upper() for l in df_plot['Final_Label'].tolist()],
            tickfont=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', weight='bold', size=11),
            showgrid=False,
            showline=True,
            linecolor='#000000',
            linewidth=3
        ),
        yaxis=dict(
            title=dict(text='NUMBER OF CHARACTERS', font=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', weight='bold', size=14)),
            showgrid=False,
            showline=True,
            linecolor='#000000',
            linewidth=3,
            zeroline=False,
            tickmode='array',
            tickvals=[(c / ITEMS_PER_ROW) * VERTICAL_STEP for c in range(0, int(max_count) + 25, 20)],
            ticktext=[str(c) for c in range(0, int(max_count) + 25, 20)],
            tickfont=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', weight='bold', size=12),
            range=[-1, max_y_val + 3]
        ),
        hoverlabel=dict(
            bgcolor='#ffffff',
            bordercolor='#000000',
            font=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', size=13, color='#000000', weight='bold')
        ),
        height=750,
        margin=dict(l=65, r=50, t=90, b=60)
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.write_html(OUTPUT_FILE, config={'displayModeBar': False})
    print(f"Vector pictogram chart successfully saved to: {os.path.abspath(OUTPUT_FILE)}")
    fig.show()

if __name__ == "__main__":
    generate_chart()