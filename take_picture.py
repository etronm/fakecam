import cv2
import requests
import numpy as np

cap = cv2.VideoCapture('/dev/video0')

# configure camera for 720p @ 60 FPS
height, width = 720, 1280
cap.set(cv2.CAP_PROP_FRAME_WIDTH ,width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
cap.set(cv2.CAP_PROP_FPS, 60)

#while True:
#    success, frame = cap.read()

success, frame = cap.read()
#cv2.imwrite("test.jpg", frame)

####################################################

_, data = cv2.imencode(".jpg", frame)
bodypix_url='http://etron-superfly:9000'

mask = None
while mask is None:
    try:
        print("etm>1")
        r = requests.post(
            url=bodypix_url,
            data=data.tobytes(),
            headers={'Content-Type': 'application/octet-stream'})
        mask = np.frombuffer(r.content, dtype=np.uint8)
        print("etm>3")    
        mask = mask.reshape((frame.shape[0], frame.shape[1]))
    except requests.RequestException as err:
        print("mask request failed, retrying")
        #raise SystemExit(err)

print("etm>2")
cv2.imwrite("test2.jpg", mask)
cv2.imwrite("test.jpg", frame)
