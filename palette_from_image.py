from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

def extract_palette(image_file, k=6, random_state=42):
    im = Image.open(image_file).convert("RGB")
    arr = np.array(im).reshape(-1, 3)
    n = min(25000, arr.shape[0])
    idx = np.random.default_rng(random_state).choice(arr.shape[0], size=n, replace=False)
    sample = arr[idx]
    km = KMeans(n_clusters=k, n_init=8, random_state=random_state).fit(sample)
    centers = km.cluster_centers_.astype(int)
    lum = (0.2126*centers[:,0] + 0.7152*centers[:,1] + 0.0722*centers[:,2])
    centers = centers[np.argsort(lum)]
    return ["#{:02X}{:02X}{:02X}".format(*c) for c in centers]
