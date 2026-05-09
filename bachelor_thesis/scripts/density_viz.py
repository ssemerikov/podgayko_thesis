"""
Kernel density estimation visualization for VOSViewer keyword map.

Produces media/fig_density.png — a 2D Gaussian KDE heatmap of keyword
positions weighted by occurrence count, with keyword labels overlaid.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from scipy.stats import gaussian_kde

from wos_parser import load_vosviewer_map, MEDIA_DIR, setup_matplotlib


def main() -> None:
    setup_matplotlib()

    # ── Load VOSViewer keyword data ──────────────────────────────────────────
    df = load_vosviewer_map()

    x = df["x"].values
    y = df["y"].values
    weights = df["occurrences"].values.astype(float)
    labels = df["label"].values

    # ── 2D Gaussian KDE weighted by occurrences ─────────────────────────────
    positions = np.vstack([x, y])
    kde = gaussian_kde(positions, weights=weights)

    # Evaluation grid with padding
    pad_x = (x.max() - x.min()) * 0.10
    pad_y = (y.max() - y.min()) * 0.10
    x_min, x_max = x.min() - pad_x, x.max() + pad_x
    y_min, y_max = y.min() - pad_y, y.max() + pad_y

    grid_size = 300
    xi = np.linspace(x_min, x_max, grid_size)
    yi = np.linspace(y_min, y_max, grid_size)
    Xi, Yi = np.meshgrid(xi, yi)
    grid_coords = np.vstack([Xi.ravel(), Yi.ravel()])
    Zi = kde(grid_coords).reshape(Xi.shape)

    # ── Visualization ────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 8))

    # Filled contour with ~20 levels
    levels = 20
    cf = ax.contourf(Xi, Yi, Zi, levels=levels, cmap="YlOrRd")
    cbar = fig.colorbar(cf, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label("Щільність", fontsize=12)

    # Overlay keyword labels with white stroke outline for readability
    stroke = [
        pe.withStroke(linewidth=2.5, foreground="white"),
    ]
    for lbl, lx, ly in zip(labels, x, y):
        ax.text(
            lx, ly, lbl,
            fontsize=8,
            ha="center",
            va="center",
            fontweight="bold",
            color="black",
            path_effects=stroke,
        )

    ax.set_title("Карта щільності ключових слів", fontsize=14, fontweight="bold")
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.tick_params(axis="both", which="both", length=0, labelbottom=False, labelleft=False)

    fig.tight_layout()

    # ── Save ─────────────────────────────────────────────────────────────────
    out_path = MEDIA_DIR / "fig_density.pdf"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
