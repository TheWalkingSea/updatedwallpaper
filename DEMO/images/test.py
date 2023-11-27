import requests
import json
import time

import win32api
import ctypes

# lib = ctypes.cdll("shlobj_core.h")
# print(lib)
# lib.setpattern(21)
SPI_SETDESKPATTERN = 21
print(ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKPATTERN, "tile", 0, 3))

# def getMonitorInfo()->list:
#     lpmi = list() # LPMONITORINFO
#     monitors = win32api.EnumDisplayMonitors()
#     for hMonitor in monitors:
#         offsetX, offsetY, width, height = win32api.GetMonitorInfo(hMonitor[0])["Monitor"]
#         width -= offsetX
#         height -= offsetY
#         lpmi.append({
#             "left": offsetX,
#             "top": offsetY,
#             "width": width,
#             "height": height
#         })
#     return lpmi
# print(getMonitorInfo())
    
# while True:

#     payload = {"access_token": "1124~qOyLYOXZ1K64MQJhcbY4mO7W7ifLLidRv4A5s2K82xhXGGMVcm9f9oV2Kv4AueYC"}
#     req = requests.get(f"https://pasco.instructure.com/api/v1/courses/373493/todo", params=payload)
#     content = req.content
#     dic = json.dumps(dict(req.headers))
#     dic = json.loads(dic)
#     print(dic["X-Rate-Limit-Remaining"])
#     # time.sleep(0)