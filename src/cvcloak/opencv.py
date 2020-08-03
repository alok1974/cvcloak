import cv2
import numpy as np


def open_capture(camera_int, width, height):
    capture = cv2.VideoCapture(camera_int)
    while True:
        if capture.isOpened():
            break
        capture.open()

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return capture


def get_background(capture):
    ret = False
    frame = None
    while True:
        for _ in range(30):
            ret, frame = capture.read()
            frame = cv2.flip(frame, 1)
        if ret:
            break

    if frame is None:
        capture.release()
        error_msg = (
            "Unable to initialize the background!"
        )
        raise RuntimeError(error_msg)

    return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


def close_capture(capture):
    capture.release()
    cv2.destroyAllWindows()


def get_frame(
        capture, background,
        low_color_1, high_color_1, low_color_2, high_color_2,
):
    if background is None:
        return

    ret, frame = capture.read()

    # Wait till capture initializes
    if not ret:
        return

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    frame = cv2.flip(frame, 1)

    return _process_capture(
        frame=frame,
        background=background,
        low_color_1=low_color_1,
        high_color_1=high_color_1,
        low_color_2=low_color_2,
        high_color_2=high_color_2,
    )


def _process_capture(
        frame, background, low_color_1,
        low_color_2, high_color_1, high_color_2
):
    # Define 1st color band
    lower_band_1 = np.array(list(low_color_1))
    upper_band_1 = np.array(list(high_color_1))
    color_band_1 = cv2.inRange(frame, lower_band_1, upper_band_1)

    # Define second color band
    lower_band_2 = np.array(list(low_color_2))
    upper_band_2 = np.array(list(high_color_2))
    color_band_2 = cv2.inRange(frame, lower_band_2, upper_band_2)

    # Combine color bands into single mask
    color_mask = color_band_1 + color_band_2

    # Apply noise filter to color mask
    color_mask = cv2.morphologyEx(
        color_mask,
        cv2.MORPH_OPEN,
        np.ones((3, 3), np.uint8),
        iterations=8,
    )

    # Apply smooth filter to color mask
    color_mask = cv2.morphologyEx(
        color_mask,
        cv2.MORPH_DILATE,
        np.ones((3, 3), np.uint8),
        iterations=1,
    )

    # Replace the mask color with color from
    # captured one frame background
    masked_bg = cv2.bitwise_and(
        background,
        background,
        mask=color_mask,
    )

    # Get the inverse of the color mask
    inverse_color_mask = cv2.bitwise_not(color_mask)

    # Get the color of the current frame sans the color mask
    masked_frame = cv2.bitwise_and(frame, frame, mask=inverse_color_mask)

    # Composite the background and current frame colors
    composite = cv2.addWeighted(masked_bg, 1, masked_frame, 1, 0)

    # Convert HSV to RGB for display
    final_composite = cv2.cvtColor(composite, cv2.COLOR_HSV2RGB)

    return final_composite
