import zlib
import base64
import tkinter as tk
from tkinter import filedialog


def compress(inp, out):
    with open(inp, 'r') as file:
        data = file.read()
    data_bytes = data.encode("utf-8")
    compressed_data = base64.b64encode(zlib.compress(data_bytes))
    with open(out, 'w') as compressed_file:
        compressed_file.write(compressed_data.decode("utf-8"))

def decompress(inp, out):
    with open(inp, 'r') as file:
        content = file.read()
    encoded_data = content.encode('utf-8')
    decompressed_data = zlib.decompress(base64.b64decode(encoded_data))
    with open(out, 'w') as file:
        file.write(decompressed_data.decode('utf-8'))

def compression():
    input_file = open_file()
    if input_file:
        compress(input_file, "compressed.txt")

def open_file():
    file = filedialog.askopenfilename(initialdir="/", title="Select a file to compress")
    return file

window = tk.Tk()
window.title("Compression")
window.geometry("600x400")

compress_button = tk.Button(window, text="Compress", command=compression)
compress_button.grid(row=0, column=0)

window.mainloop()