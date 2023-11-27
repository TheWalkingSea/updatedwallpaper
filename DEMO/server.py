from flask import Flask, request

app = Flask(__name__)

stuff = dict()

@app.route("/set", methods=["POST"])
def setter():
    global stuff
    stuff = request.json
    return stuff

@app.route("/get", methods=["GET"])
def getter():
    global stuff
    return stuff


if __name__ == "__main__":
    app.run("192.168.50.237", port=4003)
