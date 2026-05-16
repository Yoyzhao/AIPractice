# Day 1 - 基础知识学习内容

> 2026年浙江省人工智能训练师竞赛 - 第1天学习计划

---

## 学习目标

1. 掌握Python数据处理三件套（NumPy、Pandas、OpenCV）
2. 掌握图像标注工具Label-Studio的使用
3. 掌握PyTorch深度学习框架基础

**总目标**：能够独立完成图像采集、标注、格式转换的完整流程

---

## 上午时段：Python数据处理基础（9:00-12:00）

### 1.1 NumPy数值计算基础

#### 核心概念
- ** ndarray**：多维数组对象，Numpy的核心数据结构
- ** 广播机制**：不同形状数组之间的运算规则
- ** 索引与切片**：高效访问和修改数组元素

#### 必须掌握的代码

```python
import numpy as np

# 创建数组
arr1 = np.array([1, 2, 3, 4, 5])                    # 一维数组
arr2 = np.array([[1, 2, 3], [4, 5, 6]])             # 二维数组
arr3 = np.zeros((3, 4))                             # 全零数组
arr4 = np.ones((2, 3))                              # 全一数组
arr5 = np.arange(0, 10, 2)                          # 范围数组
arr6 = np.random.randn(3, 3)                        # 随机数组

# 基本属性
print(arr2.shape)    # 形状 (2, 3)
print(arr2.dtype)    # 数据类型
print(arr2.ndim)     # 维度

# 索引与切片
print(arr2[0, 0])     # 第一个元素
print(arr2[1, :])     # 第二行所有元素
print(arr2[:, 2])     # 第三列所有元素

# 运算
arr_a = np.array([1, 2, 3])
arr_b = np.array([4, 5, 6])
print(arr_a + arr_b)       # 元素相加
print(arr_a * arr_b)       # 元素相乘
print(np.dot(arr_a, arr_b)) # 点积

# 形状变换
arr = np.array([[1, 2], [3, 4], [5, 6]])
print(arr.reshape(2, 3))   # 改变形状
print(arr.flatten())       # 展平为一维
```

#### 练习任务
1. 创建5x5的单位矩阵
2. 实现两个矩阵的矩阵乘法
3. 找出数组中的最大值、最小值及其索引

---

### 1.2 Pandas数据处理基础

#### 核心概念
- ** DataFrame**：二维表格数据结构，类似Excel/SQL表
- ** Series**：一维标签数组，类似DataFrame的一列
- ** 索引操作**：行索引、列索引、条件筛选

#### 必须掌握的代码

```python
import pandas as pd

# 创建DataFrame
data = {
    'image_name': ['img001.jpg', 'img002.jpg', 'img003.jpg'],
    'width': [1920, 1280, 640],
    'height': [1080, 720, 480],
    'label': ['car', 'pedestrian', 'traffic_sign']
}
df = pd.DataFrame(data)

# 基本操作
print(df.head())          # 查看前几行
print(df.info())          # 数据类型信息
print(df.describe())      # 统计描述
print(df.shape)           # 形状
print(df.columns)         # 列名
print(df.dtypes)          # 列类型

# 索引与选择
print(df['image_name'])                    # 选择单列
print(df[['image_name', 'label']])         # 选择多列
print(df.iloc[0])                          # 位置索引
print(df.iloc[0:2])                        # 切片
print(df.loc[0, 'image_name'])             # 标签索引

# 条件筛选
print(df[df['width'] > 1000])              # 宽度大于1000的行
print(df[(df['label'] == 'car') | (df['label'] == 'pedestrian')])

# 数据修改
df['new_column'] = df['width'] / df['height']  # 添加新列
df = df.drop('new_column', axis=1)             # 删除列
df = df.rename(columns={'image_name': 'filename'})  # 重命名列

# 数据保存与读取
df.to_csv('annotations.csv', index=False)     # 保存为CSV
df.to_json('annotations.json')                # 保存为JSON
df = pd.read_csv('annotations.csv')           # 读取CSV
```

#### 练习任务
1. 创建一个包含100张图像信息的数据表（文件名、宽、高、类别）
2. 筛选出所有车辆类别的图像
3. 统计每个类别的图像数量
4. 将处理后的数据导出为CSV和JSON格式

---

### 1.3 OpenCV图像处理基础

#### 核心概念
- ** BGR格式**：OpenCV默认颜色通道顺序（蓝、绿、红）
- ** 色彩空间**：RGB、HSV、灰度图之间的转换
- ** 几何变换**：缩放、旋转、翻转、裁剪

#### 必须掌握的代码

```python
import cv2
import numpy as np

# 读取与显示图像
img = cv2.imread('image.jpg')           # 读取图像（BGR格式）
cv2.imshow('image', img)               # 显示图像
cv2.waitKey(0)                          # 等待按键
cv2.destroyAllWindows()                 # 关闭所有窗口

# 保存图像
cv2.imwrite('output.jpg', img)

# 获取图像信息
print(img.shape)    # (高度, 宽度, 通道数)
print(img.dtype)    # 数据类型
print(img.size)     # 像素总数

# 颜色空间转换
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)      # BGR转灰度
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)        # BGR转RGB
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)        # BGR转HSV

# 几何变换
resized = cv2.resize(img, (640, 480))              # 缩放
rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) # 旋转
flipped = cv2.flip(img, 1)                         # 翻转（1水平，0垂直）

# 裁剪
h, w = img.shape[:2]
cropped = img[h//4:3*h//4, w//4:3*w//4]

# 绘制图形
cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 矩形
cv2.circle(img, (cx, cy), radius, (0, 0, 255), 2)      # 圆
cv2.putText(img, 'text', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# 模糊处理
blurred = cv2.GaussianBlur(img, (5, 5), 0)

# 边缘检测
edges = cv2.Canny(img, 100, 200)

# 形态学操作
kernel = np.ones((5, 5), np.uint8)
dilated = cv2.dilate(edges, kernel, iterations=1)   # 膨胀
eroded = cv2.erode(dilated, kernel, iterations=1) # 腐蚀

# 图像采集（摄像头）
cap = cv2.VideoCapture(0)                         # 打开摄像头
while True:
    ret, frame = cap.read()                        # 读取帧
    if not ret:
        break
    cv2.imshow('camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):         # 按q退出
        break
cap.release()
cv2.destroyAllWindows()

# 保存视频/连续帧
for i in range(100):
    cv2.imwrite(f'frame_{i:04d}.jpg', frame)
```

#### 练习任务
1. 从摄像头采集10张图像并保存
2. 将图像统一调整为640x480大小
3. 对图像进行随机翻转、旋转数据增强
4. 在图像上标注Bounding Box（模拟标注）

---

## 下午时段：数据标注工具（14:00-17:00）

### 2.1 Label-Studio安装与配置

#### 安装步骤

```bash
# 方法1：pip安装
pip install label-studio

# 方法2：Docker安装（推荐）
docker pull heartexlabs/label-studio:latest
docker run -it -p 8080:8080 -v $(pwd)/mydata:/label-studio/data heartexlabs/label-studio:latest

# 启动Label-Studio
label-studio start
```

#### 初始配置
1. 访问 http://localhost:8080
2. 注册账号并登录
3. 创建一个新项目

---

### 2.2 Label-Studio目标检测标注配置

#### XML配置示例（用于创建目标检测模板）

```xml
<View>
  <Image name="image" value="$image" zoom="true"/>
  <RectangleLabels name="label" toName="image">
    <Label value="car" background="#FF0000"/>
    <Label value="pedestrian" background="#00FF00"/>
    <Label value="traffic_sign" background="#0000FF"/>
    <Label value="lane" background="#FFFF00"/>
  </RectangleLabels>
</View>
```

#### 标注界面功能
- **导入数据**：支持单张上传或批量导入
- **缩放平移**：滚轮缩放，拖拽平移
- **绘制框**：点击拖拽绘制矩形框
- **标签选择**：右侧标签面板选择类别
- **快捷键**：E编辑、D删除、Q上一个、N下一个

---

### 2.3 Label-Studio项目创建流程

#### Step 1: 创建项目
1. 点击 "Create Project"
2. 填写项目名称：`智能交通数据集`
3. 填写描述（可选）

#### Step 2: 设置标注模板
1. 选择 "Labeling Interface" -> "Custom Template"
2. 粘贴上述XML配置
3. 保存

#### Step 3: 导入数据
1. 点击 "Add Data" -> "Upload Files"
2. 选择要标注的图像
3. 确认上传

#### Step 4: 开始标注
1. 点击图像进入标注界面
2. 绘制矩形框并选择标签
3. 完成后点击 "Submit"

#### Step 5: 导出数据
1. 点击 "Export" 按钮
2. 选择导出格式（推荐 COCO 或 VOC）
3. 下载压缩包

---

### 2.4 数据格式转换代码

#### COCO格式转VOC格式

```python
import json
import os
import shutil
from PIL import Image
import xml.etree.ElementTree as ET

def coco_to_voc(coco_json_path, images_dir, output_dir):
    with open(coco_json_path, 'r') as f:
        coco_data = json.load(f)

    # 创建输出目录
    annotations_dir = os.path.join(output_dir, 'Annotations')
    images_dir_out = os.path.join(output_dir, 'JPEGImages')
    os.makedirs(annotations_dir, exist_ok=True)
    os.makedirs(images_dir_out, exist_ok=True)

    # 建立图片ID到图片信息的映射
    images_info = {img['id']: img for img in coco_data['images']}

    # 按图片分组标注
    annotations_by_image = {}
    for ann in coco_data['annotations']:
        img_id = ann['image_id']
        if img_id not in annotations_by_image:
            annotations_by_image[img_id] = []
        annotations_by_image[img_id].append(ann)

    # 生成每个图片的VOC XML
    for img_id, img_info in images_info.items():
        # 复制图片
        src_img = os.path.join(images_dir, img_info['file_name'])
        dst_img = os.path.join(images_dir_out, img_info['file_name'])
        if os.path.exists(src_img):
            shutil.copy(src_img, dst_img)

        # 创建XML
        root = ET.Element('annotation')
        ET.SubElement(root, 'filename').text = img_info['file_name']
        size = ET.SubElement(root, 'size')
        ET.SubElement(size, 'width').text = str(img_info['width'])
        ET.SubElement(size, 'height').text = str(img_info['height'])

        # 添加标注
        if img_id in annotations_by_image:
            for ann in annotations_by_image[img_id]:
                bbox = ann['bbox']  # [x, y, width, height]
                obj = ET.SubElement(root, 'object')
                ET.SubElement(obj, 'name').text = coco_data['categories'][ann['category_id']-1]['name']
                bndbox = ET.SubElement(obj, 'bndbox')
                ET.SubElement(bndbox, 'xmin').text = str(int(bbox[0]))
                ET.SubElement(bndbox, 'ymin').text = str(int(bbox[1]))
                ET.SubElement(bndbox, 'xmax').text = str(int(bbox[0] + bbox[2]))
                ET.SubElement(bndbox, 'ymax').text = str(int(bbox[1] + bbox[3]))

        # 保存XML
        xml_path = os.path.join(annotations_dir, img_info['file_name'].replace('.jpg', '.xml'))
        tree = ET.ElementTree(root)
        tree.write(xml_path)

    print(f"转换完成！共处理 {len(images_info)} 张图片")

# 使用示例
coco_to_voc('result.json', './images/', './voc_dataset/')
```

#### VOC格式转COCO格式

```python
import json
import os
import xml.etree.ElementTree as ET
from PIL import Image

def voc_to_coco(voc_root, output_json):
    categories = [
        {'id': 1, 'name': 'car'},
        {'id': 2, 'name': 'pedestrian'},
        {'id': 3, 'name': 'traffic_sign'},
        {'id': 4, 'name': 'lane'}
    ]

    coco_output = {
        'images': [],
        'annotations': [],
        'categories': categories
    }

    images_dir = os.path.join(voc_root, 'JPEGImages')
    annotations_dir = os.path.join(voc_root, 'Annotations')

    image_files = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]

    ann_id = 1
    for img_id, img_file in enumerate(image_files, 1):
        img_path = os.path.join(images_dir, img_file)
        img = Image.open(img_path)

        # 添加图片信息
        coco_output['images'].append({
            'id': img_id,
            'file_name': img_file,
            'width': img.width,
            'height': img.height
        })

        # 解析XML
        xml_file = os.path.join(annotations_dir, img_file.replace('.jpg', '.xml'))
        if os.path.exists(xml_file):
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for obj in root.findall('object'):
                bbox = obj.find('bndbox')
                xmin = int(bbox.find('xmin').text)
                ymin = int(bbox.find('ymin').text)
                xmax = int(bbox.find('xmax').text)
                ymax = int(bbox.find('ymax').text)

                # 转换为COCO格式 [x, y, width, height]
                bbox_coco = [xmin, ymin, xmax - xmin, ymax - ymin]

                category_name = obj.find('name').text
                category_id = next(c['id'] for c in categories if c['name'] == category_name)

                coco_output['annotations'].append({
                    'id': ann_id,
                    'image_id': img_id,
                    'category_id': category_id,
                    'bbox': bbox_coco,
                    'area': bbox_coco[2] * bbox_coco[3],
                    'iscrowd': 0
                })
                ann_id += 1

    with open(output_json, 'w') as f:
        json.dump(coco_output, f, indent=2)

    print(f"转换完成！共 {len(coco_output['images'])} 张图片，{len(coco_output['annotations'])} 个标注")

# 使用示例
voc_to_coco('./voc_dataset/', 'coco_annotations.json')
```

#### 导出CSV格式

```python
import json
import pandas as pd

def coco_to_csv(coco_json_path, output_csv):
    with open(coco_json_path, 'r') as f:
        coco_data = json.load(f)

    images_info = {img['id']: img for img in coco_data['images']}

    rows = []
    for ann in coco_data['annotations']:
        img_info = images_info[ann['image_id']]
        rows.append({
            'image_name': img_info['file_name'],
            'category': coco_data['categories'][ann['category_id']-1]['name'],
            'bbox_x': ann['bbox'][0],
            'bbox_y': ann['bbox'][1],
            'bbox_width': ann['bbox'][2],
            'bbox_height': ann['bbox'][3]
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"导出完成！共 {len(df)} 条标注")

# 使用示例
coco_to_csv('coco_annotations.json', 'annotations.csv')
```

---

### 2.5 数据集划分代码

```python
import os
import random
import shutil
from collections import defaultdict

def split_dataset(source_dir, output_dir, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
    assert train_ratio + val_ratio + test_ratio == 1.0

    # 创建输出目录
    for split in ['train', 'val', 'test']:
        os.makedirs(os.path.join(output_dir, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'labels', split), exist_ok=True)

    # 获取所有图片文件
    image_files = [f for f in os.listdir(os.path.join(source_dir, 'images')) if f.endswith('.jpg')]

    # 打乱顺序
    random.shuffle(image_files)

    # 计算划分点
    n_total = len(image_files)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    splits = {
        'train': image_files[:n_train],
        'val': image_files[n_train:n_train+n_val],
        'test': image_files[n_train+n_val:]
    }

    # 复制文件
    for split, files in splits.items():
        for img_file in files:
            # 复制图片
            src_img = os.path.join(source_dir, 'images', img_file)
            dst_img = os.path.join(output_dir, 'images', split, img_file)
            shutil.copy(src_img, dst_img)

            # 复制标签
            label_file = img_file.replace('.jpg', '.txt')
            src_label = os.path.join(source_dir, 'labels', label_file)
            dst_label = os.path.join(output_dir, 'labels', split, label_file)
            if os.path.exists(src_label):
                shutil.copy(src_label, dst_label)

        print(f"{split}: {len(files)} images")

    print(f"划分完成！总数: {n_total}")

# 使用示例
split_dataset('./dataset/', './output/', train_ratio=0.7, val_ratio=0.2, test_ratio=0.1)
```

---

## 晚间时段：PyTorch深度学习基础（19:00-22:00）

### 3.1 PyTorch张量基础

#### 核心概念
- ** Tensor**：PyTorch的基本数据结构，类似NumPy的ndarray
- ** GPU加速**：Tensor可以在GPU上运行
- ** 自动求导**：autograd机制自动计算梯度

#### 必须掌握的代码

```python
import torch
import numpy as np

# 创建张量
t1 = torch.tensor([1, 2, 3])                           # 从列表创建
t2 = torch.zeros(3, 4)                                 # 全零张量
t3 = torch.ones(2, 3)                                  # 全一张量
t4 = torch.randn(3, 3)                                 # 随机张量
t5 = torch.arange(0, 10, 2)                            # 范围张量

# 与NumPy互转
arr = np.array([1, 2, 3])
t_from_np = torch.from_numpy(arr)                      # NumPy转Tensor
arr_from_t = t_from_np.numpy()                         # Tensor转NumPy

# 基本属性
print(t1.shape)     # 形状
print(t1.dtype)     # 数据类型
print(t1.device)    # 设备（cpu/cuda）
print(t1.ndim)      # 维度

# GPU支持（如果有GPU）
if torch.cuda.is_available():
    t_gpu = t1.cuda()                                  # 移到GPU
    t_cpu = t_gpu.cpu()                                # 移回CPU

# 索引与切片
t = torch.tensor([[1, 2, 3], [4, 5, 6]])
print(t[0, :])       # 第一行
print(t[:, 1])       # 第二列

# 运算
a = torch.tensor([1, 2, 3])
b = torch.tensor([4, 5, 6])
print(a + b)              # 加法
print(a * b)              # 逐元素乘法
print(torch.matmul(a, b)) # 矩阵乘法
print(a.sum())            # 求和
print(a.mean())           # 均值

# 形状变换
t = torch.randn(3, 4)
print(t.reshape(4, 3))    # 改变形状
print(t.view(12))         # 展平
print(t.unsqueeze(0))     # 增加维度
print(t.squeeze(0))       # 移除维度
```

---

### 3.2 神经网络模型定义

#### 必须掌握的代码

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

# 方法1：继承nn.Module
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(32 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))  # Conv -> ReLU -> Pool
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 32 * 8 * 8)            # Flatten
        x = F.relu(self.fc1(x))               # Linear -> ReLU
        x = self.fc2(x)                        # Linear (output)
        return x

# 实例化模型
model = SimpleNet()
print(model)

# 查看模型参数
for name, param in model.named_parameters():
    print(f"{name}: {param.shape}")

# 前向传播
x = torch.randn(1, 3, 32, 32)  # Batch=1, C=3, H=32, W=32
output = model(x)
print(output.shape)  # torch.Size([1, 10])
```

#### 常用层说明
| 层类型 | 说明 |
|--------|------|
| `nn.Conv2d` | 二维卷积层 |
| `nn.MaxPool2d` / `nn.AvgPool2d` | 池化层 |
| `nn.Linear` | 全连接层 |
| `nn.BatchNorm2d` | 批归一化层 |
| `nn.Dropout` | Dropout层 |
| `nn.ReLU` / `nn.Sigmoid` / `nn.Tanh` | 激活函数 |

---

### 3.3 训练循环

#### 必须掌握的代码

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# 准备数据
x_train = torch.randn(1000, 20)
y_train = torch.randn(1000, 1)
dataset = TensorDataset(x_train, y_train)
train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

# 定义模型
class RegressionNet(nn.Module):
    def __init__(self):
        super(RegressionNet, self).__init__()
        self.fc1 = nn.Linear(20, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = RegressionNet()

# 损失函数和优化器
criterion = nn.MSELoss()                # 均方误差损失
optimizer = optim.Adam(model.parameters(), lr=0.001)  # Adam优化器

# 训练循环
num_epochs = 10
for epoch in range(num_epochs):
    model.train()                         # 设置为训练模式
    running_loss = 0.0

    for batch_x, batch_y in train_loader:
        # 前向传播
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)

        # 反向传播
        optimizer.zero_grad()             # 清零梯度
        loss.backward()                   # 计算梯度
        optimizer.step()                 # 更新参数

        running_loss += loss.item()

    avg_loss = running_loss / len(train_loader)
    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}")

# 保存和加载模型
torch.save(model.state_dict(), 'model.pth')     # 保存
model.load_state_dict(torch.load('model.pth'))  # 加载
```

---

### 3.4 分类任务训练示例

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
import torchvision.datasets as datasets

# 数据预处理
transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

# 加载数据
train_dataset = datasets.CIFAR10(root='./data', train=True, transform=transform, download=True)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# 定义分类模型
class ImageClassifier(nn.Module):
    def __init__(self, num_classes=10):
        super(ImageClassifier, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 16 * 16, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

model = ImageClassifier()
criterion = nn.CrossEntropyLoss()          # 分类用交叉熵损失
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练
for epoch in range(5):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for images, labels in train_loader:
        outputs = model(images)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    print(f"Epoch {epoch+1}: Loss={total_loss/len(train_loader):.4f}, Acc={100*correct/total:.2f}%")
```

---

## 今日总结与自检

### 知识点掌握检查

| 技能 | 要求 | 完成 |
|------|------|------|
| NumPy数组操作 | 能创建、索引、运算 | [ ] |
| Pandas数据处理 | 能读写CSV/JSON、筛选数据 | [ ] |
| OpenCV图像读取 | 能读取、保存、显示、变换 | [ ] |
| OpenCV摄像头采集 | 能从摄像头获取图像 | [ ] |
| Label-Studio安装 | 能独立安装并运行 | [ ] |
| Label-Studio标注 | 能标注目标检测框 | [ ] |
| 数据格式转换 | 能COCO/VOC/CSV互转 | [ ] |
| PyTorch张量 | 能创建、运算、GPU迁移 | [ ] |
| PyTorch模型 | 能定义简单神经网络 | [ ] |
| PyTorch训练 | 能完成完整训练循环 | [ ] |

### 明日预告

第2天将学习：
- **YOLO目标检测算法原理**
- **模型训练实战（使用ultralytics库）**
- **模型评估指标详解（mAP、Precision、Recall）**

---

*Day 1 学习完成！坚持就是胜利！*
