import paddlex
from paddlex.cls import transforms
import cv2
import imutils
import numpy as np
import socket
import time


print("Starting socket: TCP...")
server_addr = ("192.168.10.106", 8888)
socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    try:
        print("Connecting to server")
        socket_tcp.connect(server_addr)
        break
    except Exception:
        print("Can't connect to server,try it latter!")
        time.sleep(1)
        continue

bg = None

train_transforms = transforms.Compose([
    transforms.RandomCrop(crop_size=224),
    transforms.Normalize()
])

model = paddlex.load_model('tools/model/epoch_50')
CLASSES = ['pause', 'up', 'down', 'left', 'right']
Commands = {'pause':'None', 'up':'Brightness Up', 'down':'Brightness Down', 'left':'Color Left', 'right':'Color Right'}


def run_avg(image, aWeight):
    global bg
    if bg is None:
        bg = image.copy().astype('float')
        return
    cv2.accumulateWeighted(image, bg, aWeight)

def segment(image, threshold=25):
    global bg
    diff = cv2.absdiff(bg.astype('uint8'), image)

    thresholded = cv2.threshold(diff,
                                threshold,
                                255,
                                cv2.THRESH_BINARY)[1]

    (cnts, _) = cv2.findContours(thresholded.copy(),
                                 cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)

    if len(cnts) == 0:
        return
    else:
        segmented = max(cnts, key=cv2.contourArea)
        return (thresholded, segmented)
def main():
    #action = 'pause'
    aWeight = 0.5

    video = "http://admin:admin@192.168.10.103:8081"
    camera = cv2.VideoCapture(video)

    top, right, bottom, left = 90, 380, 285, 590

    num_frames = 0
    thresholded = None

    count = 0
    sumscore = np.array([0,0,0,0,0])

    while(True):
        (grabbed, frame) = camera.read()
        if grabbed:
            frame = imutils.resize(frame, width=700)
            frame = cv2.flip(frame, 1)
            clone = frame.copy()

            roi = frame[top:bottom, right:left]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)

            if num_frames < 30:
                run_avg(gray, aWeight)
            else:
                hand = segment(gray)
                if hand is not None:
                    (thresholded, segmented) = hand
                    cv2.drawContours(clone, [segmented + (right, top)], -1, (0, 0, 255))

            cv2.rectangle(clone, (left, top), (right, bottom), (0, 255, 0), 2)

            num_frames += 1
            count += 1
            cv2.imshow('Video Feed', clone)

            if not thresholded is None:
                input_im = cv2.merge([thresholded, thresholded, thresholded])
                result = model.predict(input_im, topk=5, transforms=train_transforms)
                #action = result[0]['category']
                #cv2.putText(input_im, action, (0, 20),cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 255, 0), 2)

                layout = np.zeros(input_im.shape)
                final = []
                for clas in CLASSES:
                    for v in result:
                        if v['category'] == clas:
                            final.append(v['score'])
                            break

                sumscore = sumscore + np.array(final)
                if count%20==0:
                    print(sumscore)
                    sortarr = np.argsort(sumscore)
                    #if sumscore[sortarr[4]] > sumscore[sortarr[0]]+sumscore[sortarr[1]]+sumscore[sortarr[2]]+sumscore[sortarr[3]]:
                        #print(CLASSES[sortarr[4]])

                    gesture = CLASSES[0]
                    if sumscore[4]>8:
                        gesture = CLASSES[4]
                    elif sumscore[3]>8:
                        gesture = CLASSES[3]
                    elif sumscore[2]>15:
                        gesture = CLASSES[2]
                    elif sumscore[1]>15:
                        gesture = CLASSES[1]
                    sumscore = np.array([0, 0, 0, 0, 0])
                    command = Commands[gesture]
                    socket_tcp.send(command.encode())

                cv2.imshow('Thesholded', np.vstack([input_im, layout]))

            #press 'q' to quit
            keypress = cv2.waitKey(1) & 0xFF
            if keypress == ord('q'):
                break
        else:
            camera.release()
            break


main()
cv2.destroyAllWindows()
