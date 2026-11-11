import os

image_dir = "."
with open("list", "r") as file:
    for line in file:
            clean_line = line.strip()
            print(clean_line)