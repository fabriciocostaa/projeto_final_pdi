from __future__ import annotations

from itertools import compress

import cv2
import numpy as np
from sklearn.cluster import KMeans


class DominantColors:
    def __init__(self, image: np.ndarray, clusters: int = 3) -> None:
        self.clusters = clusters
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.image = img.reshape((img.shape[0] * img.shape[1], 3))

        kmeans = KMeans(n_clusters=self.clusters)
        kmeans.fit(self.image)

        self.colors = kmeans.cluster_centers_
        self.labels = kmeans.labels_

    @staticmethod
    def rgb_to_hex(rgb: np.ndarray | list[int] | tuple[int, int, int]) -> str:
        return "#%02x%02x%02x" % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

    def get_histogram(self) -> tuple[list[np.ndarray], np.ndarray]:
        num_labels = np.arange(0, self.clusters + 1)
        hist, _ = np.histogram(self.labels, bins=num_labels)
        hist = hist.astype("float")
        hist /= hist.sum()

        colors = self.colors[(-hist).argsort()]
        hist = hist[(-hist).argsort()]

        for i in range(self.clusters):
            colors[i] = colors[i].astype(int)

        # Remove pixels que vieram do fundo mascarado.
        color_filter = [colors[i][2] < 250 and colors[i][0] > 10 for i in range(self.clusters)]
        colors = list(compress(colors, color_filter))
        filtered_hist = hist[color_filter]

        return colors, filtered_hist

    def plot_histogram(self) -> list[np.ndarray]:
        import matplotlib.pyplot as plt

        colors, hist = self.get_histogram()
        chart = np.zeros((50, 500, 3), np.uint8)
        start = 0

        for i, color in enumerate(colors):
            end = start + hist[i] * 500
            r, g, b = color
            cv2.rectangle(chart, (int(start), 0), (int(end), 50), (r, g, b), -1)
            start = end

        plt.figure()
        plt.axis("off")
        plt.imshow(chart)
        plt.show()

        return colors
