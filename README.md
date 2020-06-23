# PaddlePaddle实现手势识别玩转吃豆豆！

![](https://ai-studio-static-online.cdn.bcebos.com/2207b0c19f2944cd997f003f3ddb8b8fc735d852ba584d1dadb12bb5c94d0697)


## 文章目录：

### 1. 手势数据采集
### 2. PaddleX训练模型
### 3. 测试手势识别模型
### 4. 测试游戏种手势控制
### 5. 大功告成~


```python
# 解压代码
!unzip /home/aistudio/data/data41298/code.zip -d /home/aistudio/work/
```


```python
!pip install paddlex
```

拳头表示向下走：

![](https://ai-studio-static-online.cdn.bcebos.com/968be5f9b32f4840a0c3d7d4fd477359a6a41afec8cb400f81557827ae65b5de)

手掌表示向上走：

![](https://ai-studio-static-online.cdn.bcebos.com/a380aea8ff944a9fbc6f3677fb90b418aa8e05fdf6c1419495e1ad8cd49aa613)

下面两个分别是向左和向右：

![](https://ai-studio-static-online.cdn.bcebos.com/3b1a1c71eb9941e7ba41cc11cc3444f3994c17b8373f4d81b7ec7d8b18013e8f)
![](https://ai-studio-static-online.cdn.bcebos.com/0155857100374323bf167f0fdb90973e1ef9b0f4880d408080e5e83a1d740397)

空白表示按位不动：

![](https://ai-studio-static-online.cdn.bcebos.com/f0d252786c2a428abc721c786b53d0244ca803b928f541dc8b2cbb5085f204b2)



```python
# 设置工作路径
import os
os.chdir('/home/aistudio/work/Pacman-master/')
```

## 1. 手势数据采集：

这一步需要在本地运行collect文件夹下PalmTracker.py文件进行手势数据采集；

运行该程序时会打开摄像头，在指定区域做出手势，按s保存；

![](https://ai-studio-static-online.cdn.bcebos.com/06c664b20f794a4da1d3cffc5c57aad616dc037a5c8542fa802c879bb67fdac9)



```python
# !python collect/PalmTracker.py
```

    collect    data     game.py  pacman.py	test.jpg  utils.py
    config.py  demo.py  images   src	tools	  weights


## 2. PaddleX训练模型

这一步使用PaddleX提供的ResNet18进行训练；

预训练模型使用在'IMAGENET'上训练的权重，PaddleX选择参数 pretrain_weights='IMAGENET' 即可；

我这里每种手势共收集了40张左右，训练结果准确率在93%以上；

### 2.1 定义数据集


```python
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
```

### 2.2 使用ResNet18训练模型

此处训练20个epoch，初始学习率为2e-2


```python
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
```

## 3 测试手势识别模型：


```python
from paddlex.cls import transforms
import matplotlib.pyplot as plt
import paddlex
import cv2
import warnings

warnings.filterwarnings('ignore')

train_transforms = transforms.Compose([
    transforms.RandomCrop(crop_size=224),
    transforms.Normalize()
])

model = paddlex.load_model('weights/final')
im = cv2.imread('test.jpg')
result = model.predict(im, topk=1, transforms=train_transforms)
print("Predict Result:", result)

%matplotlib inline
plt.imshow(im)
plt.show()
```

    2020-06-23 09:27:29 [INFO]	Model[ResNet18] loaded.
    Predict Result: [{'category_id': 1, 'category': 'left', 'score': 0.9999609}]



![png](output_13_1.png)


## 4. 测试游戏中手势控制：

本地运行demo.py即可；

![](https://ai-studio-static-online.cdn.bcebos.com/39bb2143fff544e0b553e5499ec7f3f49346affa73b94f42902d2314b9d9c47d)



```python
!python demo.py
```

## 5. 大功告成

然后将该控制嵌入到游戏中即可~

游戏代码来自：https://github.com/hbokmann/Pacman


```python
!python game.py
```

![](https://ai-studio-static-online.cdn.bcebos.com/0f06ca2879024729a5f3411a4c7fac5d370e1b7ce4754833b084b624de9187c2)


### 演示视频我放到Youtube了（因为B站审核太慢了，，，）

链接地址：[https://youtu.be/tlZT2WeaK1U](https://youtu.be/tlZT2WeaK1U)

## 更新，B站审核通过啦！

链接地址：[https://www.bilibili.com/video/BV1xa4y1Y7Mb/](https://www.bilibili.com/video/BV1xa4y1Y7Mb/)

## 关于作者：
> 北京理工大学 大二在读

> 感兴趣的方向为：目标检测、人脸识别、EEG识别等

> 将会定期分享一些小项目，感兴趣的朋友可以互相关注一下：[主页链接](http://aistudio.baidu.com/aistudio/personalcenter/thirdview/67156)

> 也欢迎大家fork、评论交流

> 作者博客主页：[https://blog.csdn.net/weixin_44936889](https://blog.csdn.net/weixin_44936889)

