import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from collections import Counter

# 1. Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else '.'
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'final_labeled_data.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'plots')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'identity_intersection_chord.html')

if not os.path.exists(INPUT_FILE):
    INPUT_FILE = 'final_labeled_data.csv'

# Load data
df = pd.read_csv(INPUT_FILE)

# 2. Extract Labels and Separate Single, Pair, and Multi-Labels
df_clean = df.dropna(subset=['Final_Label']).copy()

all_labels = set()
single_label_counts = Counter()
pair_connections = Counter()
high_intersection_characters = []

for idx, row in df_clean.iterrows():
    labels = sorted([l.strip() for l in row['Final_Label'].split(';')])
    for l in labels:
        all_labels.add(l)
    
    if len(labels) == 1:
        single_label_counts[labels[0]] += 1
    elif len(labels) == 2:
        pair_connections[tuple(labels)] += 1
    else:
        high_intersection_characters.append({
            'name': row.get('Character', 'Unknown'),
            'labels': labels
        })

label_list = sorted(list(all_labels))
num_labels = len(label_list)

# 3. High-Contrast Pride Colors Map
COLOR_MAP = {
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

# 4. Circular layout configuration for outer nodes
angles = np.linspace(0, 2 * np.pi, num_labels, endpoint=False)
label_positions = {label_list[i]: (np.cos(angles[i]), np.sin(angles[i])) for i in range(num_labels)}

fig = go.Figure()

# 5. One thick loop per category for Single-Label characters
for l, count in single_label_counts.items():
    lx, ly = label_positions[l]
    label_idx = label_list.index(l)
    angle = angles[label_idx]
    
    r = 0.15
    cx = (1 - r) * lx
    cy = (1 - r) * ly
    
    line_width = int(2 + np.log1p(count) * 3)
    
    t = np.linspace(angle, angle + 2 * np.pi, 50)
    curve_x = cx + r * np.cos(t)
    curve_y = cy + r * np.sin(t)
    
    fig.add_trace(go.Scatter(
        x=curve_x, y=curve_y,
        mode='lines',
        line=dict(color=COLOR_MAP.get(l, '#94a3b8'), width=line_width),
        opacity=0.4,
        hoverinfo='text',
        text=f"Category: {l}<br>Exclusive Characters: {int(count)}",
        showlegend=False
    ))

# 6. Aggregated 2-Label lines
for (l1, l2), count in pair_connections.items():
    x0, y0 = label_positions[l1]
    x1, y1 = label_positions[l2]
    
    pair_width = int(1 + np.log1p(count) * 3)
    
    t = np.linspace(0, 1, 40)
    cx = (1-t)**2 * x0 + 2*(1-t)*t * 0 + t**2 * x1
    cy = (1-t)**2 * y0 + 2*(1-t)*t * 0 + t**2 * y1
    
    fig.add_trace(go.Scatter(
        x=cx, y=cy,
        mode='lines',
        line=dict(color=COLOR_MAP.get(l1, '#94a3b8'), width=pair_width),
        opacity=0.35,
        hoverinfo='text',
        text=f"Connection: {l1} ↔ {l2}<br>Shared Characters: {int(count)}",
        showlegend=False
    ))

# 7. 3+ Labels: Equidistant circular spread on inner ring
high_intersec_count = len(high_intersection_characters)

for idx_high, char in enumerate(high_intersection_characters):
    custom_angle = (2 * np.pi / high_intersec_count) * idx_high
    cx = 0.65 * np.cos(custom_angle)
    cy = 0.65 * np.sin(custom_angle)
    
    for l in char['labels']:
        lx, ly = label_positions[l]
        fig.add_trace(go.Scatter(
            x=[cx, lx], y=[cy, ly],
            mode='lines',
            line=dict(color=COLOR_MAP.get(l, '#94a3b8'), width=1),
            opacity=0.20,
            hoverinfo='skip',
            showlegend=False
        ))
        
    fig.add_trace(go.Scatter(
        x=[cx], y=[cy],
        mode='markers',
        marker=dict(size=7, color='black'),
        hoverinfo='text',
        text=f"Character: {char['name']}<br>Identities: {', '.join(char['labels'])}",
        showlegend=False
    ))

# 8. Large outer category nodes (Hover skipped)
outer_x = [label_positions[l][0] for l in label_list]
outer_y = [label_positions[l][1] for l in label_list]
outer_colors = [COLOR_MAP.get(l, '#94a3b8') for l in label_list]

fig.add_trace(go.Scatter(
    x=outer_x, y=outer_y,
    mode='markers+text',
    marker=dict(
        size=26,
        color=outer_colors,
        line=dict(color='black', width=1.5)
    ),
    text=label_list,
    textposition="top center",
    hoverinfo='skip',
    showlegend=False
))

# 9. Layout settings
fig.update_layout(
    title_text="INTERSECTIONAL CHORD NETWORK: Pride Flag Color Palette",
    title_font=dict(size=16, family="Arial", color="black"),
    width=900,
    height=900,
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.4, 1.4]),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.4, 1.4]),
    plot_bgcolor='white'
)

# Save and open
os.makedirs(OUTPUT_DIR, exist_ok=True)
fig.write_html(OUTPUT_FILE)
print(f"Chord network updated and saved: {os.path.abspath(OUTPUT_FILE)}")
fig.show()