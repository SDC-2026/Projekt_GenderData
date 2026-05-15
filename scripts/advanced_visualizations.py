import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import squarify
import plotly.graph_objects as go


# =========================================================
# PATHS
# =========================================================

script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(script_path))

input_file = os.path.join(
    project_root,
    "data",
    "processed",
    "final_labeled_data.csv"
)

output_dir = os.path.join(
    project_root,
    "visualizations"
)

os.makedirs(output_dir, exist_ok=True)


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(input_file)

print("Columns found:")
print(df.columns.tolist())


# =========================================================
# DATA PREPARATION
# =========================================================

df["Year_Clean"] = (
    df["Year"]
    .astype(str)
    .str.extract(r"(\d{4})")
)

df["Year_Clean"] = pd.to_numeric(
    df["Year_Clean"],
    errors="coerce"
)

df_labels = df.copy()

df_labels["Final_Label"] = (
    df_labels["Final_Label"]
    .astype(str)
    .str.split(";")
)

df_labels = df_labels.explode("Final_Label")

df_labels["Final_Label"] = (
    df_labels["Final_Label"]
    .str.strip()
)

df_labels = df_labels[
    df_labels["Final_Label"] != "[MANUAL_REVIEW_REQUIRED]"
]

df_labels = df_labels.dropna(
    subset=["Year_Clean", "Final_Label"]
)

df_labels["Year_Clean"] = df_labels["Year_Clean"].astype(int)


# =========================================================
# 1. TREEMAP OVERVIEW
# =========================================================

identity_counts = df_labels["Final_Label"].value_counts()

# Colors for better readability
treemap_colors = [
    "#4E79A7",  # blue
    "#59A14F",  # green
    "#F28E2B",  # orange
    "#E15759",  # red
    "#76B7B2",  # teal
    "#B07AA1",  # purple
    "#EDC948",  # yellow
    "#9C755F",  # brown
    "#BAB0AC",  # gray
    "#FF9DA7",  # pink
]

labels = [
    f"{label}\n{count}"
    for label, count in identity_counts.items()
]

plt.figure(figsize=(16, 9))

squarify.plot(
    sizes=identity_counts.values,
    label=labels,
    color=treemap_colors[:len(identity_counts)],
    alpha=0.9,
    text_kwargs={
        "fontsize": 13,
        "fontweight": "bold",
        "color": "white"
    },
    bar_kwargs={
        "linewidth": 2,
        "edgecolor": "white"
    }
)

plt.title(
    "Treemap of LGBTQ+ Identity Representation",
    fontsize=22,
    fontweight="bold",
    pad=20
)

plt.axis("off")

treemap_path = os.path.join(
    output_dir,
    "treemap_identity_distribution.png"
)

plt.savefig(
    treemap_path,
    dpi=300,
    bbox_inches="tight",
    facecolor="white"
)

plt.close()

# =========================================================
# 2. STACKED BAR CHART OVER TIME
# =========================================================

year_identity_counts = (
    df_labels
    .groupby(["Year_Clean", "Final_Label"])
    .size()
    .unstack(fill_value=0)
)

plt.figure(figsize=(14, 8))

year_identity_counts.plot(
    kind="bar",
    stacked=True,
    figsize=(14, 8)
)

plt.title(
    "LGBTQ+ Identity Representation Over Time",
    fontsize=16
)

plt.xlabel("Year")
plt.ylabel("Number of Label Mentions")
plt.xticks(rotation=45)

plt.legend(
    title="Identity",
    bbox_to_anchor=(1.05, 1),
    loc="upper left"
)

plt.tight_layout()

stacked_path = os.path.join(
    output_dir,
    "stacked_bar_identity_over_time.png"
)

plt.savefig(
    stacked_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# =========================================================
# 3. LINE CHART OVER TIME
# =========================================================

plt.figure(figsize=(14, 8))

year_identity_counts.plot(
    kind="line",
    marker="o",
    figsize=(14, 8)
)

plt.title(
    "Development of LGBTQ+ Identity Representation Across Years",
    fontsize=16
)

plt.xlabel("Year")
plt.ylabel("Number of Label Mentions")
plt.xticks(rotation=45)

plt.legend(
    title="Identity",
    bbox_to_anchor=(1.05, 1),
    loc="upper left"
)

plt.tight_layout()

line_path = os.path.join(
    output_dir,
    "line_chart_identity_development.png"
)

plt.savefig(
    line_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# =========================================================
# 4. SANKEY DIAGRAM: YEAR TO IDENTITY
# =========================================================

sankey_data = (
    df_labels
    .groupby(["Year_Clean", "Final_Label"])
    .size()
    .reset_index(name="Count")
)

years = sorted(
    sankey_data["Year_Clean"]
    .dropna()
    .astype(int)
    .unique()
)

identities = sorted(
    sankey_data["Final_Label"]
    .dropna()
    .unique()
)

nodes = [str(year) for year in years] + identities

node_indices = {
    node: index
    for index, node in enumerate(nodes)
}

sources = []
targets = []
values = []

for _, row in sankey_data.iterrows():
    year = str(int(row["Year_Clean"]))
    identity = row["Final_Label"]

    sources.append(node_indices[year])
    targets.append(node_indices[identity])
    values.append(row["Count"])

fig = go.Figure(
    data=[
        go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(
                    width=0.5
                ),
                label=nodes
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values
            )
        )
    ]
)

fig.update_layout(
    title_text="Sankey Diagram: Year to LGBTQ+ Identity",
    font_size=11
)

sankey_path = os.path.join(
    output_dir,
    "sankey_year_to_identity.html"
)

fig.write_html(sankey_path)


# =========================================================
# SUMMARY
# =========================================================

print("\nAdvanced visualizations created:")
print(treemap_path)
print(stacked_path)
print(line_path)
print(sankey_path)