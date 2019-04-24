import time

from flask import Flask, Response, abort, render_template, Markup

import camera

app = Flask(__name__)

camera.load_all_cameras()
camera.start_refreshing()


@app.route('/')
def hello_world():
    return 'Yup, index page works.'


@app.route('/cam/<int:num>')
def cam(num):
    """
    Stream num'th camera.
    """

    if num >= len(camera.all_cameras):
        abort(404)

    def gen():
        while True:
            time.sleep(1 / camera.FPS)
            frame = camera.all_frames[num]
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stream')
def stream():
    """
    Stream all cameras on one page.
    """

    camera_streams = ""
    for i in range(len(camera.all_cameras)):
        camera_streams += "<img src=/cam/%d style='width: 20%%'></img>" % i

    return render_template('stream.html', imgs=Markup(camera_streams))


def main():
    # Does threaded=True even do anything? Or is it a myth? Like the door-close button in elevators. 🤔
    app.run(threaded=True)


if __name__ == '__main__':
    main()
