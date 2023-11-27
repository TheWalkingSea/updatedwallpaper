from flask import Flask, request, send_file, redirect, session
from pytube import YouTube
from io import BytesIO
from tempfile import TemporaryDirectory
import re
import os
import zipfile

app = Flask(__name__)
IP = "192.168.50.39"

def removesuffix(name, remove):
    a = name.split(remove)
    return a[0]
    
@app.before_request
def before_request():
    session.permenant = True

@app.route("/downloadall", methods=["GET"])
def downloadfolder():
    with zipfile.ZipFile("songs.zip", "w") as Zip:
        for foldername in os.listdir(os.path.join(os.getcwd(), "music")):
            foldername = os.path.join(os.getcwd(), os.path.join("music", foldername))
            for filename in os.listdir(foldername):
                Zip.write(os.path.join(foldername, filename), arcname=filename)
    with open("songs.zip", "rb") as r:
        bytes = r.read()
    return send_file(BytesIO(bytes), download_name="songs.zip", as_attachment=True)
                

@app.route("/")
def default():
    return "running"

@app.route("/fail")
def fail():
    return "fail"

@app.route("/downloadvideo", methods=["POST"])
def downloadvideo():
    if request.method == "POST":
        if not request.form["URL"]:
            return redirect("/fail")
        else:
            with TemporaryDirectory() as tmp_dir:
                url = request.form["URL"]
                stream = YouTube(url).streams.filter(res="1080p").first()
                if not stream:
                    stream = YouTube(url).streams.get_highest_resolution()
                print("DOWNLOADING")
                download_path=stream.download(output_path=tmp_dir)
                print("DOWNLOADED")
                video_name = download_path.split("\\")[-1].strip(tmp_dir)
                with open(download_path, "rb") as f:
                    file_bytes = f.read()
                print("SENDING")
                return send_file(BytesIO(file_bytes), download_name=video_name, as_attachment=True)


@app.route("/downloadaudio", methods=["POST"])
def downloadaudio():
    if request.method == "POST":
        if not request.form["URL"]:
            return redirect("/fail")
        else:#try:
            def get_video_name(): # f"{stream.default_filename[:-4]}.mp3"
                try:
                    name = stream.default_filename
                    name = re.sub("([\(\[]).*?([\)\]])", "", name)
                    name = name.split("-", 1)[1]
                    name = name.replace("-", "", 1)
                    name = name.split("ft")[0]
                    name = name.split("feat")[0]
                except: pass
                name = removesuffix(name, ".mp4")
                name = name.strip()
                name += ".mp3"
                return name

            url = YouTube(request.form["URL"])
            stream = url.streams #.streams.get_highest_resolution()
            stream = stream.filter(only_audio=True).first()
            dire = os.path.join(os.getcwd(), os.path.join("music", url.author.replace("VEVO", "")))
            if not os.path.isdir(dire):
                dire = dire.replace("VEVO", "")
                os.makedirs(dire)
            print(dire)
            path = stream.download(output_path=dire, filename=get_video_name())
            with open(path, "rb") as r:
                bytes = r.read()
            return send_file(BytesIO(bytes), download_name=get_video_name(), as_attachment=True)

@app.route("/updatenames", methods=["GET"])
def updatenames():
    load = dict()
    other = list()
    for foldername in os.listdir(os.path.join(os.getcwd(), "music")):
        files = list()
        path = path = os.listdir(os.path.join(os.getcwd(), os.path.join("music", foldername)))
        for filename in path:
            files.append(removesuffix(filename, ".mp3"))
            if len(path) > 4:
                load[foldername] = files
            else:
                other.append(removesuffix(filename, ".mp3"))
    load["Other"] = other
    return load
    



if __name__ == "__main__":
    app.run(port=4000, host=IP)