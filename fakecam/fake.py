import os
import cv2
import numpy as np
import requests
import pyfakewebcam

def get_mask(frame, bodypix_url='http://etron-superfly:9000'):
    print("etm>1")    
    _, data = cv2.imencode(".jpg", frame)
    print("etm>1b")    
    r = requests.post(
        url=bodypix_url,
        data=data.tobytes(),
        headers={'Content-Type': 'application/octet-stream'})
    print("etm>2")    
    mask = np.frombuffer(r.content, dtype=np.uint8)
    print("etm>3")    
    mask = mask.reshape((frame.shape[0], frame.shape[1]))
    print("etm>4")    
    return mask

def post_process_mask(mask):
    mask = cv2.dilate(mask, np.ones((10,10), np.uint8) , iterations=1)
    mask = cv2.blur(mask.astype(float), (30,30))
    return mask

def shift_image(img, dx, dy):
    img = np.roll(img, dy, axis=0)
    img = np.roll(img, dx, axis=1)
    if dy>0:
        img[:dy, :] = 0
    elif dy<0:
        img[dy:, :] = 0
    if dx>0:
        img[:, :dx] = 0
    elif dx<0:
        img[:, dx:] = 0
    return img

def hologram_effect(img):
    # add a blue tint
    holo = cv2.applyColorMap(img, cv2.COLORMAP_WINTER)
    # add a halftone effect
    bandLength, bandGap = 2, 3
    for y in range(holo.shape[0]):
        if y % (bandLength+bandGap) < bandLength:
            holo[y,:,:] = holo[y,:,:] * np.random.uniform(0.1, 0.3)
    # add some ghosting
    holo_blur = cv2.addWeighted(holo, 0.2, shift_image(holo.copy(), 5, 5), 0.8, 0)
    holo_blur = cv2.addWeighted(holo_blur, 0.4, shift_image(holo.copy(), -5, -5), 0.6, 0)
    # combine with the original color, oversaturated
    out = cv2.addWeighted(img, 0.5, holo_blur, 0.6, 0)
    return out

def get_frame(cap, background_scaled):
    _, frame = cap.read()
    # fetch the mask with retries (the app needs to warmup and we're lazy)
    # e v e n t u a l l y c o n s i s t e n t
    mask = None
    while mask is None:
        try:
            mask = get_mask(frame)
        except requests.RequestException as err:
            print("mask request failed, retrying")
            #raise SystemExit(err)
    # post-process mask and frame
    mask = post_process_mask(mask)
    frame = hologram_effect(frame)
    # composite the foreground and background
    inv_mask = 1-mask
    for c in range(frame.shape[2]):
        frame[:,:,c] = frame[:,:,c]*mask + background_scaled[:,:,c]*inv_mask
    return frame

# setup access to the *real* webcam
cap = cv2.VideoCapture('/dev/video0')
height, width = 720, 1280
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cap.set(cv2.CAP_PROP_FPS, 60)

# setup the fake camera
fake = pyfakewebcam.FakeWebcam('/dev/video20', width, height)

# load the virtual background
background = cv2.imread("/data/background.jpg")
background_scaled = cv2.resize(background, (width, height))

# ==etm============================================================
# ==etm============================================================
###etm, printea
#success, frame = cap.read()
#cv2.imwrite("/data/test111.jpg", frame)

# ==etm============================================================
# ==etm============================================================




# frames forever
while True:
    success, frame = cap.read()

    #----------- 
    #tratar de imprimir tensoflow
    #cv2.imwrite("test.jpg", frame)
    #break

    #-----------
    #solo lee camara ==etm============================================================
    frame = hologram_effect(frame)

    #--- tratar de implementar tensorflow.........................
    #_, data = cv2.imencode(".jpg", frame)
    #bodypix_url='http://bodypix:9000'

    #r = requests.post(
    #        url=bodypix_url,
    #        data=data.tobytes(),
    #        headers={'Content-Type': 'application/octet-stream'})

    #print(r)
    # ==etm============================================================
    #obten chewaka
    #frame = get_frame(cap, background_scaled)
    #==etm============================================================
    
    
    # fake webcam expects RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    fake.schedule_frame(frame)
