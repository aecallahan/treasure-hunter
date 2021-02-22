import os
import tailer
import json

filePath = os.path.join("..", "..", "..", "AppData", "LocalLow", "Wizards Of The Coast", "MTGA", "Player.log")
numberOfLogs = 0

for line in tailer.follow(open(filePath)):
    print(line)

