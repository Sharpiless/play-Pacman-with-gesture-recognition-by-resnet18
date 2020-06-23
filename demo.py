import paddlex
from paddlex.cls import transforms
import cv2
import imutils
import numpy as np

bg = None

train_transforms = transforms.Compose([
    transforms.RandomCrop(crop_size=224),
    transforms.Normalize()
])

model = paddlex.load_model('weights/final')
CLASSES = ['pause', 'up', 'down', 'left', 'right']


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
    action = 'pause'
    aWeight = 0.5

    camera = cv2.VideoCapture(0)

    top, right, bottom, left = 90, 380, 285, 590

    num_frames = 0
    thresholded = None

    count = 0

    while(True):
        (grabbed, frame) = camera.read()
        if grabbed:

            frame = imutils.resize(frame, width=700)

            frame = cv2.flip(frame, 1)

            clone = frame.copy()

            (height, width) = frame.shape[:2]

            roi = frame[top:bottom, right:left]

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)

            if num_frames < 30:
                run_avg(gray, aWeight)
            else:
                hand = segment(gray)

                if hand is not None:
                    (thresholded, segmented) = hand

                    cv2.drawContours(
                        clone, [segmented + (right, top)], -1, (0, 0, 255))

            cv2.rectangle(clone, (left, top), (right, bottom), (0, 255, 0), 2)

            num_frames += 1

            cv2.imshow('Video Feed', clone)

            if not thresholded is None:

                input_im = cv2.merge(
                    [thresholded, thresholded, thresholded])
                result = model.predict(
                    input_im, topk=5, transforms=train_transforms)
                action = result[0]['category']
                cv2.putText(input_im, action, (0, 20),
                            cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 255, 0), 2)

                layout = np.zeros(input_im.shape)
                final = []
                for clas in CLASSES:
                    for v in result:
                        if v['category'] == clas:
                            final.append(v['score'])
                            break

                for (i, score) in enumerate(final):
                    # construct the label text
                    text = "{}: {:.2f}%".format(CLASSES[i], score * 100)

                    w = int(score * 300)
                    cv2.rectangle(layout, (7, (i * 35) + 5),
                                  (w, (i * 35) + 35), (0, 0, 255), -1)
                    cv2.putText(layout, text, (10, (i * 35) + 23),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                                (255, 255, 255), 2)

                cv2.imshow('Thesholded', np.vstack([input_im, layout]))

            keypress = cv2.waitKey(1) & 0xFF

            if keypress == ord('q'):
                break
        else:
            camera.release()
            break


main()
cv2.destroyAllWindows()
