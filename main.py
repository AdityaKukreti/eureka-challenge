import subprocess
import cv2
import time

adb_connect = subprocess.Popen('adb connect 192.168.29.82:24', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, error = adb_connect.communicate()

if error:
    print(f"Error connecting to device: {error.decode('utf-8')}")
    exit(1)

screen_mirror = subprocess.Popen('adb shell screenrecord --bit-rate=8m --output-format=h264 - | ffplay -framerate 60 -', shell=True)

mouse_down = False
start_x, start_y = 0, 0
last_frame_time = 0
new_frame_time = 0
min_frame_time = 1 / 10  

window_width = 450  
window_height = 800  

def mouse_callback(event, x, y, flags, param):
    global mouse_down, start_x, start_y

    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_down = True
        start_x, start_y = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        mouse_down = False

        device_width, device_height = img.shape[1], img.shape[0]
        tap_x = int((x / window_width) * device_width)
        tap_y = int((y / window_height) * device_height)

     
        subprocess.Popen(f'adb shell input tap {tap_x} {tap_y}', shell=True)
    elif event == cv2.EVENT_MOUSEMOVE and mouse_down:
      
        device_width, device_height = img.shape[1], img.shape[0]
        start_x_device = int((start_x / window_width) * device_width)
        start_y_device = int((start_y / window_height) * device_height)
        end_x_device = int((x / window_width) * device_width)
        end_y_device = int((y / window_height) * device_height)

      
        subprocess.Popen(f'adb shell input swipe {start_x_device} {start_y_device} {end_x_device} {end_y_device} 500', shell=True)

      
        start_x, start_y = x, y
    elif event == cv2.EVENT_MOUSEWHEEL:
     
        scroll_amount = flags // 120  # One wheel step is 120 units

       
        if scroll_amount > 0:
           
            subprocess.Popen(f'adb shell input swipe {int(img.shape[1]/2)} {int(img.shape[0]*0.9)} {int(img.shape[1]/2)} {int(img.shape[0]*0.1)} {abs(scroll_amount*500)}', shell=True)
        else:
           
            subprocess.Popen(f'adb shell input swipe {int(img.shape[1]/2)} {int(img.shape[0]*0.1)} {int(img.shape[1]/2)} {int(img.shape[0]*0.9)} {abs(scroll_amount*500)}', shell=True)

while True:
    try:
       
        output, error = subprocess.Popen('adb exec-out screencap -p > screen.png', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


        if error:
            print(f"Error capturing screen: {error.decode('utf-8')}")
            continue

   
        img = cv2.imread('screen.png')


        img = cv2.resize(img, (window_width, window_height))

        cv2.imshow('Android Screen', img)

        cv2.setMouseCallback('Android Screen', mouse_callback)

        new_frame_time = time.time()
        frame_time = new_frame_time - last_frame_time
        fps = 1 / frame_time
        last_frame_time = new_frame_time
        print(f"FPS: {int(fps)}")

        if frame_time < min_frame_time:
            time.sleep(min_frame_time - frame_time)

        key = cv2.waitKey(max(1, int(1000 / 60)))
    except cv2.error as e:
        print(f"OpenCV error: {e}")
        break

    if key == ord('h'):
        subprocess.Popen('adb shell input keyevent 123', shell=True)  # Left
    elif key == ord('l'):
        subprocess.Popen('adb shell input keyevent 124', shell=True)  # Right
    elif key == ord('k'):
        subprocess.Popen('adb shell input keyevent 19', shell=True)  # Up
    elif key == ord('j'):
        subprocess.Popen('adb shell input keyevent 20', shell=True)  # Down
    elif key == ord('q'):
        break

screen_mirror.terminate()

cv2.destroyAllWindows()
