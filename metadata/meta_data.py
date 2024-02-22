import os


class FlipperMetaData:
    def __init__(self, dir_path) -> None:
        meta = ""
        for filename in os.listdir(dir_path):
            if filename == "meta.txt":
                meta = filename
        with open(os.path.join(dir_path, meta), 'r') as m:
            m.readline()
            m.readline()
            m.readline()
            self.width = int(m.readline().split(': ')[1])
            self.height = int(m.readline().split(': ')[1])
            m.readline()
            m.readline()
            self.frame_order = [int(x) for x in m.readline().split(': ')[1].split(' ')]
            m.readline()
            self.framerate = int(m.readline().split(': ')[1])
