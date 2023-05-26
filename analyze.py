import json
import pandas as pd
import matplotlib.pyplot as plt
from helpers import from_json
import matplotlib.patches as mpatches
import numpy as np


def generate_histogram():
    # Load data from json file
    data = from_json("data.json")

    # Convert data to DataFrame
    df = pd.DataFrame(
        [
            {
                "title": pr.token_counts.title,
                "body": pr.token_counts.body,
                "diff": pr.token_counts.diff,
            }
            for pr in data
        ]
    )

    # Compute total tokens
    df["total_tokens"] = df["title"] + df["body"] + df["diff"]

    # Define bins logarithmically
    bins = np.logspace(
        np.log10(df["total_tokens"].min() + 1),
        np.log10(df["total_tokens"].max() + 1),
        num=50,
    )

    # Calculate quantiles
    q50 = df["total_tokens"].quantile(0.50)
    q90 = df["total_tokens"].quantile(0.90)
    q95 = df["total_tokens"].quantile(0.95)
    q99 = df["total_tokens"].quantile(0.99)

    # Define colors
    colors = ["blue", "green", "yellow", "red"]

    # Generate histogram and color by quantile
    n, bins, patches = plt.hist(df["total_tokens"], bins=bins, edgecolor="black")

    for patch, right_side_bin in zip(patches, bins[1:]):
        if right_side_bin < q50:
            patch.set_facecolor(colors[0])
        elif right_side_bin < q90:
            patch.set_facecolor(colors[1])
        elif right_side_bin < q95:
            patch.set_facecolor(colors[2])
        elif right_side_bin < q99:
            patch.set_facecolor(colors[3])

    # Create legend
    labels = [
        "<=50th percentile",
        "<=90th percentile",
        "<=95th percentile",
        "<=99th percentile",
    ]
    patches = [
        mpatches.Patch(color=color, label=label) for color, label in zip(colors, labels)
    ]
    plt.legend(handles=patches)

    # Add vertical lines and annotations for the quantiles
    quantiles = [q50, q90, q95, q99]
    for q, color, label in zip(quantiles, colors, labels):
        plt.axvline(q, color=color, linestyle="dashed", linewidth=1)
        plt.text(
            q,
            plt.gca().get_ylim()[1],
            f"{label}: {q:.0f}",
            rotation=90,
            verticalalignment="top",
        )

    plt.title("Total tokens in Pull Requests")
    plt.xlabel("Number of tokens")
    plt.ylabel("Number of pull requests")

    # Set x-axis to logarithmic scale
    plt.xscale("log")

    plt.show()


if __name__ == "__main__":
    generate_histogram()
