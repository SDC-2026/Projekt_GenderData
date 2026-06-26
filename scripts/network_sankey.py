import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# Path configuration for runtime flexibility across different IDEs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else '.'
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'final_labeled_data.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'plots')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'sankey_diagram.html')

# Fallback to local directory if the file is missing from the processed folder
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = 'final_labeled_data.csv'

# Distinct color palette restored to HEX for dynamic alpha control
COLOR_MAP = {
    # Platform Types (Gatekeepers)
    'Streaming': '#312e81',
    'Cable': '#451a03',
    'Broadcast': '#064e3b',
    'Other / Independent': '#1e293b',

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
    """
    Converts hexadecimal color (HEX) to RGBA format with specified opacity.
    """
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def map_network_to_platform(network):
    if pd.isna(network):
        return 'Unknown'
    network_clean = str(network).strip()
    
    streaming = [
        'Netflix', 'Apple TV+', 'Amazon Prime', 'Amazon Prime Video', 'Disney+', 
        'Hulu', 'HBO Max', 'Max', 'Paramount+', 'Peacock', 'YouTube', 'Globoplay', 
        'Rakuten Viki', 'Tencent Video', 'Line TV', 'Watcha', 'Crave', 'Stan', 
        'CBS All Access', 'Atresplayer Premium', 'Viki, WeTV, AbemaTV', 'TV Asahi, Viki', 
        'Fuji Television, Viki, GagaOOLala', 'Rakuten TV, Viki, GagaOOLala'
    ]
    cable = [
        'HBO', 'Showtime', 'Starz', 'FX', 'Channel 4', 'Sky Atlantic', 'AMC', 
        'Syfy', 'USA Syfy', 'Sky Atlantic, Starz', 'HBO; Sky Atlantic'
    ]
    broadcast = [
        'Fox', 'ABC', 'NBC', 'CBS', 'The CW', 'BBC', 'ZDF', 'ITV', 'Rai 1', 
        'NHK General TV', 'Global', 'Freeform', 'BBC One', 'BBC One HBO', 
        'BBC One, HBO', 'BBC iPlayer', 'Alibi', 'Global Network', 'Tencent Video, Line TV',
        'One 31; Line TV', 'One 31', 'One 31 iQIYI', 'TV Tokyo', 'TV Tokyo, Tencent Video, Crunchyroll',
        'HRT 1, HRTi, YouTube', 'TV Asahi'
    ]
    
    for s in streaming:
        if s.lower() in network_clean.lower():
            return 'Streaming'
    for c in cable:
        if c.lower() in network_clean.lower():
            return 'Cable'
    for b in broadcast:
        if b.lower() in network_clean.lower():
            return 'Broadcast'
            
    return 'Other / Independent'

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
    df['Platform_Type'] = df['Network'].apply(map_network_to_platform)
    
    top_n = 10
    top_networks = df['Network'].value_counts().nlargest(top_n).index
    df['Network_Grouped'] = df['Network'].apply(lambda x: x if x in top_networks else 'Other Networks')

    # Define Flow A: Platform -> Network
    flow_a = df.groupby(['Platform_Type', 'Network_Grouped']).size().reset_index(name='value')
    flow_a.columns = ['source_label', 'target_label', 'value']

    # Define Flow B: Network -> Simplified Identity
    flow_b = df.groupby(['Network_Grouped', 'Simplified_Label']).size().reset_index(name='value')
    flow_b.columns = ['source_label', 'target_label', 'value']

    flows = pd.concat([flow_a, flow_b], ignore_index=True)

    all_nodes = list(pd.concat([flows['source_label'], flows['target_label']]).unique())
    node_indices = {node: idx for idx, node in enumerate(all_nodes)}

    sources = flows['source_label'].map(node_indices).tolist()
    targets = flows['target_label'].map(node_indices).tolist()
    values = flows['value'].tolist()

    sorted_keys = sorted(COLOR_MAP.keys(), key=len, reverse=True)

    # Nodes receive a higher opacity (0.85) for solid neobrutalist structure
    node_colors = []
    for node in all_nodes:
        base_color = '#94a3b8'
        for key in sorted_keys:
            if key.lower() in node.lower():
                base_color = COLOR_MAP[key]
                break
        node_colors.append(hex_to_rgba(base_color, alpha=0.85))

    # Links receive a soft opacity (0.35) to remain beautifully semi-transparent
    link_colors = []
    for _, row in flows.iterrows():
        source_node = row['source_label']
        base_color = '#94a3b8'
        for key in sorted_keys:
            if key.lower() in source_node.lower():
                base_color = COLOR_MAP[key]
                break
        link_colors.append(hex_to_rgba(base_color, alpha=0.35))

    # Build interactive Sankey visualization
    fig = go.Figure(data=[go.Sankey(
        valueformat="d",
        textfont=dict(family='"Helvetica Neue", Helvetica, Arial, sans-serif', size=13, color='#000000', weight='bold'),
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="#000000", width=3),  # Bold neobrutalist outline
            label=[label.upper() for label in all_nodes],
            color=node_colors,
            hovertemplate='<b>CATEGORY: %{label}</b><br>TOTAL CONNECTIONS: %{value}<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            line=dict(color="rgba(0,0,0,0.1)", width=1),  # Discrete separating border
            # Fixed: Kept the exact dynamic arrow syntax and renamed metric line to TOTAL CHARACTERS:
            hovertemplate='<b>FLOW: %{source.label} → %{target.label}</b><br>TOTAL CHARACTERS: %{value}<extra></extra>'
        )
    )])

    # Configure layout with transparent background and crisp fonts
    fig.update_layout(
        title=dict(
            text="REPRESENTATION FLOW: FROM DISTRIBUTOR TO QUEER IDENTITY",
            font=dict(size=18, color='#000000', weight=900),
            x=0.02,
            y=0.95
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family='"Helvetica Neue", Helvetica, Arial, sans-serif',
            size=12,
            color='#000000'
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
        height=700,
        margin=dict(l=20, r=20, t=80, b=20)
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.write_html(OUTPUT_FILE, config={'displayModeBar': False})
    print(f"Sankey diagram successfully saved to: {os.path.abspath(OUTPUT_FILE)}")
    fig.show()

if __name__ == "__main__":
    generate_sankey()