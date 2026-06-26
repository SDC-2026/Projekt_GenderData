import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from collections import Counter

# 1. Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else '.'
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'final_labeled_data.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'plots')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'intersectional_identity_network.html')

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

# 3. Dynamic Linear Scaling for Line Widths (Honest proportional mapping)
all_counts = list(single_label_counts.values()) + list(pair_connections.values())
max_count = max(all_counts) if all_counts else 1

# Enforce base baseline width to preserve visibility of smaller categories
MIN_WIDTH = 5
MAX_WIDTH = 20

def get_linear_width(count):
    # Proportional mapping to maintain exact data scale ratios
    return MIN_WIDTH + (count / max_count) * (MAX_WIDTH - MIN_WIDTH)

# 4. High-Contrast Pride Colors Map (HEX)
COLOR_MAP = {
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

def hex_to_rgba(hex_str, alpha=0.35):
    hex_str = hex_str.lstrip('#')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

# 5. Circular layout configuration for outer nodes
angles = np.linspace(0, 2 * np.pi, num_labels, endpoint=False)
label_positions = {label_list[i]: (np.cos(angles[i]), np.sin(angles[i])) for i in range(num_labels)}

fig = go.Figure()

# 6. One loop per category for Single-Label characters (Linear width applied)
for l, count in single_label_counts.items():
    lx, ly = label_positions[l]
    label_idx = label_list.index(l)
    angle = angles[label_idx]
    
    r = 0.15
    cx = (1 - r) * lx
    cy = (1 - r) * ly
    
    line_width = get_linear_width(count)
    
    t = np.linspace(angle, angle + 2 * np.pi, 50)
    curve_x = cx + r * np.cos(t)
    curve_y = cy + r * np.sin(t)
    
    base_color = COLOR_MAP.get(l, '#94a3b8')
    fig.add_trace(go.Scatter(
        x=curve_x, y=curve_y,
        mode='lines',
        line=dict(color=hex_to_rgba(base_color, alpha=0.35), width=line_width),
        hoverinfo='text',
        text=f"<b>CATEGORY: {l.upper()}</b><br>EXCLUSIVE CHARACTERS: {int(count)}",
        showlegend=False
    ))

# 7. Aggregated 2-Label lines (Linear width applied)
for (l1, l2), count in pair_connections.items():
    x0, y0 = label_positions[l1]
    x1, y1 = label_positions[l2]
    
    pair_width = get_linear_width(count)
    
    t = np.linspace(0, 1, 40)
    cx = (1-t)**2 * x0 + 2*(1-t)*t * 0 + t**2 * x1
    cy = (1-t)**2 * y0 + 2*(1-t)*t * 0 + t**2 * y1
    
    base_color = COLOR_MAP.get(l1, '#94a3b8')
    fig.add_trace(go.Scatter(
        x=cx, y=cy,
        mode='lines',
        line=dict(color=hex_to_rgba(base_color, alpha=0.35), width=pair_width),
        hoverinfo='text',
        text=f"<b>CONNECTION: {l1.upper()} ↔ {l2.upper()}</b><br>SHARED CHARACTERS: {int(count)}",
        showlegend=False
    ))

# 8. 3+ Labels: Equidistant circular spread on inner ring (Fine 20% opacity)
high_intersec_count = len(high_intersection_characters)

for idx_high, char in enumerate(high_intersection_characters):
    custom_angle = (2 * np.pi / high_intersec_count) * idx_high
    cx = 0.65 * np.cos(custom_angle)
    cy = 0.65 * np.sin(custom_angle)
    
    for l in char['labels']:
        lx, ly = label_positions[l]
        base_color = COLOR_MAP.get(l, '#94a3b8')
        fig.add_trace(go.Scatter(
            x=[cx, lx], y=[cy, ly],
            mode='lines',
            line=dict(color=hex_to_rgba(base_color, alpha=0.20), width=1.5),
            hoverinfo='skip',
            showlegend=False
        ))
        
    fig.add_trace(go.Scatter(
        x=[cx], y=[cy],
        mode='markers',
        marker=dict(size=8, color='#000000', line=dict(color='#ffffff', width=1)),
        hoverinfo='text',
        text=f"<b>CHARACTER: {char['name'].upper()}</b><br>IDENTITIES: {', '.join(char['labels']).upper()}",
        showlegend=False
    ))

# 9. Large outer category nodes (Solid 85% opacity, thick borders, ALL-CAPS labels)
outer_x = [label_positions[l][0] for l in label_list]
outer_y = [label_positions[l][1] for l in label_list]
outer_colors = [hex_to_rgba(COLOR_MAP.get(l, '#94a3b8'), alpha=0.85) for l in label_list]
outer_labels_caps = [l.upper() for l in label_list]

fig.add_trace(go.Scatter(
    x=outer_x, y=outer_y,
    mode='markers+text',
    marker=dict(
        size=26,
        color=outer_colors,
        line=dict(color='#000000', width=3)
    ),
    text=outer_labels_caps,
    textposition="top center",
    textfont=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', size=11, color='#000000', weight='bold'),
    hoverinfo='skip',
    showlegend=False
))

# 10. Layout settings with strict canvas centering and squaring
fig.update_layout(
    title=dict(
        text="INTERSECTIONAL IDENTITY NETWORK",
        font=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', size=18, color='#000000', weight=900),
        x=0.5,           
        xanchor='center' 
    ),
    width=900,
    height=900,
    xaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showticklabels=False, 
        range=[-1.4, 1.4],
        domain=[0.05, 0.95] 
    ),
    yaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showticklabels=False, 
        range=[-1.4, 1.4],
        domain=[0.05, 0.95], 
        scaleanchor="x",     
        scaleratio=1
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
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
    margin=dict(l=0, r=0, t=80, b=0), 
    autosize=False
)

# Save and open
os.makedirs(OUTPUT_DIR, exist_ok=True)
fig.write_html(OUTPUT_FILE, config={'displayModeBar': False})
print(f"Network updated and successfully saved to: {os.path.abspath(OUTPUT_FILE)}")
fig.show()