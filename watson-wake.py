import snowboydecoder
import sys
import signal
import os
import requests
import os.path
import time

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
print('Listening... Press Ctrl+C to exit')

def detected_callback():
  print "start"
  detector.terminate()

  TOP_DIR = os.path.dirname(os.path.abspath(__file__))
  DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
  os.system("aplay " + DETECT_DING + " > /dev/null 2>&1")

  flag=True
  while flag:
    os.system("arecord -r 32000 -d 2 /home/pi/temp/out.wav")
    requests.get('http://localhost:1880/test')

    counter=0
    flag=False

    while True:
      file = open('/proc/asound/card0/pcm0p/sub0/status', 'r')
      status = file.readline()
      print "*** audio status: " + status
    
      if status.find("closed")>-1:
        counter+=1
      if counter>10:
        flag=False
        break
      if status.find("RUNNING")>-1:
        flag=True
      if flag==True and status.find("closed")>-1:
        break
      time.sleep(1)

  os.execv(sys.executable, ['python'] + sys.argv)

# main loop
detector.start(detected_callback=detected_callback,
                interrupt_check=interrupt_callback,
                sleep_time=0.03)
detector.terminate()
