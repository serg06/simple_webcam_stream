import time
from multiprocessing.pool import ThreadPool
from threading import Thread
from typing import List

import cv2

FPS = 30.0  # max FPS (used for efficiency)
CAM_LOAD_BATCH_SIZE = 5

# TODO: Store all the following stuff in a Cameras object?

all_cameras: List[cv2.VideoCapture] = []
all_frames: List[bytes] = []
all_threads: List[Thread] = []


def load_camera(idx=0):
    cam = cv2.VideoCapture(idx)
    success, _ = cam.read()

    if success:
        return cam

    cam.release()
    return None


def load_all_cameras():
    """
    Load all cameras (into all_cameras) in batches until one camera fails to load.
    """

    assert CAM_LOAD_BATCH_SIZE > 0

    i = 0
    pool = ThreadPool(CAM_LOAD_BATCH_SIZE)  # Load BATCH_SIZE cameras at once.

    while True:
        print('loading cameras %d to %d...' % (i * CAM_LOAD_BATCH_SIZE, (i + 1) * CAM_LOAD_BATCH_SIZE - 1))

        # load cameras 0          to   BATCH_SIZE-1
        # then cameras BATCH_SIZE to 2*BATCH_SIZE-1
        # then ...
        cameras = pool.map(func=load_camera, iterable=range(i * CAM_LOAD_BATCH_SIZE, (i + 1) * CAM_LOAD_BATCH_SIZE))

        # if first camera failed to load, we outta here
        if cameras[0] is None:
            print('first camera failed')
            break

        # if some other camera failed to load, append the working ones and we outta here
        if cameras[-1] is None:
            # find the first broken camera
            first_broken_idx = cameras.index(None)
            print('camera at index %d failed' % first_broken_idx)

            # attach the working cameras
            working_cameras = cameras[:first_broken_idx]
            print('appending %d cameras' % len(working_cameras))
            all_cameras.extend(working_cameras)
            print('there are now %d loaded cameras' % len(all_cameras))

            break

        # all cameras loaded! Append and try again.
        print('appending %d cameras' % len(cameras))
        all_cameras.extend(cameras)
        print('there are now %d loaded cameras' % len(all_cameras))

        i += 1


# start refreshing all camera frames
def start_refreshing():
    global all_frames
    global all_threads

    # TODO: kill any existing threads (in all_threads) first

    all_frames = [b'' for _ in range(len(all_cameras))]
    threads = []

    for i in range(len(all_cameras)):
        t = Thread(target=update_frame, args=(i,))
        t.start()
        threads.append(t)

    all_threads = threads


def update_frame(idx):
    print("launch camera %d thread..." % idx)
    global all_frames
    while True:
        _, image = all_cameras[idx].read()
        _, jpeg = cv2.imencode('.jpg', image)
        all_frames[idx] = jpeg.tobytes()
        time.sleep(1 / FPS)
