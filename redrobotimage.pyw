import os
from PIL import Image

INPUT_FILE = "InBoxRedO.txt"
IMAGE_FOLDER = "ImageDB"
OUTPUT_FOLDER = "ImageOverlay"
OUTPUT_FILENAME = "redsquarerobot.png"

def get_robot_name(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.readline().strip()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None

def find_and_convert_image(robot_name, output_filename):
    if not robot_name:
        return
    for file in os.listdir(IMAGE_FOLDER):
        if file.lower().startswith(robot_name.lower()) and file.lower().endswith(('.png', '.jpg', '.jpeg')):
            src_path = os.path.join(IMAGE_FOLDER, file)
            dst_path = os.path.join(OUTPUT_FOLDER, output_filename)
            try:
                with Image.open(src_path) as img:
                    img.convert("RGBA").save(dst_path, format="PNG")
                print(f"Converted and saved '{src_path}' as '{dst_path}'")
            except Exception as e:
                print(f"Failed to convert image: {e}")
            return
    print(f"No image found for robot: '{robot_name}'")

if __name__ == "__main__":
    name = get_robot_name(INPUT_FILE)
    find_and_convert_image(name, OUTPUT_FILENAME)
