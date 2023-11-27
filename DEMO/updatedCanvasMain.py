"""
Copyright (c) 2022, Austin McCallister
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. 
"""


import win32api
import aiohttp
import json
import datetime
import asyncio
from PIL import Image, ImageDraw, ImageFont
import os
import ctypes
import winreg
import requests


class instructuretoimgcp():
    def __init__(self, api_token, parsedCourses=dict()):
        self.api_token = api_token
        self.courseids = {"Legal Aspects Business": 373493, "Geometry": 373524, "English": 373351, "Business Entrep": 373487, "Biology": 373220, "Computer Science": 373246}
        # self.temp = {"English": 373351}
        self.parsedcourses = parsedCourses
        self.screen = int(open("screen.txt", "r").read())
        # self.parsedcourses = {'English': {'Practice Exam I': {'points': 100.0, 'due': datetime.datetime(2022, 8, 8, 8, 59, 59)}, 'Dialectical Journal': {'points': 100.0, 'due': datetime.datetime(2022, 8, 8, 8, 59, 59)}},  'Math': {'5-1 Quiz': {'points': 100.0, 'due': datetime.datetime(2022, 8, 8, 9, 59, 59)}}} # Developer testing dictionaries
        # self.size = (1440, 900) # Small screen
        # self.size = (1920, 1080)
        # self.size = (1179, 621)
        # self.size = (2560, 1440)
        # self.size = (2736, 1824)
        self.W, self.H = self.size
        self.italfont = ImageFont.truetype(font= "Tools/ariali.ttf", size=70)
        self.boldfontTitle = ImageFont.truetype(font= "Tools/arialbd.ttf", size=int(self.H*0.03333333333)) # 30
        self.boldfont = ImageFont.truetype(font= "Tools/arialbd.ttf", size=int(self.H*0.03333333333)) # 30
        self.font = ImageFont.truetype(font= "Tools/arial.ttf", size=int(self.H*0.02777777777)) # 25


    async def parse(self):
        payload = {"access_token": self.api_token}
        async with aiohttp.ClientSession() as session:
            async with session.get("https://pasco.instructure.com/api/v1/users/self/todo", params=payload) as req:
                for assignmentData in json.loads(await req.read()):
                    parsedAssignments = dict()
                    assignment = assignmentData["assignment"]
                    if not assignment["locked_for_user"] and int(assignment['points_possible']) != 0: # add not later
                        points = assignment['points_possible']
                        name = assignment['name']
                        try:
                            due = datetime.datetime.strptime(assignment['lock_at'], "%Y-%m-%dT%H:%M:%Sz")
                        except:
                            due = None
                        parsedAssignments[name] = {'points': points, "due": due}
                    else:
                        #print(f"locked {item['assignment']['name']}")
                        pass
                    if parsedAssignments:
                        courseName = await self.stripName(assignmentData["context_name"].title())
                        if courseName in self.parsedcourses.keys(): # Tada no try block needed, give yourself a pat on the back
                            self.parsedcourses[courseName].update(parsedAssignments)
                        else:
                            self.parsedcourses[courseName] = parsedAssignments
                    
    async def stripName(self, course):
        return course.split("-")[0]


    def parseScreenDimensions(self, monitors) -> list: # Converts (0,0) from the top left of hMonitor 1, to top left of virtual monitor to be image process. We love Windows ikik
        parsed = list()
        offsetx = min([i["left"] for i in monitors])
        offsety = min([i["top"] for i in monitors])
        for hMonitor in monitors:
            left, top, *args = hMonitor.values()
            left -= offsetx
            top -= offsety
            parsed.append((left, top, *args))
        return parsed

    @property
    def size(self):
        lpmi = self.getMonitorInfoW()
        if len(lpmi) < 2: # Singe Monitor Setup
            size = (lpmi[0][2], lpmi[0][3])
        else: # Multi-Monitor Setup
            size = (lpmi[self.screen][2], lpmi[self.screen][3])
        return size

    def getMonitorInfoW(self) -> list:
        lpmi = list() # LPMONITORINFO
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
        monitors = win32api.EnumDisplayMonitors()
        for hMonitor in monitors:
            offsetX, offsetY, width, height = win32api.GetMonitorInfo(hMonitor[0])["Monitor"]
            width -= offsetX
            height -= offsetY
            lpmi.append({
                "left": offsetX,
                "top": offsetY,
                "width": width,
                "height": height
            })
        return self.parseScreenDimensions(lpmi)

    def resize(self, monitor, img): # vs -> virtualScreen, resizes image to FILL mode
        top, left, width, height = monitor # Height of hMonitor
        if img.size != (width, height):
            bWidth, bHeight = img.size # Background image
            scale = height/bHeight # Scale factor from background img to hMonitor
            crop = (bWidth*scale-width)/2 # Crops sides off poorly balanced sides
            img = img.resize((int(bWidth*scale), int(bHeight*scale))) # width | height
            bWidth, bHeight = img.size # Background image
            return img.crop(map(int, (crop, 0, bWidth-crop, height))) # left | top | right | bottom
        else: return img

    def makeTiles(self, todoimg):
        todoimg.save(r"images\preview.png")
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        virtualScreen = (user32.GetSystemMetrics(78), user32.GetSystemMetrics(79))
        monitors = self.getMonitorInfoW()
        SPI_SETDESKPATTERN = 21 # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-systemparametersinfow
        if len(monitors) != 1:
            wallpaper = Image.new(size=virtualScreen, mode='RGB', color='black')
            for index, hMonitor in enumerate(monitors):
                if index == self.screen: # Second Screen
                    wallpaper.paste(todoimg, (hMonitor[0], hMonitor[1]))
                else:
                    if os.path.exists(os.path.join(os.getcwd(), rf"images/monitor{index+1}.png")):
                        path = os.path.join(os.getcwd(), rf"images/monitor{index+1}.png")
                    else:
                        path = os.path.join(os.getcwd(), r"images/default.png")
                        backgroundimg = Image.open(path)
                    img = self.resize(hMonitor, backgroundimg)
                    wallpaper.paste(img, (hMonitor[0], hMonitor[1]))
            return wallpaper
        else:
            print("IMG")
            return todoimg
        

        # print(monitors)
        # wallpaper.paste(img, box=(0, 180, self.W, self.H+180))
        # path = os.path.join(os.getcwd(), "default.png")
        # default = Image.open(path)
        # default = default.resize(size=(1920, 1080))
        # wallpaper.paste(default, box=(1440, 0, 3360, 1080))
        # return wallpaper

    def toPIL(self, courses):
        path = os.path.join(os.getcwd(), r"images\template.png")
        if not os.path.exists(path):
            img = Image.new(mode='RGB', size=self.size, color=(220, 255, 255))
            draw = ImageDraw.Draw(img)
            w, h = draw.textsize("To-Do List", font=self.italfont)
            draw.text(((self.W-w)/2, 72), "To-Do List", fill=(0, 0, 0), font=self.italfont)
        else:
            img = Image.open(path)
            img = img.resize(size=(self.W, self.H))
            draw = ImageDraw.Draw(img)
            w, h = draw.textsize("To-Do List", font=self.italfont)
            draw.text(((self.W-w)/2, 72), "To-Do List", fill=(0, 0, 0), font=self.italfont)
        #print(draw.textsize("Sun, Dec 31, 2021", self.font), draw.textsize("100 points", self.font))
        height = 180 # Default Value
        x1 = (self.W-(self.W*.2083)) # (self.W-300) # 20.83% LINE 1 from right
        x2 = (self.W-(self.W*.3125)) # (self.W-450) # 31.25% LINE 2 from right
        def drawTable(height=180):
            draw.line((x2, height, x2, self.H), fill='black', width=3) # Add 1st line
            draw.line((x1, height, x1, self.H), fill='black', width=3) # Add 2nd line
            draw.line((0, height+60, self.W, height+60), fill='black', width=3) # Add crossing line
            w, h = draw.textsize("Due Date", font=self.boldfontTitle) # Get width of "Due Date"
            draw.text(((self.W-x1-w)/2+x1, height), "Due Date", fill='black', font=self.boldfontTitle) # Add "Due Date" text
            w, h = draw.textsize("Points", font=self.boldfontTitle) # Get width of "Points"
            draw.text(((x2-x1-w)/2+x1, height), "Points", fill='black', font=self.boldfontTitle) # Add "Points" text
            w, h = draw.textsize("Assignments", font=self.boldfontTitle) # Get width of "Assignments"
            draw.text(((x2-w)/2, height), "Assignments", fill='black', font=self.boldfontTitle) # Add "Assignments" text
        height += self.H*0.03472222222 # 50 # Adds an extra line for columns above
        for key, value in courses.items():
            #print(key, height)
            height += 45 # Height above courseName, creates footer for prev course
            indent = 50 # self.W*.034722 # 50
            draw.text((indent, height), key, fill='black', font=self.boldfont)
            height += self.H*0.00851851851 # Difference between course name and assignments
            totalHeight = height
            for i in range(len(value)):
                totalHeight += self.H*.042
            draw.rounded_rectangle((75, height+self.H*.036, self.W-25, totalHeight+self.H*.038), radius=8, fill=(220, 255, 255))
            for assignment, info in value.items():
                height += self.H*.042 # Difference between assignment to assignment
                if info['due']:
                    timedel = info['due'] + datetime.timedelta(minutes=1) # Assignments that close at 11:59, makes it the next day
                    time = timedel.strftime("%a, %b %d, %Y")
                    w, h = draw.textsize(time, font=self.font)
                    draw.text(((self.W-x1-w)/2+x1, height), time, fill='black', font=self.font)
                points = f'{int(info["points"])} points'
                draw.text((indent*2, height), assignment, fill='black', font=self.font)
                w, h = draw.textsize(points, font=self.font)
                draw.text(((x2-x1-w)/2+x1, height), points, fill='black', font=self.font)
        drawTable()
        return self.makeTiles(img)


    def setReg(self, TileWallpaper, WallpaperStyle):
        REG_PATH = r"Control Panel\Desktop"
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, "TileWallpaper", 0, winreg.REG_SZ, "1") # https://docs.microsoft.com/en-us/windows/win32/controls/themesfileformat-overview?redirectedfrom=MSDN#control-paneldesktop-section
        winreg.SetValueEx(registry_key, "WallpaperStyle", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(registry_key)

    def background(self, img):
        if self.parsedcourses: # uncomment later
            img.save(r"images\processed.png")
            dir = os.path.join(os.getcwd(), r"images\processed.png")
            self.setReg(1, 0) # TILE || Hour count on this single line: 6hrs. Next time, broadcast the wallpaper BEFORE you set the registry funny boy
            ctypes.windll.user32.SystemParametersInfoW(20, 0, dir, 3)
        else: # uncomment later
            dir = os.path.join(os.getcwd(), r"images\default.png")
            self.setReg(0, 2) # Fill
            ctypes.windll.user32.SystemParametersInfoW(20, 0, dir, 3)



class record():
    def __init__(self, msg, time: datetime) -> None:
        self.msg = msg
        self.time = time

    def endTimer(self):
        print(f"{self.msg}: {(datetime.datetime.utcnow()-self.time).total_seconds()}")
        
def recordTime(msg):
    return record(msg, datetime.datetime.utcnow())


data = dict()
def waitforupdate():
    while True:
        r = requests.get("http://192.168.50.237:4003/get")
        try:
            s = r.json()
            time = s['time']
            time = time.replace("-", ":").replace(":", "-", 2)[:-6] + "Z"
            time = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%Sz")
            stuff = {s["class"]: {s["assign"]: {"points": int(s['points']), "due": time}}}
            if stuff != data:
                print(stuff)
                data.update(stuff)
                return stuff
        except: pass

async def main():
    while True:
        d = waitforupdate()
        tasks = list()
        async with aiohttp.ClientSession() as session:
            begin = recordTime("TOTAL TIME")
            rt = recordTime("FETCHING...")
            iti = instructuretoimgcp("1124~qOyLYOXZ1K64MQJhcbY4mO7W7ifLLidRv4A5s2K82xhXGGMVcm9f9oV2Kv4AueYC", d)
            await iti.parse()
            rt.endTimer()

            loop = asyncio.get_event_loop()
            rt = recordTime("FILTERING...")
            if iti.parsedcourses:
                img = await loop.run_in_executor(None, iti.toPIL, iti.parsedcourses)
            else: img = None
            rt.endTimer()
            rt = recordTime("SETTING WALLPAPER...")
            await loop.run_in_executor(None, iti.background, img)
            rt.endTimer()
            begin.endTimer()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())