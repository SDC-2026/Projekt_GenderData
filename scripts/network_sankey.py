import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

print("SCRIPT RUNNING...")

# Path configuration for runtime flexibility across different IDEs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else '.'
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'final_labeled_data.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'docs', 'plots')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'sankey_diagram.html')

# Fallback to local directory if the file is missing from the processed folder
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = 'final_labeled_data.csv'

# Distinct color palette restored to HEX for dynamic alpha control
COLOR_MAP = {
    # Major Networks
    'Netflix': '#e50914',
    'HBO': '#000000',
    'HBO Max': '#4f46e5',
    'Max': '#4f46e5',
    'Disney+': '#0063e5',
    'Hulu': '#10b981',
    'Amazon Prime': '#ff9900',
    'Amazon Prime Video': '#ff9900',
    'The CW': '#15803d',
    'Apple TV+': '#6b7280',
    'Paramount+': '#00b2ff',
    'One 31': '#fcd34d',
    'Peacock': '#0d9488',
    'BBC': '#991b1b',
    'ABC': '#f87171',
    'NBC': '#06b6d4',
    'CBS': '#2563eb',
    'Fox': '#475569',
    'Starz': '#881337',
    'Showtime': '#ef4444',
    'Other Networks': '#a1a1aa',

    # Identity Categories
    'Lesbian': '#d62900',
    'Gay': '#008026',
    'Bisexual & Pansexual': '#ff1b8d',
    'Trans & Non-Binary': '#5bcefa',
    'Asexual': '#7400b8',
    'Queer / Questioning': '#4d004d',
    'Unlabeled / Pending': '#cbd5e1',
    'Other / Unknown': '#94a3b8'
}

def hex_to_rgba(hex_str, alpha=0.35):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def simplify_identity(label):
    if pd.isna(label):
        return 'Unlabeled / Pending'
    label_clean = str(label).strip()
    parts = [p.strip().lower() for p in label_clean.split(';')]
    
    for part in parts:
        if any(x in part for x in ['transgender', 'trans', 'non-binary', 'genderfluid', 'intersex']):
            return 'Trans & Non-Binary'
            
    is_bi_pan, is_lesbian, is_gay, is_asexual, is_queer = False, False, False, False, False
    
    for part in parts:
        if any(x in part for x in ['bisexual', 'pansexual', 'demisexual', 'fluid']):
            is_bi_pan = True
        elif 'lesbian' in part:
            is_lesbian = True
        elif 'gay' in part:
            is_gay = True
        elif 'asexual' in part:
            is_asexual = True
        elif 'queer' in part or 'questioning' in part:
            is_queer = True
            
    if is_bi_pan: return 'Bisexual & Pansexual'
    if is_lesbian: return 'Lesbian'
    if is_gay: return 'Gay'
    if is_asexual: return 'Asexual'
    if is_queer: return 'Queer / Questioning'
        
    return 'Other / Unknown'

def generate_sankey():
    print("=== Starting Sankey Diagram Generation ===")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Data file not found at: {os.path.abspath(INPUT_FILE)}")
        return

    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} records for visualization analysis.")
    
    df['Simplified_Label'] = df['Final_Label'].apply(simplify_identity)
    
    top_n = 10
    top_networks = df['Network'].value_counts().nlargest(top_n).index
    df['Network_Grouped'] = df['Network'].apply(lambda x: x if x in top_networks else 'Other Networks')

    # 1. Aggregate and sort flows alphabetically to ensure stable node mapping
    flows = df.groupby(['Network_Grouped', 'Simplified_Label']).size().reset_index(name='value')
    flows = flows.sort_values(by=['Network_Grouped', 'Simplified_Label'])
    flows.columns = ['source_label', 'target_label', 'value']

    # 2. Extract stable unique nodes sorted alphabetically
    # This gives Plotly a predictable index while letting the layout algorithm balance sizes
    sources_order = sorted(flows['source_label'].unique())
    targets_order = sorted(flows['target_label'].unique())
    all_nodes = sources_order + targets_order

    node_indices = {node: idx for idx, node in enumerate(all_nodes)}

    sources = flows['source_label'].map(node_indices).tolist()
    targets = flows['target_label'].map(node_indices).tolist()
    values = flows['value'].tolist()

    sorted_keys = sorted(COLOR_MAP.keys(), key=len, reverse=True)

    node_colors = []
    for node in all_nodes:
        base_color = '#94a3b8'
        for key in sorted_keys:
            if key.lower() in node.lower():
                base_color = COLOR_MAP[key]
                break
        node_colors.append(hex_to_rgba(base_color, alpha=0.85))

    link_colors = []
    for _, row in flows.iterrows():
        source_node = row['source_label']
        base_color = '#94a3b8'
        for key in sorted_keys:
            if key.lower() in source_node.lower():
                base_color = COLOR_MAP[key]
                break
        link_colors.append(hex_to_rgba(base_color, alpha=0.35))

    # Construct interactive visualization utilizing dynamic balancing
    fig = go.Figure(data=[go.Sankey(
        valueformat="d",
        arrangement='snap',  # Restores default dynamic calculation to prevent overlaps
        textfont=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', size=13, color='#000000', weight='bold'),
        node=dict(
            pad=22,          # Increased padding to strictly separate block spaces
            thickness=25,
            line=dict(color="#000000", width=3),
            label=[label.upper() for label in all_nodes],
            color=node_colors,
            hovertemplate='<b>CATEGORY: %{label}</b><br>TOTAL CONNECTIONS: %{value}<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            line=dict(color="rgba(0,0,0,0.1)", width=1),
            hovertemplate='<b>FLOW: %{source.label} → %{target.label}</b><br>TOTAL CHARACTERS: %{value}<extra></extra>'
        )
    )])

    fig.update_layout(
        title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', size=12, color='#000000'),
        hoverlabel=dict(bgcolor='#ffffff', bordercolor='#000000', font=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', size=13, color='#000000', weight='bold')),
        height=700,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.write_html(
        OUTPUT_FILE, 
        config={'displayModeBar': False},
        include_plotlyjs='cdn',
        full_html=False
    )
    print(f"Sankey diagram successfully saved to: {os.path.abspath(OUTPUT_FILE)}")
    fig.show()  # Local browser preview call retained

if __name__ == "__main__":
    generate_sankey()