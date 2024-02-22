import logging
import subprocess
import os
import sys
import argparse
from metadata.meta_data import FlipperMetaData
from PIL import Image, ImageOps

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

def reconstruct_xbm_structure(data, width, height):
    structure = ""
    structure += f"#define t_width {width}\n"
    structure += f"#define t_height {height}\nstatic char t_bits[] = "
    structure += "{"
    for byte in data:
        str_byte = hex(byte)
        if len(str_byte) < 4:
            _, succ = str_byte.split('x')
            str_byte = '0x0' + succ

        structure += f"{str_byte}, "
    structure += "};"
    return structure


class ImageTools:
    __pil_unavailable = False
    __hs2_unavailable = False

    def __init__(self):
        self.logger = logging.getLogger()

    def hs2xbm(self, data):
        if self.__hs2_unavailable:
            return subprocess.check_output(
                ["heatshrink", "-d", "-w8", "-l4"], input=data
            )

        try:
            import heatshrink2
        except ImportError:
            self.__hs2_unavailable = True
            self.logger.info("heatshrink2 module is missing, using heatshrink cli util")
            return self.hs2xbm(data)

        return heatshrink2.decompress(data, window_sz2=8, lookahead_sz2=4)

    def xbm2png(self, width, height, data, filename):
        try:
            im = Image.frombytes('1', (width, height), data, decoder_name='xbm')
            im = ImageOps.invert(im)
            im.save(filename, 'PNG')
        except Exception as e:
            self.logger.error(f"Error converting XBM to PNG: {e}")

def bm2png(file, output_filename):
    tools = ImageTools()

    with open(file, "rb") as f:
        compression_flag = f.read(1)
        # width, height = f.read(2), f.read(2)
        # width = int.from_bytes(width, "big")
        # height = int.from_bytes(height, "big")
        width, height = 128, 64
        data = f.read()

    if compression_flag == b'\x01':  # Data is compressed
        # data = decode_data(data)
        data = data[3:]
        data = tools.hs2xbm(data)
    elif compression_flag == b'\x00':  # Data is raw
        # No decompression needed
        pass
    else:
        raise ValueError("Unknown compression flag")

    tools.xbm2png(width, height, bytearray(reconstruct_xbm_structure(data,128,64), encoding='utf-8'), output_filename)

def find_file(directory, filename):
        # List all files and directories in the specified directory
    for item in os.listdir(directory):
        # Construct the full path to the item
        item_path = os.path.join(directory, item)
        # Check if the item is a file and matches the filename we're looking for
        if os.path.isfile(item_path) and item == filename:
            return item  # Return the full path to the file if found
    return None  # Return None if the file was not found

def convert_bm_to_png(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(".bm"):
            source_path = os.path.join(directory_path, filename)
            output_path = os.path.join(directory_path, filename.replace(".bm", ".png"))
            bm2png(source_path, output_path)

def create_gif_from_png(directory_path, gif_name):
    metadata = FlipperMetaData(directory_path)
    images = []
    count = 0
    for i in metadata.frame_order:
        filename = find_file(directory_path, f"frame_{i}.png") 
        if filename is None:
            continue
        if filename.endswith(".png"):
            img_path = os.path.join(directory_path, filename)
            images.append(Image.open(img_path))
        if images:
            images[0].save(gif_name, save_all=True, append_images=images[1:], duration=(1/6)*1000, loop=0)
        count += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Flipper Animation Compiler", description="Takes a directory of a flipper animation and converts it to a gif")
    parser.add_argument('directory', nargs='+', type=str)
    parser.add_argument('-o', '--output', type=str, default='output.gif')
    parser.add_argument('-r', '--remove', type=int, default=0)
    args = parser.parse_args()
    count = 0
    for dir in args.directory:
        directory_path = dir
        convert_bm_to_png(directory_path)
        if count == 0:
            create_gif_from_png(directory_path, args.output)
        else:
            create_gif_from_png(directory_path, f"{count}_{args.output}")
        count += 1
