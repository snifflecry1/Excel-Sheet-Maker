import os

os.environ["EVENTLET_NO_GREENDNS"] = "yes"
import eventlet

eventlet.monkey_patch()

from app import create_app, socket

flask_app, socket = create_app()

if __name__ == "__main__":
    socket.run(
        flask_app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True
    )
