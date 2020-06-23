from paddlex.cls import transforms
import os
import cv2
import numpy as np
import paddlex as pdx

base = './data'

with open(os.path.join('train_list.txt'), 'w') as f:
    for i, cls_fold in enumerate(os.listdir(base)):
        cls_base = os.path.join(base, cls_fold)
        files = os.listdir(cls_base)
        print('{} train num:'.format(cls_fold), len(files))
        for pt in files:
            img = os.path.join(cls_fold, pt)
            info = img + ' ' + str(i) + '\n'
            f.write(info)

with open(os.path.join('labels.txt'), 'w') as f:
    for i, cls_fold in enumerate(os.listdir(base)):
        f.write(cls_fold+'\n')

train_transforms = transforms.Compose([
    transforms.RandomCrop(crop_size=224),
    transforms.Normalize()
])

train_dataset = pdx.datasets.ImageNet(
    data_dir=base,
    file_list='train_list.txt',
    label_list='labels.txt',
    transforms=train_transforms,
    shuffle=True)

num_classes = len(train_dataset.labels)
model = pdx.cls.ResNet18(num_classes=num_classes)
model.train(num_epochs=20,
            train_dataset=train_dataset,
            train_batch_size=32,
            lr_decay_epochs=[5, 10, 15],
            learning_rate=2e-2,
            save_dir='w',
            log_interval_steps=5,
            save_interval_epochs=4)

im = cv2.imread('test.jpg')
result = model.predict('test.jpg', topk=1, transforms=train_transforms)
print("Predict Result:", result)