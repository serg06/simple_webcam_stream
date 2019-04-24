Simple webcam streaming with Flask.
Inspired by https://blog.miguelgrinberg.com/post/video-streaming-with-flask.
Expanded to work with multiple cameras.

What it does:
- Starts looking through all your cameras
- Continually caches last frame from every camera
- When someone asks for camera feed, repeatedly stream that camera's last cached frame

Requires:
- Python 3.x
- OpenCV2: `pip install opencv-python` (And no, no numpy required.)
- `pip install` any other imports that complain.

Endpoints:
- /cam/<int:num>: Streams camera with index num directly to you.
- /stream: Streams all cameras to you and puts them together on one page.
