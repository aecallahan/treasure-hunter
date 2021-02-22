import os
import tailer
import json

filePath = os.path.join("..", "..", "AppData", "LocalLow", "Wizards Of The Coast", "MTGA", "Player.log")
numberOfLogs = 0

for line in tailer.follow(open(filePath)):
    if line.startswith('{ "transactionId"'):
        numberOfLogs += 1
        log = json.loads(line)
        # print(json.dumps(log, indent=2))
        print(log)
        print()
        print(f'----{numberOfLogs}-----')
        print()


