import os
import sys

audio_formats = [".ogg", ".wav", ".mp3"]

def extract_audiof(PATH):
    return [os.path.abspath(f) for f in os.scandir(PATH) if f.is_file()
            if os.path.splitext(f)[1] in audio_formats]

def write_file(path):
    
    with open(ASSETS/"paths.txt", "a+") as f:
        with open(ASSETS/"paths.txt", "r") as rf:
            c = rf.readlines()
            for pathf in c:
                if pathf.strip("\n") == path:
                    print("Directory is already being tracked.")
                    sys.exit()
                else:
                    continue

        f.write(path+"\n")
        sys.exit()

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]