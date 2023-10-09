import cv2
import dlib
import face_recognition

detector = dlib.get_frontal_face_detector()
cap = cv2.VideoCapture(0)

while(True):
    ret, frame = cap.read()
    dets = face_recognition.face_locations(frame, model="cnn")
    print("face_recognition:",dets)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    dets = detector(gray, 1)
    
    for i, d in enumerate(dets):
        print("dlib: Left: {} Top: {} Right: {} Bottom: {}".format(
            d.left(), d.top(), d.right(), d.bottom()))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break