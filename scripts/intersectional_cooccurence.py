import pandas as pd
import plotly.graph_objects as go
import os

# 1. Path configuration matching your directory structure
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "..", "data", "processed", "final_labeled_data.csv")

# Load data
df = pd.read_csv(csv_path)

# 2. Extract flows from primary to secondary labels
left_labels = ['Gay', 'Lesbian', 'Bisexual']
right_labels = ['Queer', 'Transgender', 'Non-binary', 'Pansexual', 'Genderfluid', 'Intersex']
all_nodes = left_labels + right_labels

# Create a mapping from label to index for Plotly
node_indices = {label: i for i, label in enumerate(all_nodes)}

# Color Configuration matching your project rules (Green for Gay)
colors_map = {
    'Gay': '#008026',         # Your specified Green for Gay
    'Lesbian': '#E65100',     # Lesbian Flag Orange
    'Bisexual': '#D60270',    # Bisexual Flag Magenta
    'Queer': '#7C3AED',       # Queer Purple
    'Transgender': '#5BCEFA', # Trans Light Blue
    'Non-binary': '#FFF430',  # Non-binary Yellow
    'Pansexual': '#FF1B8D',   # Pansexual Hot Pink
    'Genderfluid': '#B57EDC', # Genderfluid Lavender
    'Intersex': '#FFD800'     # Intersex Gold
}
node_colors = [colors_map[node] for node in all_nodes]

sources = []
targets = []
values = []
link_colors = []

# Count occurrences
flow_data = {}
for label_str in df['Final_Label']:
    labels = [l.strip() for l in label_str.split(';')]
    if len(labels) > 1:
        primaries = [l for l in labels if l in left_labels]
        secondaries = [l for l in labels if l in right_labels]
        
        for p in primaries:
            for s in secondaries:
                pair = (p, s)
                flow_data[pair] = flow_data.get(pair, 0) + 1

# Build Plotly lists and assign transparent flow colors matching the source node
for (p, s), weight in flow_data.items():
    sources.append(node_indices[p])
    targets.append(node_indices[s])
    values.append(int(weight))  # Keeps data values as integers
    
    # Convert hex to standard RGBA string with 0.35 opacity
    hex_color = colors_map[p].lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    link_colors.append(f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.35)')

# 3. Create the interactive Sankey diagram
fig = go.Figure(data=[go.Sankey(
    valueformat = "d", # Forces Plotly to display ALL hover values as integers without decimals
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 2),
      label = all_nodes,
      color = node_colors,
      hovertemplate = 'Kategorie: %{label}<br>Gesamtverbindungen: %{value}<extra></extra>'
    ),
    link = dict(
      source = sources,
      target = targets,
      value = values,
      color = link_colors,
      hovertemplate = 'Strom: %{source.label} → %{target.label}<br>Anzahl: %{value}<extra></extra>'
  ))])

# 4. Style formatting using integer values
fig.update_layout(
    title_text="SANKEY INTERACTIVE FLOW DIAGRAM (PRIDE COLORS)",
    title_font=dict(size=16, family="Arial", color="black"),
    font_size=12,
    width=1000,
    height=700
)

# 5. Automatically save and open in browser
output_html = os.path.join(script_dir, "sankey_interactive.html")
fig.write_html(output_html, auto_open=True)