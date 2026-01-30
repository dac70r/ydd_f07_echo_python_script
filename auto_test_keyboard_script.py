import subprocess
import time
import sys

scan_codes = {
    'a': '1C', 'b': '32', 'c': '21', 'd': '23', 'e': '24', 'f': '2B', 'g': '34',
    'h': '33', 'i': '43', 'j': '3B', 'k': '42', 'l': '4B', 'm': '3A', 'n': '31',
    'o': '44', 'p': '4D', 'q': '15', 'r': '2D', 's': '1B', 't': '2C', 'u': '3C',
    'v': '2A', 'w': '1D', 'x': '22', 'y': '35', 'z': '1A',
    '0': '45', '1': '16', '2': '1E', '3': '26', '4': '25', '5': '2E', '6': '36',
    '7': '3D', '8': '3E', '9': '46', ':': '4C', '`': '0E', '~': '0E',
    ' ': '29', '\\': '5D', '[':'54', ']': '5B', '{': '54', '}': '5B', 
    '+': '55', '!': '16', '#': '26', '|': '5D',
    '@': '1E', '$': '25', '%': '2E', '^': '36',
    '&': '3D', '*': '3E', '(': '46', ')': '45',
    ',': '41', '.': '49', '/': '4A', ';': '4C', "'": '52', '"' : '52',
    '=': '55', '-': '4E', '_': '4E', '<': '41', '>': '49', '?': '4A',
}
lines_kunlun = ["+hello",
    "HELLO",
    "Hello",
    "HeLLo",
    "123",
    "Hello123",
    "Hello World",
    "a b c",
    "!",
    "@",
    "#",
    "$",
    "%",
    "!@#$%",
    "^&*()",
    "-",
    "=",
    "-=",
    "Hello World!",
    "Hello Everest! Good Afternoon@Every One",
    "test@example.com",
    "Price: $99.99",
    "C:\\Users\\Admin",
    "Username",
    "admin",
    "Password",
    "123456"
]

lines = [
    "Stress Testing Dennis",
    "`1234567890-=",
    "~!@#$%^&*()_+",
    "qwertyuiop[]\\",
    "QWERTYUIOP{}|",
    "asdfghjkl;'",
    "ASDFGHJKL:\"",
    "zxcvbnm,./",
    "ZXCVBNM<>?"
]

COM_PORT = "COM25"

def run(cmd):
    print(">>", cmd)
    subprocess.run(cmd, shell=True, check=True)

def run_ps2_type(keycode):
    subprocess.run([sys.executable, "add07.py", "ps2", "type", keycode], check=True)

def send_string(text):
    for char in text:
        code = scan_codes.get(char.lower())
        if code is None:
            print(f"[WARN] No mapping for '{char}'")
            continue

        # handle shiftup for uppercase / special
        if char.isupper() or char in '+!#@$%|^&*():"~<>?{}?':
            run("python add07.py ps2 -p COM25 type 12,0")    
            #time.sleep(0.05)  # inter-key delay

        run_ps2_type(code)

        # handle shiftdown for uppercase / special
        if char.isupper() or char in '+!#@$%|^&*():~<>"{}?':
            run("python add07.py ps2 -p COM25 type 12,1")
            #time.sleep(0.05)  # inter-key delay

run("python add07.py ps2 -p COM25 sim-on")

run("python add07.py ps2 -p COM25 key")
time.sleep(2)         # delay to allow us to capture echo sent by host

print("Now testng for Keyboard Functionality!")

for line in lines:
    send_string(line)
    run("python add07.py ps2 -p COM25 type 5A")      #space
    #time.sleep(0.1)  # inter-line delay

run("python add07.py ps2 -p COM25 sim-off")

print("Finish testing")
