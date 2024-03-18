import subprocess
import cv2
import time

# Connect to the Android device
adb_connect = subprocess.Popen('adb connect 192.168.29.82:24', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, error = adb_connect.communicate()

# Check if the connection was successful
if error:
    print(f"Error connecting to device: {error.decode('utf-8')}")
    exit(1)

# Start screen mirroring
screen_mirror = subprocess.Popen('adb shell screenrecord --bit-rate=8m --output-format=h264 - | ffplay -framerate 60 -', shell=True)

# Control the device
mouse_down = False
start_x, start_y = 0, 0
last_frame_time = 0
new_frame_time = 0
min_frame_time = 1 / 10  # Minimum frame time for 10 FPS

# Window size variables
window_width = 450  # Adjust this value to change the window width
window_height = 800  # Adjust this value to change the window height

def mouse_callback(event, x, y, flags, param):
    global mouse_down, start_x, start_y

    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_down = True
        start_x, start_y = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        mouse_down = False

        # Calculate the tap coordinates based on the screen resolution
        device_width, device_height = img.shape[1], img.shape[0]
        tap_x = int((x / window_width) * device_width)
        tap_y = int((y / window_height) * device_height)

        # Send the tap command to the device
        subprocess.Popen(f'adb shell input tap {tap_x} {tap_y}', shell=True)
    elif event == cv2.EVENT_MOUSEMOVE and mouse_down:
        # Calculate the swipe coordinates based on the screen resolution
        device_width, device_height = img.shape[1], img.shape[0]
        start_x_device = int((start_x / window_width) * device_width)
        start_y_device = int((start_y / window_height) * device_height)
        end_x_device = int((x / window_width) * device_width)
        end_y_device = int((y / window_height) * device_height)

        # Send the swipe command to the device
        subprocess.Popen(f'adb shell input swipe {start_x_device} {start_y_device} {end_x_device} {end_y_device} 500', shell=True)

        # Update the start coordinates
        start_x, start_y = x, y
    elif event == cv2.EVENT_MOUSEWHEEL:
        # Calculate the scroll amount based on the wheel delta
        scroll_amount = flags // 120  # One wheel step is 120 units

        # Send the scroll command to the device
        if scroll_amount > 0:
            # Scroll down
            subprocess.Popen(f'adb shell input swipe {int(img.shape[1]/2)} {int(img.shape[0]*0.9)} {int(img.shape[1]/2)} {int(img.shape[0]*0.1)} {abs(scroll_amount*500)}', shell=True)
        else:
            # Scroll up
            subprocess.Popen(f'adb shell input swipe {int(img.shape[1]/2)} {int(img.shape[0]*0.1)} {int(img.shape[1]/2)} {int(img.shape[0]*0.9)} {abs(scroll_amount*500)}', shell=True)

while True:
    try:
        # Get the screen capture from the device
        output, error = subprocess.Popen('adb exec-out screencap -p > screen.png', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        # Check for errors
        if error:
            print(f"Error capturing screen: {error.decode('utf-8')}")
            continue

        # Load the screen capture as an OpenCV image
        img = cv2.imread('screen.png')

        # Resize the image to fit the window
        img = cv2.resize(img, (window_width, window_height))

        # Display the screen capture
        cv2.imshow('Android Screen', img)

        # Set the mouse callback function
        cv2.setMouseCallback('Android Screen', mouse_callback)

        # Calculate the frame rate
        new_frame_time = time.time()
        frame_time = new_frame_time - last_frame_time
        fps = 1 / frame_time
        last_frame_time = new_frame_time
        print(f"FPS: {int(fps)}")

        # Limit the frame rate to minimum 10 FPS
        if frame_time < min_frame_time:
            time.sleep(min_frame_time - frame_time)

        # Send commands to the device based on user input
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

# Stop screen mirroring
screen_mirror.terminate()

# Release the OpenCV window
cv2.destroyAllWindows()
