"""Geometric operations for layout parsing."""

from __future__ import annotations

import numpy as np

from leapx.services.layout_parser.structures.bbox import BBox


def overlaps(
    bboxes1: np.ndarray | list[BBox],
    bboxes2: np.ndarray | list[BBox],
) -> np.ndarray:
    """
    Compute overlap matrix between two sets of bounding boxes.

    Calculates how much each bbox in bboxes1 overlaps with each bbox in bboxes2,
    normalized by the area of bboxes1. This is a vectorized implementation
    adapted from Luminoth source code.

    Args:
        bboxes1: Array of shape (n1, 4) or list of BBox objects
                 Each row is [x0, y0, x2, y2]
        bboxes2: Array of shape (n2, 4) or list of BBox objects
                 Each row is [x0, y0, x2, y2]

    Returns:
        Matrix M of shape (n1, n2) where:
            M[i,j] = intersection_area(bboxes1[i], bboxes2[j]) / area(bboxes1[i])

    Example:
        >>> bbox1 = np.array([[0, 0, 10, 10]])  # Area = 121
        >>> bbox2 = np.array([[5, 5, 15, 15]])  # Overlaps with bbox1
        >>> overlaps(bbox1, bbox2)
        array([[0.21487603]])  # ~21% overlap
    """
    # Convert BBox objects to numpy arrays if needed
    if isinstance(bboxes1, list):
        bboxes1 = np.array([[b.x0, b.y0, b.x2, b.y2] for b in bboxes1])
    if isinstance(bboxes2, list):
        bboxes2 = np.array([[b.x0, b.y0, b.x2, b.y2] for b in bboxes2])

    # Ensure numpy arrays
    bboxes1 = np.asarray(bboxes1)
    bboxes2 = np.asarray(bboxes2)

    # Calculate intersection coordinates
    intersection_x0 = np.maximum(bboxes1[:, [0]], bboxes2[:, [0]].T)
    intersection_y0 = np.maximum(bboxes1[:, [1]], bboxes2[:, [1]].T)
    intersection_x2 = np.minimum(bboxes1[:, [2]], bboxes2[:, [2]].T)
    intersection_y2 = np.minimum(bboxes1[:, [3]], bboxes2[:, [3]].T)

    # Calculate intersection dimensions (add 1 for inclusive coordinates)
    intersection_width = np.maximum(intersection_x2 - intersection_x0 + 1, 0.0)
    intersection_height = np.maximum(intersection_y2 - intersection_y0 + 1, 0.0)

    # Calculate intersection area
    intersection_area = intersection_width * intersection_height

    # Calculate bboxes1 areas
    bboxes1_width = bboxes1[:, [2]] - bboxes1[:, [0]] + 1
    bboxes1_height = bboxes1[:, [3]] - bboxes1[:, [1]] + 1
    bboxes1_area = bboxes1_width * bboxes1_height

    # Create overlap matrix and compute ratios where intersection exists
    overlap_matrix = np.zeros((bboxes1.shape[0], bboxes2.shape[0]))
    np.divide(
        intersection_area,
        bboxes1_area,
        out=overlap_matrix,
        where=intersection_area > 0.0,
    )

    return overlap_matrix


def bbox_intersection(bbox1: BBox, bbox2: BBox) -> BBox | None:
    """
    Calculate intersection of two bounding boxes.

    Args:
        bbox1: First bounding box
        bbox2: Second bounding box

    Returns:
        BBox representing intersection, or None if no overlap
    """
    x0 = max(bbox1.x0, bbox2.x0)
    y0 = max(bbox1.y0, bbox2.y0)
    x2 = min(bbox1.x2, bbox2.x2)
    y2 = min(bbox1.y2, bbox2.y2)

    if x2 < x0 or y2 < y0:
        return None

    return BBox(x0=x0, y0=y0, x2=x2, y2=y2)


def bbox_union(bbox1: BBox, bbox2: BBox) -> BBox:
    """
    Calculate union (bounding box) of two bounding boxes.

    Args:
        bbox1: First bounding box
        bbox2: Second bounding box

    Returns:
        BBox encompassing both input boxes
    """
    return BBox(
        x0=min(bbox1.x0, bbox2.x0),
        y0=min(bbox1.y0, bbox2.y0),
        x2=max(bbox1.x2, bbox2.x2),
        y2=max(bbox1.y2, bbox2.y2),
    )


def bbox_iou(bbox1: BBox, bbox2: BBox) -> float:
    """
    Calculate Intersection over Union (IoU) of two bounding boxes.

    IoU is a common metric for measuring overlap between bounding boxes.
    It ranges from 0 (no overlap) to 1 (perfect overlap).

    Args:
        bbox1: First bounding box
        bbox2: Second bounding box

    Returns:
        IoU score between 0 and 1
    """
    intersection = bbox_intersection(bbox1, bbox2)
    if intersection is None or intersection.area == 0:
        return 0.0

    union_area = bbox1.area + bbox2.area - intersection.area
    if union_area == 0:
        return 0.0

    return intersection.area / union_area


def bbox_distance(bbox1: BBox, bbox2: BBox) -> float:
    """
    Calculate minimum distance between two bounding boxes.

    Returns 0 if boxes overlap, otherwise returns minimum Euclidean
    distance between box edges.

    Args:
        bbox1: First bounding box
        bbox2: Second bounding box

    Returns:
        Minimum distance between boxes
    """
    # Check if boxes overlap
    if not (
        bbox1.x2 < bbox2.x0
        or bbox1.x0 > bbox2.x2
        or bbox1.y2 < bbox2.y0
        or bbox1.y0 > bbox2.y2
    ):
        return 0.0

    # Calculate horizontal and vertical distances
    horizontal_distance = max(0, bbox1.x0 - bbox2.x2, bbox2.x0 - bbox1.x2)
    vertical_distance = max(0, bbox1.y0 - bbox2.y2, bbox2.y0 - bbox1.y2)

    # Return Euclidean distance
    return np.sqrt(horizontal_distance**2 + vertical_distance**2)


def cluster_points(
    array: list | np.ndarray,
    threshold: float = 10.0,
    key=None,
) -> np.ndarray:
    """
    Remove close points by clustering.

    Groups points that are within threshold distance and keeps only
    one representative point per cluster.

    Args:
        array: Array of points or objects to cluster
        threshold: Minimum distance between points (default: 10.0)
        key: Function to extract comparison value (default: identity)

    Returns:
        Numpy array with clustered points

    Example:
        >>> points = [1, 2, 3, 15, 16, 30]
        >>> cluster_points(points, threshold=5)
        array([1, 15, 30])
    """
    if key is None:

        def key(x):
            return x

    array = sorted(array, key=key)

    if len(array) == 0:
        return np.asarray([])

    result = [array[0]]

    for i, x in enumerate(array[1:]):
        if (key(x) - key(array[i])) > threshold:
            result.append(x)

    return np.asarray(result)
