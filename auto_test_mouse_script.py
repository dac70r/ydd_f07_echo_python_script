import subprocess
import time
import sys

scan_codes = {
    'a': '1C', 'b': '32', 'c': '21', 'd': '23', 'e': '24', 'f': '2B', 'g': '34',
    'h': '33', 'i': '43', 'j': '3B', 'k': '42', 'l': '4B', 'm': '3A', 'n': '31',
    'o': '44', 'p': '4D', 'q': '15', 'r': '2D', 's': '1B', 't': '2C', 'u': '3C',
    'v': '2A', 'w': '1D', 'x': '22', 'y': '35', 'z': '1A',
    '0': '45', '1': '16', '2': '1E', '3': '26', '4': '25', '5': '2E', '6': '36',
    '7': '3D', '8': '3E', '9': '46',
    ' ': '29', '\\': '5D', '{':'54', '}':'5B', 
    '+': '55', '!': '16', '#': '26', '|': '5D',
    '@': '1E', '$': '25', '%': '2E', '^': '36',
    '&': '3D', '*': '3E', '(': '46', ')': '45',
    ',': '41', '.': '49', '/': '4A', ';': '4C', "'": '52',
    '=': '55', '-': '4E',
}

lines = [
    "+hello",
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
        if char.isupper() or char in "+!#@$%|^&*()":
            run("python add07.py ps2 -p COM25 type 12,0")    
            time.sleep(0.05)  # inter-key delay

        run_ps2_type(code)

        # handle shiftdown for uppercase / special
        if char.isupper() or char in "+!#@$%^&*()":
            run("python add07.py ps2 -p COM25 type 12,1")
            time.sleep(0.05)  # inter-key delay

def movement_square():
    i = 0
    while i < 5:
        run("python add07.py ps2 -p COM25 move 0 -40")
        i = i + 1
    i = 0

    while i < 5:
        run("python add07.py ps2 -p COM25 move 40 0")
        i = i + 1
    i = 0

    while i < 5:
        run("python add07.py ps2 -p COM25 move 0 40")
        i = i + 1
    i = 0

    while i < 5:
        run("python add07.py ps2 -p COM25 move -40 0")
        i = i + 1
    i = 0

def double_left_click():
    run("python add07.py ps2 -p COM25 move 0 0 --left")
    run("python add07.py ps2 -p COM25 move 0 0 ")
    run("python add07.py ps2 -p COM25 move 0 0 --left")
    run("python add07.py ps2 -p COM25 move 0 0 ")

# right click press down
def example():
    i = 0
    while i < 5:
        run("python add07.py ps2 -p COM25 move 0 -10 --left")
        i = i + 1
    i = 0

    # move right to empty space
    while i < 5:
        run("python add07.py ps2 -p COM25 move 10 0")
        i = i + 1
    i = 0

    # move right to cancel selected
    run("python add07.py ps2 -p COM25 move 0 0 --left")

    # right click
    run("python add07.py ps2 -p COM25 move 0 0 --right")
    run("python add07.py ps2 -p COM25 move 0 0")

    # move right 2 spaces
    while i < 2:
        run("python add07.py ps2 -p COM25 move 10 0")
        i = i + 1
    i = 0

    # move down 4 spaces
    while i < 7:
        run("python add07.py ps2 -p COM25 move 0 -8")
        i = i + 1
    i = 0

    # click on select
    run("python add07.py ps2 -p COM25 move 0 0 --left")
    run("python add07.py ps2 -p COM25 move 0 0")

    
    i = 0
    while i < 12:
        run("python add07.py ps2 -p COM25 move -10 0")
        run("python add07.py ps2 -p COM25 move 0 -10")
        i = i + 1
    i = 0
    run("python add07.py ps2 -p COM25 move 0 -10")
    run("python add07.py ps2 -p COM25 move 0 -10")

    run("python add07.py ps2 -p COM25 move 0 0 --left")
    run("python add07.py ps2 -p COM25 move 0 0")

    # mouse wheel operation (cannot be tested, no ps2 mouse with wheel)
    #while i < 7:
        #run("python add07.py ps2 -p COM25 move 0 0 --wheel -1")
        #i = i + 1
    #i = 0



    


print("Now testing for Mouse Functionality!")

run("python add07.py ps2 -p COM25 sim-on")
run("python add07.py ps2 -p COM25 mouse")

movement_square()
double_left_click()
example()

run("python add07.py ps2 -p COM25 sim-off")

print("Finish testing")

# proceed to run keyboard functions 
run("python auto_test_keyboard_script.py")
