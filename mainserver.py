import aiohttp
import json
import datetime
import PIL
import asyncio
from PIL import Image, ImageDraw, ImageColor, ImageFont
from io import BytesIO
import os


from flask import Flask, request, send_file, redirect, session, jsonify

from tempfile import TemporaryDirectory
import re
import zipfile

LOGIN = {"admin": "kFi7H%*lKmO"}
app = Flask(__name__)
IP = "192.168.50.179"
PORT = 4000

class instructuretoimgcp():
    def __init__(self, api_token):
        self.api_token = api_token
        self.courseids = {"AP Calculus BC": 409805, "Computer Science A": 418634, "AP Physics": 410143, "English Honours": 419043, "AP World History": 410268}
        # self.temp = {"English": 373351}
        self.parsedcourses = dict()
        #self.parsedcourses = {'English': {'The ssssssssssssssssssssssssssssssssssssssssseond assignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}} # Developer testing dictionaries
        self.size = (1440, 900) # Small screen
        self.W, self.H = self.size
        self.italfont = ImageFont.truetype(font= "fonts/ariali.ttf", size=70)
        self.boldfont = ImageFont.truetype(font= "fonts/arialbd.ttf", size=30)
        self.font = ImageFont.truetype(font= "fonts/arial.ttf", size=25)


    # async def parse(self, key, value, session): # Grabs todo list and formats to a readable format
    #     parsed_assignments = dict()
    #     payload = {"access_token": self.api_token}
    #     async with session.get(f"https://pasco.instructure.com/api/v1/courses/{value}/todo", params=payload) as req:
    #         print(req.url)
    #         req = json.loads(await req.read()) # parses the bytes to a list
    #         for item in req:
    #             print(assignment)
    #             assignment = item["assignment"]
    #             if not assignment["locked_for_user"] and int(assignment['points_possible']) != 0: # add not later
    #                 points = assignment['points_possible']
    #                 name = assignment['name']
    #                 try:
    #                     due = datetime.datetime.strptime(assignment['lock_at'], "%Y-%m-%dT%H:%M:%Sz")
    #                 except:
    #                     due = None
    #                 parsed_assignments[name] = {'points': points, "due": due}
    #             else:
    #                 #print(f"locked {item['assignment']['name']}")
    #                 pass
    #         if parsed_assignments:
    #             self.parsedcourses[key] = parsed_assignments



    def toPIL(self, courses):
        path = os.path.join(os.getcwd(), "template.png")
        if not os.path.exists(path):
            img = Image.new(mode='RGB', size=self.size, color=(220, 255, 255))
            draw = ImageDraw.Draw(img)
            w = draw.textlength("To-do List", font=self.italfont)
            draw.text(((self.W-w)/2, 72), "To-do List", fill=(0, 0, 0), font=self.italfont)
        else:
            img = Image.open(path)
            img = img.resize(size=(self.W, self.H))
            draw = ImageDraw.Draw(img)
        #print(draw.textlength("Sun, Dec 31, 2021", self.font), draw.textlength("100 points", self.font))
        height = 180 # Default Value
        x1 = (self.W-300)
        x2 = (self.W-450)
        def addtable():
            draw.line((x2, height, x2, self.H), fill='black', width=3) # Add 1st line
            draw.line((x1, height, x1, self.H), fill='black', width=3) # Add 2nd line
            draw.line((0, height+60, self.W, height+60), fill='black', width=3) # Add crossing line
            w = draw.textlength("Due Date", font=self.boldfont) # Get width of "Due Date"
            draw.text(((self.W-x1-w)/2+x1, height), "Due Date", fill='black', font=self.boldfont) # Add "Due Date" text
            w = draw.textlength("Points", font=self.boldfont) # Get width of "Points"
            draw.text(((x2-x1-w)/2+x1, height), "Points", fill='black', font=self.boldfont) # Add "Points" text
            w = draw.textlength("Assignments", font=self.boldfont) # Get width of "Assignments"
            draw.text(((x2-w)/2, height), "Assignments", fill='black', font=self.boldfont) # Add "Assignments" text

        addtable()
        height += 40 # Adds an extra line for columns above
        for key, value in courses.items():
            #print(key, height)
            height += 40
            indent = 50
            draw.text((indent, height), key, fill='black', font=self.boldfont)
            for assignment, info in value.items():
                height += 40
                if info['due']:
                    timedel = info['due'] + datetime.timedelta(minutes=1)
                    time = timedel.strftime("%a, %b %d, %Y")
                    w = draw.textlength(time, font=self.font)
                    draw.text(((self.W-x1-w)/2+x1, height), time, fill='black', font=self.font)
                points = f'{int(info["points"])} points'
                draw.text((indent*2, height), assignment, fill='black', font=self.font)
                w = draw.textlength(points, font=self.font)
                draw.text(((x2-x1-w)/2+x1, height), points, fill='black', font=self.font)
        
        wallpaper = Image.new(size=(3360, 1080), mode='RGB', color='black')
        wallpaper.paste(img, box=(0, 180, self.W, self.H+180))
        path = os.path.join(os.getcwd(), "default.png")
        default = Image.open(path)
        default = default.resize(size=(1920, 1080))
        wallpaper.paste(default, box=(1440, 0, 3360, 1080))
        return wallpaper




class instructuretoimg():
    def __init__(self, api_token):
        self.api_token = api_token
        self.courseids = {"AP Calculus BC": 409805, "Computer Science A": 418634, "AP Physics": 410143, "English Honours": 419043, "AP World History": 410268}
        self.parsedcourses = dict()
        # self.parsedcourses = {'En glish': {'The Modulheu Exam Review for Biology': {'points': 100.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}, 'The MoBiology': {'points': 100.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}},  'Math': {'The Modulheu Exam Review for Biology': {'points': 100.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}} # Developer testing dictionaries
        self.size = (1170, 2532) # Small screen
        self.W, self.H = self.size
        self.italfont = ImageFont.truetype(font= "fonts/ariali.ttf", size=85)
        self.boldfont = ImageFont.truetype(font= "fonts/arialbd.ttf", size=40)
        self.font = ImageFont.truetype(font= "fonts/arial.ttf", size=35)


    async def parse(self, key, value, session): # Grabs todo list and formats to a readable format
        parsed_assignments = dict()
        payload = {"access_token": self.api_token}
        async with session.get(f"https://pasco.instructure.com/api/v1/courses/{value}/todo", params=payload) as req:
            print(req.url)
            req = json.loads(await req.read()) # parses the bytes to a list
            for item in req:
                assignment = item["assignment"]
                if not assignment["locked_for_user"] and int(assignment['points_possible']) != 0: # add not later
                    points = assignment['points_possible']
                    name = assignment['name']
                    try:
                        due = datetime.datetime.strptime(assignment['lock_at'], "%Y-%m-%dT%H:%M:%Sz")
                    except:
                        due = None
                    parsed_assignments[name] = {'points': points, "due": due}
                else:
                    #print(f"locked {item['assignment']['name']}")
                    pass
            if parsed_assignments:
                self.parsedcourses[key] = parsed_assignments



    def toPIL(self, courses):
        path = os.path.join(os.getcwd(), "template.png")
        if not os.path.exists(path):
            img = Image.new(mode='RGB', size=self.size, color=(220, 255, 255))
            draw = ImageDraw.Draw(img)
            w = draw.textlength("To-do List", font=self.italfont)
            draw.text(((self.W-w)/2, 670), "To-do List", fill=(0, 0, 0), font=self.italfont)
        else:
            img = Image.open(path)
            img = img.resize(size=(self.W, self.H))
            draw = ImageDraw.Draw(img)
        #print(draw.textlength("Sun, Dec 31, 2021", self.font), draw.textlength("100 points", self.font))
        height = 775 # Default Value
        x1 = (self.W-325) # Variability between line 1
        x2 = (self.W-505) # Variability between line 2
        def addtable():
            draw.line((x2, height, x2, self.H), fill='black', width=3) # Add 1st line
            draw.line((x1, height, x1, self.H), fill='black', width=3) # Add 2nd line
            draw.line((0, height+60, self.W, height+60), fill='black', width=3) # Add crossing line
            w = draw.textlength("Due Date", font=self.boldfont) # Get width of "Due Date"
            draw.text(((self.W-x1-w)/2+x1, height), "Due Date", fill='black', font=self.boldfont) # Add "Due Date" text
            w = draw.textlength("Points", font=self.boldfont) # Get width of "Points"
            draw.text(((x2-x1-w)/2+x1, height), "Points", fill='black', font=self.boldfont) # Add "Points" text
            w = draw.textlength("Assignments", font=self.boldfont) # Get width of "Assignments"
            draw.text(((x2-w)/2, height), "Assignments", fill='black', font=self.boldfont) # Add "Assignments" text

        addtable()

        height += 40 # Adds an extra line for columns above
        for key, value in courses.items():
            #print(key, height)
            height += 40
            indent = 50
            draw.text((indent, height), key, fill='black', font=self.boldfont)
            for assignment, info in value.items():
                height += 50
                if draw.textlength(assignment, font=self.font) >= 540:
                    rough_assignment = str() # Temporary string
                    current_line = str()
                    for char in assignment:
                        if draw.textlength(current_line, font=self.font) <= 530:
                            rough_assignment += char
                            current_line += char
                        else:
                            rough_assignment += "-\n" + char
                            current_line = char
                        
                    draw.text((indent*2, height), rough_assignment, fill='black', font=self.font)
                    height += 34


                else:
                    draw.text((indent*2, height), assignment, fill='black', font=self.font)

                if info['due']:
                    timedel = info['due'] + datetime.timedelta(minutes=1)
                    time = timedel.strftime("%a, %b %d, %Y")
                    w = draw.textlength(time, font=self.font)
                    draw.text(((self.W-x1-w)/2+x1, height), time, fill='black', font=self.font)
                points = f'{int(info["points"])} points'
                w = draw.textlength(points, font=self.font)
                draw.text(((x2-x1-w)/2+x1, height), points, fill='black', font=self.font)
        
        return img


def verify(req):
    return req.args.get("USER") in LOGIN and LOGIN[req.args.get("USER")] == req.args.get("PASS")



@app.route("/todo", methods=["GET"])
async def todo():
    tasks = list()
    async with aiohttp.ClientSession() as session:
        iti = instructuretoimg("TOKEN")
        for key, value in iti.courseids.items():
            task = iti.parse(key, value, session)
            tasks.append(task)
        await asyncio.gather(*tasks) # uncomment later

        loop = asyncio.get_event_loop()
        if iti.parsedcourses:
            img = await loop.run_in_executor(None, iti.toPIL, iti.parsedcourses)
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            return send_file(BytesIO(img_byte_arr), download_name="image.png", as_attachment=True)
        else:
            img = open("default.png", "rb")
            return send_file(img, download_name="default.png", as_attachment=True)
        # input(iti.parsedcourses)
        #input = {'English': {'The second assignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'Legal Aspects Business': {'The Five Main Sources of the Law': {'points': 0.0, 'due': datetime.datetime(2021, 8, 28, 3, 59, 59)}}, 'Geometry': {'My math assignment here': {'points': 0.0, 'due': datetime.datetime(2021, 4, 14, 3, 59, 59)}, 'My other math assignment here': {'points': 0.0, 'due': datetime.datetime(2021, 4, 14, 3, 59, 59)}}, 'myclass': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'mclass': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'muytrclass': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'mycls': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'mycs': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'mss': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'msswdefghyj': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'dfgfweumss': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'hrwthrtwmss': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'Engldfahhfdish': {'The second assignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'Engldfgdsahhfdish': {'The second assignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'Engldfgdsahhfdffish': {'The second assignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'Engldfgdsahhfdddish': {'The second assignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}}
        #img.show()


@app.route("/updatewallpaper")
async def updatewallpaper():
    tasks = list()
    async with aiohttp.ClientSession() as session:
        iti = instructuretoimgcp("TOKEN")
        for key, value in iti.courseids.items():
            task = iti.parse(key, value, session)
            tasks.append(task)
        await asyncio.gather(*tasks) # uncomment later
        loop = asyncio.get_event_loop()
        #input = {'English': {'The second assignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'Legal Aspects Business': {'The Five Main Sources of the Law': {'points': 0.0, 'due': datetime.datetime(2021, 8, 28, 3, 59, 59)}}, 'Geometry': {'My math assignment here': {'points': 0.0, 'due': datetime.datetime(2021, 4, 14, 3, 59, 59)}, 'My other math assignment here': {'points': 0.0, 'due': datetime.datetime(2021, 4, 14, 3, 59, 59)}}, 'myclass': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'mclass': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'muytrclass': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'mycls': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'mycs': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'mss': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'msswdefghyj': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'dfgfweumss': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'hrwthrtwmss': {'The dwegssignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'Engldfahhfdish': {'The second assignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'Engldfgdsahhfdish': {'The second assignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'Engldfgdsahhfdffish': {'The second assignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}, 'Engldfgdsahhfdddish': {'The second assignment': {'points': 10.0, 'due': datetime.datetime(2021, 8, 8, 3, 59, 59)}}}
        img = await loop.run_in_executor(None, iti.toPIL, iti.parsedcourses)
        #img.show()
        await loop.run_in_executor(None, iti.background, img)


def removesuffix(name, remove):
    a = name.split(remove)
    return a[0]
    
@app.before_request
def before_request():
    session.permenant = True


@app.route("/")
def default():
    return "running"

@app.route("/fail")
def fail():
    return "fail"


if __name__ == '__main__':
    app.run(IP, PORT)