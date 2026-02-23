import subprocess
import time
import sys


def run(cmd):
    print(">>", cmd)
    subprocess.run(cmd, shell=True, check=True)

def main():
    print("Test Simple Sim on + Key + Sim_Off!")
    
    run("python add07.py ps2 -p COM7 sim-on")
    #time.sleep(1)

    run("python add07.py ps2 -p COM7 key")
    time.sleep(60)

    run("python add07.py ps2 -p COM7 sim-off")
    #time.sleep(1)

    #print("Finish testing")

for i in range(1):
    print("Test Simple Sim on + Key + Sim_Off Iteration: " + str(i))
    main()

