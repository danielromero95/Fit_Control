# src/A_preprocessing/video_utils.py

"""Utility functions for working with video files."""

import os
import cv2


def validate_video(path: str) -> dict:
    """Validate a video file and return its basic properties.

    Parameters
    ----------
    path : str
        Path to the video file.

    Returns
    -------
    dict
        Dictionary with keys ``fps``, ``frame_count`` and ``duration``.

    Raises
    ------
    IOError
        If the file does not exist or cannot be opened.
    ValueError
        If the video reports zero FPS.
    """
    if not os.path.exists(path):
        raise IOError(f"File does not exist: {path}")

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        cap.release()
        raise IOError(f"Cannot open video file: {path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    if fps == 0:
        raise ValueError("Video FPS is zero")

    duration = frame_count / fps
    return {"fps": fps, "frame_count": frame_count, "duration": duration}
