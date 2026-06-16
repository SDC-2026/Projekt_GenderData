import pandas as pd
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

# Distinct color palette based on corporate brands and Pride flags
COLOR_MAP = {
    # Platform Types (Gatekeepers) - Using deep, rich, distinct structural tones
    'Streaming': '#312e81',            # Deep indigo
    'Cable': '#451a03',                # Dark chocolate brown (no overlap with Amazon)
    'Broadcast': '#064e3b',            # Very dark forest green (no overlap with Hulu)
    'Other / Independent': '#1e293b',  # Dark slate gray

    # Major Networks (Official brand colors / highly distinct alternatives)
    'Netflix': '#e50914',               # Netflix red
    'HBO': '#000000',                   # Pure black HBO
    'HBO Max': '#4f46e5',               # Royal indigo Max
    'Max': '#4f46e5',                   # Royal indigo Max
    'Disney+': '#0063e5',               # Bright, classic Disney royal blue (no longer too dark)
    'Hulu': '#10b981',                  # Bright green Hulu (clearly distinct from dark Broadcast green)
    'Amazon Prime': '#ff9900',          # Vibrant orange Amazon Prime
    'Amazon Prime Video': '#ff9900',    # Vibrant orange Amazon Prime
    'The CW': '#15803d',                # Mid-leaf green (clearly distinct from Hulu)
    'Apple TV+': '#6b7280',             # Cool mid-gray Apple
    'Paramount+': '#00b2ff',            # Electric cyan blue Paramount
    'One 31': '#fcd34d',                # Light pastel yellow-gold (no overlap with Amazon's orange)
    'Peacock': '#0d9488',               # Peacock teal green
    'BBC': '#991b1b',                   # Deep crimson red (distinct from Netflix red)
    'ABC': '#f87171',                   # Coral red ABC
    'NBC': '#06b6d4',                   # Cyan NBC
    'CBS': '#2563eb',                   # Cobalt blue CBS
    'Fox': '#475569',                   # Slate-navy Fox
    'Starz': '#881337',                 # Deep burgundy Starz (no overlap with Amazon)
    'Showtime': '#ef4444',              # Scarlet red Showtime
    'Other Networks': '#a1a1aa',        # Warm neutral gray for remaining networks

    # Identity Categories (Pride flag colors)
    'Lesbian': '#ea580c',               # Warm orange-red (lesbian flag)
    'Gay': '#059669',                   # Emerald green (classic pride flag subset)
    'Bisexual & Pansexual': '#d946ef',  # Vibrant fuchsia (bisexual/pansexual flags)
    'Trans & Non-Binary': '#38bdf8',    # Sky blue (transgender flag)
    'Asexual': '#7c3aed',               # Violet (asexual flag)
    'Queer / Questioning': '#ec4899',    # Pink queer color
    'Unlabeled / Pending': '#cbd5e1',   # Light slate gray
    'Other / Unknown': '#94a3b8'        # Mid slate gray
}

def hex_to_rgba(hex_str, alpha=0.35):
    """
    Converts hexadecimal color (HEX) to RGBA format with specified opacity.
    This makes the paths (links) soft and semi-transparent.
    """
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def map_network_to_platform(network):
    """
    Classifies television networks into structural platform types (gatekeepers).
    """
    if pd.isna(network):
        return 'Unknown'
    
    network_clean = str(network).strip()
    
    # Lists for media platform classification
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
    
    # Substring check to correctly handle joint networks
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
    """
    Aggregates and simplifies complex, overlapping, and rare identities
    to prevent excessive categories on the chart.
    """
    if pd.isna(label):
        return 'Unlabeled / Pending'
    
    label_clean = str(label).strip()
    
    # Split multiple labels (e.g., "Gay; Bisexual; Queer")
    parts = [p.strip().lower() for p in label_clean.split(';')]
    
    # 1. Prioritize Gender Identity (transgender, non-binary)
    for part in parts:
        if any(x in part for x in ['transgender', 'trans', 'non-binary', 'genderfluid', 'intersex']):
            return 'Trans & Non-Binary'
            
    # Flag variables for sexual orientation categories
    is_bi_pan = False
    is_lesbian = False
    is_gay = False
    is_asexual = False
    is_queer = False
    
    # 2. Check keywords across all segments
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
            
    # Return strictly structured category
    if is_bi_pan:
        return 'Bisexual & Pansexual'
    if is_lesbian:
        return 'Lesbian'
    if is_gay:
        return 'Gay'
    if is_asexual:
        return 'Asexual'
    if is_queer:
        return 'Queer / Questioning'
        
    return 'Other / Unknown'

def generate_sankey():
    """
    Main workflow: load data, simplify categories, group networks,
    map flows, and build the interactive HTML Sankey diagram.
    """
    print("=== Starting Sankey Diagram Generation ===")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Data file not found at: {os.path.abspath(INPUT_FILE)}")
        return

    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} records for visualization analysis.")
    
    # Apply simplification to reduce category fragmentation
    df['Simplified_Label'] = df['Final_Label'].apply(simplify_identity)
    
    # Map networks to platform types
    df['Platform_Type'] = df['Network'].apply(map_network_to_platform)
    
    # Group rare networks to prevent chart overload (Top-10 + Others)
    top_n = 10
    top_networks = df['Network'].value_counts().nlargest(top_n).index
    df['Network_Grouped'] = df['Network'].apply(lambda x: x if x in top_networks else 'Other Networks')

    # Define Flow A: Platform -> Network
    flow_a = df.groupby(['Platform_Type', 'Network_Grouped']).size().reset_index(name='value')
    flow_a.columns = ['source_label', 'target_label', 'value']

    # Define Flow B: Network -> Simplified Identity
    flow_b = df.groupby(['Network_Grouped', 'Simplified_Label']).size().reset_index(name='value')
    flow_b.columns = ['source_label', 'target_label', 'value']

    # Merge flows into a single transition dataframe
    flows = pd.concat([flow_a, flow_b], ignore_index=True)

    # Node indexing (Plotly requires integer indices instead of string labels)
    all_nodes = list(pd.concat([flows['source_label'], flows['target_label']]).unique())
    node_indices = {node: idx for idx, node in enumerate(all_nodes)}

    sources = flows['source_label'].map(node_indices).tolist()
    targets = flows['target_label'].map(node_indices).tolist()
    values = flows['value'].tolist()

    # Sort keys by length descending to match longer strings first (e.g., 'HBO Max' before 'HBO')
    sorted_keys = sorted(COLOR_MAP.keys(), key=len, reverse=True)

    # Apply colors to diagram nodes with length-prioritized substring matching
    node_colors = []
    for node in all_nodes:
        color = '#94a3b8'  # Default fallback gray
        for key in sorted_keys:
            if key.lower() in node.lower():
                color = COLOR_MAP[key]
                break
        node_colors.append(color)

    # Generate colored paths (links) based on source node color with length-prioritized lookup
    link_colors = []
    for _, row in flows.iterrows():
        source_node = row['source_label']
        base_color = '#94a3b8'  # Default fallback gray
        for key in sorted_keys:
            if key.lower() in source_node.lower():
                base_color = COLOR_MAP[key]
                break
        link_colors.append(hex_to_rgba(base_color, alpha=0.35))

    # Build interactive Sankey visualization in Plotly
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=18,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors  # Apply generated colored paths
        )
    )])

    # Configure chart styling and margins
    fig.update_layout(
        title_text="Representation Flow: From Distributor to Queer Identity",
        font_size=12,
        height=700,
        margin=dict(l=15, r=15, t=50, b=15)
    )

    # Save result to plots directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.write_html(OUTPUT_FILE)
    print(f"Sankey diagram successfully saved to: {os.path.abspath(OUTPUT_FILE)}")
    
    # Automatically open browser preview
    fig.show()

if __name__ == "__main__":
    generate_sankey()