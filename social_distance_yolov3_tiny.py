import cv2
import numpy as np
import random
import os
import time

net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny-custom-social.cfg")

distance_threshold = 50

cap = cv2.VideoCapture('humans.mp4')

frameWidth = int(cap.get(3))
frameHeight = int(cap.get(4))

size = (frameWidth, frameHeight)

fourcc = cv2.VideoWriter_fourcc(*"MJPG")
out = cv2.VideoWriter('output.avi', fourcc, 20.0, size, True)

def dist(pt1,pt2):
    try:
        return ((pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2)**0.5
    except:
        return

layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
 
ret = True

while ret:

    ret, img = cap.read()

    height, width = img.shape[:2]

    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    net.setInput(blob)
    outs = net.forward(output_layers)

    confidences = []
    boxes = []
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            if class_id!=0:
                continue
            confidence = scores[class_id]
            if confidence > 0.3:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)

                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    persons = []
    centroids = []
    violate = set()

    for i in range(len(boxes)):
        if i in indexes:
            x,y,w,h = boxes[i]
            persons.append(boxes[i])
            centroids.append([x+w//2, y+h//2])

    for i in range(len(persons)):
        for j in range(i+1, len(persons)):
            if dist(centroids[i], centroids[j]) <= distance_threshold:
                violate.add(tuple(persons[i]))
                violate.add(tuple(persons[j]))
    
    v = 0
    for (x,y,w,h) in persons:
        if (x,y,w,h) in violate:
            color = (0,0,255)
            v+=1
        else:
            color = (0,255,0)
        cv2.rectangle(img, (x,y), (x+w,y+h), color, 2)
        cv2.circle(img, (x+w//2,y+h//2), 2, (0,0,255), 2)

    cv2.putText(img,'No of Violations : '+str(v), (20, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1)

    out.write(img)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) == 27:
        break

cap.release()
out.release()

cv2.destroyAllWindows()
