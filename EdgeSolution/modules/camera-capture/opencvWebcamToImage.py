import cv2
import time
import os


def video_to_frames(input_loc, output_loc):
    """Function to extract frames from input video stream/file and save an average image in an output directory.

    Args:
        input_loc: Input video stream/file.
        output_loc: Output directory to save the frames.

    Returns:
        The picture location
    """
    (r_avg, g_avg, b_avg) = (None, None, None)
    total = 0

    try:
        os.mkdir(output_loc)
    except OSError:
        pass
    time_start = time.time()
    time_end = time_start + 2
    cap = cv2.VideoCapture(input_loc)
    while time.time() <= time_end:
        ret, frame = cap.read()
        (b, g, r) = cv2.split(frame.astype("float"))
        if r_avg is None:
            r_avg = r
            b_avg = b
            g_avg = g
        else:
            r_avg = ((total * r_avg) + (1 * r)) / (total + 1.0)
            g_avg = ((total * g_avg) + (1 * g)) / (total + 1.0)
            b_avg = ((total * b_avg) + (1 * b)) / (total + 1.0)
        total += 1

    cap.release()
    cv2.destroyAllWindows()
    avg = cv2.merge([b_avg, g_avg, r_avg]).astype("uint8")
    picture_location = output_loc + "/avg_pic_%d.jpg" % int(time_end)
    cv2.imwrite(picture_location, avg)
    return picture_location
