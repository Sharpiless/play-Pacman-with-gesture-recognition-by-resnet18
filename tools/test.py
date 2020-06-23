from paddlex.cls import transforms
import paddlex
import cv2

train_transforms = transforms.Compose([
    transforms.RandomCrop(crop_size=224),
    transforms.Normalize()
])

model = paddlex.load_model('weights/final')
im = cv2.imread('test.jpg')
result = model.predict(im, topk=3, transforms=train_transforms)
print("Predict Result:", result)
