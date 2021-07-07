from .saccades import identify_by_velocity as identify_saccades_by_velocity
from .saccades import kmeans_identification as identify_saccades_by_kmeans


__all__ = [
    'identify_saccades_by_velocity',
    'identify_saccades_by_kmeans',
]
