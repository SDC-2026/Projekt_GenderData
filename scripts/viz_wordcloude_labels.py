from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Basisordner
BASE_DIR = Path(__file__).resolve().parent

# CSV laden
csv_path = BASE_DIR.parent / "data" / "processed" / "final_labeled_data.csv"
df = pd.read_csv(csv_path)

# Alle Labels sammeln
all_labels = []

for labels in df["Final_Label"].dropna():
    split_labels = labels.split(";")

    for label in split_labels:
        cleaned = label.strip()

        if cleaned != "":
            all_labels.append(cleaned)

# Häufigkeiten zählen
label_freq = pd.Series(all_labels).value_counts().to_dict()

# Wordcloud
wordcloud = WordCloud(
    width=1200,
    height=600,
    background_color="white",
    colormap="viridis"
).generate_from_frequencies(label_freq)

# Plot
plt.figure(figsize=(16, 8))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Wordcloud der einzelnen Labels", fontsize=20)

# Speichern
save_path = BASE_DIR.parent / "visualizations" / "wordcloud_labels_clean.png"

plt.savefig(save_path, bbox_inches="tight", dpi=300)

print(f"Gespeichert unter: {save_path}")

plt.show()