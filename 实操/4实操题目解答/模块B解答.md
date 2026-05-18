# 模块B：人工智能应用模型训练 解答与解析

## 概述

模块B占总分的25%，包含2个子任务：

- B1：图像模型训练（YOLO11）
- B2：文本模型训练（BERT）

根据模块A制作的数据集，完成模型训练并生成可用的模型权重文件。

***

## 任务B1：图像模型训练

### 一、任务目标

1. 基于YOLO11进行目标检测模型训练
2. 生成训练成绩：训练图像数量、标签类别、instances、精确率、召回率、mAP50、mAP50-95
3. 使用训练好的模型对测试图片进行验证
4. 使用训练好的模型对视频进行验证并保存结果

### 二、环境准备

**检查YOLO11是否安装：**

```bash
# 检查ultralytics包
pip show ultralytics

# 如果未安装，执行以下命令
pip install ultralytics
```

**验证数据集路径：**

确认模块A中已完成数据集划分，数据集结构如下：

```
A3/数据集划分/
├── train/images/ & train/labels/
├── val/images/ & val/labels/
└── test/images/ & test/labels/
```

### 三、数据集配置文件（data.yaml）

在训练前，需要创建数据集配置文件：

```yaml
# A3/data.yaml - YOLO数据集配置
path: A3/数据集划分      # 数据集根目录（相对路径）
train: train/images     # 训练集图像目录
val: val/images         # 验证集图像目录
test: test/images       # 测试集图像目录

# 类别数量和名称（必须与标注时一致）
nc: 8                   # 类别数量
names: ['person', 'turn_left', 'turn_right', 'limit_20', 'limit_100', 'red_light', 'yellow_light', 'green_light']
```

### 四、YOLO11模型训练

**训练命令：**

```bash
# YOLO11目标检测训练命令详解
# yolo detect train   - YOLO检测任务 + train模式（训练模式）
# data=data.yaml      - 数据集配置文件路径
# model=yolo11n.pt    - 预训练模型权重（11n=nano、11s=small、11m=medium、11l=large、11x=xlarge）
# epochs=100          - 训练轮数
# imgsz=640           - 输入图像尺寸
yolo detect train data=data.yaml model=yolo11n.pt epochs=100 imgsz=640
```

**预训练模型来源：**

| 项目 | 说明 |
|------|------|
| **来源** | Ultralytics官方提供的COCO数据集预训练权重 |
| **获取方式** | 首次训练时命令会自动下载（需网络连接） |
| **存储位置** | `C:\Users\你的用户名\AppData\Roaming\Ultralytics` |
| **手动下载** | https://github.com/ultralytics/assets/releases |
| **离线训练** | 将.pt文件放在项目目录，使用相对路径 |

**参数调优建议：**

| 参数 | 可选值 | 说明 | 调整建议 |
|------|--------|------|----------|
| model | yolo11n/s/m/l/x | 模型规模 | 竞赛推荐s/m |
| epochs | 50~300 | 训练轮数 | 小数据集50-100 |
| imgsz | 320/416/512/640 | 图像尺寸 | 竞赛推荐640 |
| batch | 8/16/32 | 批大小 | 显存不足时降低 |

**竞赛推荐配置（性价比最高）：**

```bash
# 推荐配置1：平衡模式（精度与速度兼顾）
yolo detect train data=data.yaml model=yolo11s.pt epochs=100 imgsz=640 batch=16

# 推荐配置2：高精度模式（适合硬件强的环境）
yolo detect train data=data.yaml model=yolo11m.pt epochs=150 imgsz=640 batch=8
```

**训练输出结果示例：**

```
Epoch    GPU_mem   box_loss   cls_loss   dfl_loss   Instances       mAP50   mAP50-95
   100/100     3.21G     0.825      1.234      0.567         45        0.876      0.685

Results saved to runs/detect/train
✓ added device plugin 'NVIDIA'...
Model summary (fused): 225 layers, 11,123,123 parameters, 0 gradients
Optimizer summary: AdamW (beta1=0.9, beta2=0.999), learning rate=0.001
                       From model: yolo11s.pt
                       100 epochs completed in 0.145 hours.
```

**训练输出文件说明：**

| 文件/目录 | 说明 |
|-----------|------|
| `runs/detect/train/weights/best.pt` | 验证集上mAP最高的模型（推荐使用） |
| `runs/detect/train/weights/last.pt` | 最后一轮训练的模型 |
| `runs/detect/train/results.csv` | 训练过程指标记录（可用Excel打开） |
| `runs/detect/train/results.png` | 训练曲线可视化图 |

### 五、训练评估指标解读

训练完成后，YOLO会输出以下关键指标：

| 指标 | 含义 | 优秀标准 |
|------|------|----------|
| **precision（精确率）** | 预测为正的样本中真正为正的比例 | >0.8 |
| **recall（召回率）** | 实际为正的样本中被正确预测的比例 | >0.8 |
| **mAP50** | IoU阈值为0.5时的平均精度均值 | >0.7 |
| **mAP50-95** | IoU从0.5到0.95的平均精度均值 | >0.5 |

**mAP计算原理：**

```
mAP = 所有类别的AP平均值
AP = 精确率-召回率曲线下面积

mAP50 = IoU阈值=0.5时的mAP
mAP50-95 = IoU阈值从0.5到0.95（步长0.05）的mAP平均值
```

**各指标重要性：**

| 场景 | 重点关注指标 |
|------|-------------|
| 交通标志检测 | recall（漏检危险） |
| 自动驾驶安全 | mAP50-95（综合性能） |
| 实时性要求 | 推理速度FPS |

### 六、图片验证（val模式）

训练完成后，使用验证集评估模型性能：

```bash
# YOLO模型验证命令详解
# yolo detect val      - YOLO检测任务 + val模式（验证模式）
# data=data.yaml      - 数据集配置文件路径，包含验证集路径、类别数、类别名称
# model=runs/detect/train/weights/best.pt  - 训练生成的模型权重文件路径
#                       best.pt = 验证集上mAP最高的模型
#                       last.pt = 最后一轮训练的模型
yolo detect val data=data.yaml model=runs/detect/train/weights/best.pt
```

**验证结果输出示例：**

```
Results saved to runs/detect/val
✓ Model: best.pt
✓ Data: data.yaml

评估指标：
- images: 80           # 验证图像数量
- instances: 240       # 总检测实例数
- precision: 0.89      # 精确率
- recall: 0.85          # 召回率
- mAP50: 0.87          # IoU@0.5的平均精度
- mAP50-95: 0.68       # 多IoU阈值的平均精度
```

### 七、图片测试（test模式）

使用测试集进行模型泛化能力评估：

```bash
# 测试命令 - 使用best.pt或last.pt
# split=test 指定使用测试集进行评估
yolo detect val data=data.yaml model=runs/detect/train/weights/best.pt split=test
```

**val模式 vs test模式区别：**

| 模式 | 数据集 | 用途 | 比赛使用 |
|------|--------|------|----------|
| **val模式**（默认） | 验证集（val/） | 训练过程中验证模型性能 | 训练时自动评估 |
| **test模式** | 测试集（test/） | 评估模型泛化能力 | 裁判评判时用 |

**简单理解**：
- `val` = 训练时用的"练习题"，选手可以反复验证
- `test` = 裁判提供的"正式考试题"，用于最终评分

**如果裁判提供新的测试数据集：**

```bash
# 1. 创建新的测试数据配置（如果测试集路径不同）
# 2. 指定模型和测试数据
yolo detect val data=test_data.yaml model=runs/detect/train/weights/best.pt split=test
```

### 八、视频验证

使用训练好的模型对视频进行目标检测：

**Python程序示例（video_detection.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频目标检测程序
功能：使用YOLO11模型对视频进行目标检测并保存结果
"""

from ultralytics import YOLO
import cv2
import os

def video_detection(model_path, video_path, output_path):
    """
    视频目标检测函数

    参数:
        model_path - 模型权重路径（如 best.pt）
        video_path - 输入视频路径
        output_path - 输出视频保存路径
    """
    # 加载模型
    model = YOLO(model_path)
    print(f"模型加载成功: {model_path}")

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误：无法打开视频 {video_path}")
        return

    # 获取视频参数
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"视频信息: {width}x{height}, {fps}fps, 共{total_frames}帧")

    # 创建视频写入器
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # fourcc是视频编解码器的四字符代码(FourCC)
    # '*'mp4v' 表示将字符串拆分为4个字符: 'm', 'p', '4', 'v'
    # 常见视频格式fourcc代码:
    #   'mp4v' = MPEG-4 Part 2 (通用性好,Windows兼容)
    #   'avc1' = H.264/AVC (高压缩率,需要额外编码器)
    #   'XVID' = Xvid (开源MPEG-4)
    #   'MJPG' = Motion JPEG (无损,文件大)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    detection_results = []

    print("开始视频检测...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # 使用YOLO进行检测
        # conf=0.25  置信度阈值，只保留概率≥25%的检测结果
        # iou=0.45   非极大值抑制(NMS)的IoU阈值，用于去除重叠框
        #           IoU>0.45的同类别框只保留置信度最高的一个
        results = model(frame, conf=0.25, iou=0.45)

        # 绘制检测结果
        annotated_frame = results[0].plot()

        # 在画面上显示帧数
        cv2.putText(annotated_frame, f"Frame: {frame_count}/{total_frames}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 统计本帧检测结果
        if len(results[0].boxes) > 0:
            classes = results[0].boxes.cls.cpu().numpy()
            confs = results[0].boxes.conf.cpu().numpy()
            detection_results.append({
                'frame': frame_count,
                'count': len(classes),
                'classes': classes.tolist()
            })

        # 写入输出视频
        out.write(annotated_frame)

        if frame_count % 30 == 0:
            print(f"已处理: {frame_count}/{total_frames} 帧")

    cap.release()
    out.release()

    print(f"视频检测完成！结果已保存至: {output_path}")
    print(f"总检测帧数: {frame_count}")
    print(f"有检测结果的帧数: {len(detection_results)}")

    return detection_results

if __name__ == '__main__':
    # 配置路径
    model_path = 'runs/detect/train/weights/best.pt'  # 训练好的模型
    video_path = 'A1/素材/测试视频.mp4'                # 待检测视频
    output_path = 'B1/视频检测结果.mp4'                # 输出路径

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 执行视频检测
    video_detection(model_path, video_path, output_path)
```

### 九、任务B1文件存储

按照赛题要求，将文件存储到结果文件夹：

```
AI0102/B1/
├── best.pt                  # 训练生成的模型权重文件
├── last.pt                  # 最后一轮的模型权重
├── 训练过程截图/             # 训练曲线、评估指标截图
├── val_results/             # 验证结果
│   ├── results.txt          # 验证指标数据
│   └── 验证图像/             # 可视化验证结果
├── 图片测试结果/             # 测试集检测结果
│   ├── image_001.jpg
│   ├── image_002.jpg
│   └── ...
└── 视频检测结果.mp4          # 视频验证输出
```

**注意：** 结果存储文件夹命名方式为 `AI+场次号+赛位号`，如 `AI0102`

***

## 任务B2：文本模型训练

### 一、任务目标

1. 基于BERT模型进行文本分类模型训练
2. 生成训练成绩：训练文本数量、标签类别、样本实例数、精确率、召回率、F1值、准确率
3. 对文本测试数据集进行语义分类验证

### 二、文本分类数据集格式

模块A任务A4制作的文本数据集应包含以下字段：

**JSON格式示例（train.json）：**

```json
[
    {
        "id": 1,
        "text": "您好，我想咨询一下产品使用方法",
        "label": "咨询"
    },
    {
        "id": 2,
        "text": "产品出现故障，无法正常使用",
        "label": "投诉"
    },
    {
        "id": 3,
        "text": "机器报错E001，需要上门维修",
        "label": "报修"
    }
]
```

**标签映射：**

| 类别序号 | 类别名称 | 说明 |
|----------|----------|------|
| 0 | 咨询 | 用户询问相关信息 |
| 1 | 投诉 | 用户表达不满或抱怨 |
| 2 | 报修 | 用户报告设备故障 |

### 三、BERT文本分类训练

**Python程序示例（bert_text_classification.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BERT文本分类训练程序
功能：使用bert-base-chinese模型进行文本分类训练
"""

import os
import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import AdamW, get_linear_schedule_with_warmup
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
import numpy as np

# -------------------- 第一部分：配置参数 --------------------
class Config:
    """训练配置类"""
    def __init__(self):
        # model_name: 预训练模型名称
        # bert-base-chinese 是谷歌发布的中文BERT预训练模型
        # 包含104种语言，中文效果良好
        self.model_name = 'bert-base-chinese'

        # max_length: 输入文本的最大长度（token数）
        # BERT最大支持512 tokens
        # 过长会增加计算量，过短可能截断重要信息
        # 竞赛建议: 64-128即可
        self.max_length = 128

        # batch_size: 批大小，每批次处理的样本数
        # 越大训练越快，但显存占用越高
        # RTX3080约16GB显存可设16-32
        self.batch_size = 16

        # epochs: 训练轮数，整个数据集训练几次
        # 轮数太少欠拟合，太多过拟合
        # 竞赛建议: 3-5轮即可
        self.epochs = 3

        # learning_rate: 学习率，控制参数更新步长
        # BERT微调推荐2e-5 (0.00002) 或 3e-5
        # 太大震荡不收敛，太小训练太慢
        self.learning_rate = 2e-5

        # warmup_ratio: 预热比例，前10%的步骤学习率逐步增加
        # 有助于训练初期稳定收敛
        self.warmup_ratio = 0.1

        # num_labels: 分类类别数量
        # 咨询、投诉、报修 共3类
        self.num_labels = 3

        # label2id / id2label: 标签与ID的映射字典
        # 用于将字符串标签转换为数字ID
        self.label2id = {'咨询': 0, '投诉': 1, '报修': 2}
        self.id2label = {0: '咨询', 1: '投诉', 2: '报修'}

        # device: 计算设备，自动选择GPU或CPU
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# -------------------- 第二部分：数据集类 --------------------
class TextDataset(Dataset):
    """
    文本分类数据集类
    继承自torch.utils.data.Dataset，用于PyTorch数据加载
    功能：将JSON文件中的文本数据转换为BERT可处理的格式
    """

    def __init__(self, file_path, tokenizer, max_length, label2id):
        """
        初始化数据集

        参数:
            file_path  - JSON数据文件路径（如train.json）
            tokenizer  - BERT分词器（用于将文本转为token）
            max_length - 最大文本长度（超过则截断）
            label2id  - 标签到数字ID的映射字典
        """
        self.tokenizer = tokenizer  # BERT分词器
        self.max_length = max_length  # 最大序列长度
        self.label2id = label2id  # 标签映射

        # 加载JSON数据
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def __len__(self):
        """返回数据集样本总数"""
        return len(self.data)

    def __getitem__(self, idx):
        """
        获取单个样本

        参数:
            idx - 样本索引

        返回:
            包含input_ids、attention_mask、labels的字典
        """
        # 获取原始数据
        item = self.data[idx]
        text = item['text']  # 原始文本
        label = self.label2id.get(item['label'], 0)  # 标签转ID

        # Tokenize：将文本转换为BERT输入格式
        # tokenizer返回包含以下字段的字典:
        #   input_ids      - 文本的token ID序列
        #   attention_mask - 注意力掩码（1表示真实token，0表示padding）
        encoding = self.tokenizer(
            text,                    # 待分词文本
            max_length=self.max_length,  # 最大长度
            padding='max_length',     # 填充到最大长度
            truncation=True,          # 超过最大长度则截断
            return_tensors='pt'       # 返回PyTorch张量
        )

        # 返回模型输入格式
        # squeeze(0) 去除batch维度，因为Dataset每次返回1条样本
        return {
            'input_ids': encoding['input_ids'].squeeze(0),      # token ID序列
            'attention_mask': encoding['attention_mask'].squeeze(0),  # 注意力掩码
            'labels': torch.tensor(label, dtype=torch.long)     # 标签ID（LongTensor）
        }

# -------------------- 第三部分：训练函数 --------------------
def train_epoch(model, data_loader, optimizer, scheduler, device):
    """
    训练一个epoch（遍历整个训练集一次）

    参数:
        model       - BERT分类模型
        data_loader - 训练数据加载器
        optimizer   - 优化器（如AdamW）
        scheduler   - 学习率调度器
        device      - 计算设备（GPU/CPU）

    返回:
        平均训练损失
    """
    model.train()  # 设置为训练模式（启用dropout等）
    total_loss = 0  # 累计损失

    # 遍历每个batch
    for batch in data_loader:
        # 将数据移动到计算设备
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)

        # 清除上一步的梯度
        optimizer.zero_grad()

        # 前向传播：计算损失
        # model返回包含loss和logits的对象
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss  # 交叉熵损失
        total_loss += loss.item()  # 累计损失值

        # 反向传播：计算梯度
        loss.backward()

        # 梯度裁剪：防止梯度爆炸
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

        # 更新模型参数
        optimizer.step()

        # 更新学习率（按调度器规则）
        scheduler.step()

    # 返回平均损失
    return total_loss / len(data_loader)

def evaluate(model, data_loader, device):
    """评估模型"""
    model.eval()
    predictions = []
    true_labels = []

    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits

            preds = torch.argmax(logits, dim=1)
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())

    # 计算评估指标
    accuracy = accuracy_score(true_labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        true_labels, predictions, average='weighted'
    )

    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

# -------------------- 第四部分：主程序 --------------------
if __name__ == '__main__':
    config = Config()
    print(f"使用设备: {config.device}")

    # 加载tokenizer和模型
    print(f"加载模型: {config.model_name}")
    tokenizer = BertTokenizer.from_pretrained(config.model_name)
    model = BertForSequenceClassification.from_pretrained(
        config.model_name,
        num_labels=config.num_labels
    )
    model.to(config.device)

    # 创建数据集
    train_dataset = TextDataset('A4/文本数据集划分/train.json', tokenizer,
                               config.max_length, config.label2id)
    val_dataset = TextDataset('A4/文本数据集划分/val.json', tokenizer,
                             config.max_length, config.label2id)

    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.batch_size)

    print(f"训练集样本数: {len(train_dataset)}")
    print(f"验证集样本数: {len(val_dataset)}")

    # 优化器和学习率调度器
    optimizer = AdamW(model.parameters(), lr=config.learning_rate)
    total_steps = len(train_loader) * config.epochs
    warmup_steps = int(total_steps * config.warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )

    # 训练循环
    best_f1 = 0
    for epoch in range(config.epochs):
        print(f"\nEpoch {epoch + 1}/{config.epochs}")

        # 训练
        train_loss = train_epoch(model, train_loader, optimizer, scheduler, config.device)
        print(f"训练损失: {train_loss:.4f}")

        # 评估
        metrics = evaluate(model, val_loader, config.device)
        print(f"准确率: {metrics['accuracy']:.4f}")
        print(f"精确率: {metrics['precision']:.4f}")
        print(f"召回率: {metrics['recall']:.4f}")
        print(f"F1值: {metrics['f1']:.4f}")

        # 保存最佳模型
        if metrics['f1'] > best_f1:
            best_f1 = metrics['f1']
            torch.save(model.state_dict(), 'B2/best_model.pt')
            print("最佳模型已保存!")

    print("\n训练完成!")
    print(f"最佳F1值: {best_f1:.4f}")
```

### 四、BERT训练评估指标解读

| 指标 | 含义 | 计算公式 | 优秀标准 |
|------|------|----------|----------|
| **accuracy（准确率）** | 正确预测占总样本的比例 | (TP+TN)/(TP+TN+FP+FN) | >0.85 |
| **precision（精确率）** | 预测为正的样本中真正为正的比例 | TP/(TP+FP) | >0.85 |
| **recall（召回率）** | 实际为正的样本中被正确预测的比例 | TP/(TP+FN) | >0.85 |
| **F1值** | 精确率和召回率的调和平均 | 2×P×R/(P+R) | >0.85 |

**多分类混淆矩阵示例：**

| 真实\预测 | 咨询 | 投诉 | 报修 |
|-----------|------|------|------|
| 咨询 | 45 | 3 | 2 |
| 投诉 | 2 | 48 | 5 |
| 报修 | 1 | 4 | 40 |

### 五、文本分类预测

**Python程序示例（text_classification_predict.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本分类预测程序
功能：加载训练好的BERT模型，对新文本进行分类
"""

import torch
from transformers import BertTokenizer, BertForSequenceClassification

def predict_text(text, model_path, tokenizer_path, label2id):
    """
    文本分类预测函数

    参数:
        text - 待预测文本
        model_path - 模型权重路径
        tokenizer_path - tokenizer路径
        label2id - 标签到ID的映射

    返回:
        预测标签和置信度
    """
    # 加载模型和tokenizer
    tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
    model = BertForSequenceClassification.from_pretrained(model_path)
    model.eval()

    id2label = {v: k for k, v in label2id.items()}

    # Tokenize
    inputs = tokenizer(text, return_tensors='pt', max_length=128, truncation=True)

    # 预测
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
        pred_id = torch.argmax(probs, dim=1).item()
        confidence = probs[0][pred_id].item()

    pred_label = id2label[pred_id]
    return pred_label, confidence

if __name__ == '__main__':
    # 配置
    model_path = 'B2/best_model'
    tokenizer_path = 'bert-base-chinese'
    label2id = {'咨询': 0, '投诉': 1, '报修': 2}

    # 测试预测
    test_texts = [
        "您好，请问产品质保期是多久？",
        "机器坏了，完全无法使用，太失望了！",
        "空调不制冷，需要安排师傅上门检修"
    ]

    print("=" * 50)
    print("BERT文本分类预测测试")
    print("=" * 50)

    for text in test_texts:
        label, conf = predict_text(text, model_path, tokenizer_path, label2id)
        print(f"\n文本: {text}")
        print(f"预测: {label} (置信度: {conf:.4f})")
```

### 六、任务B2文件存储

按照赛题要求，将文件存储到结果文件夹：

```
AI0102/B2/
├── best_model.pt              # 训练生成的模型权重
├── 训练日志/                   # 训练过程日志
│   ├── training_log.txt
│   └── metrics.csv
├── 评估结果/                   # 验证评估结果
│   ├── evaluation_report.txt
│   └── confusion_matrix.png
└── 文本分类预测结果/            # 预测结果文件
    ├── predictions.json
    └── prediction_results.txt
```

***

## 模块B文件存储汇总

### 结果文件夹结构

```
AI0102/                    # 结果存储文件夹（AI+场次号+赛位号）
├── B1/                    # 任务B1
│   ├── best.pt           # YOLO11模型权重（最佳）
│   ├── last.pt           # YOLO11模型权重（最后）
│   ├── 训练成绩截图/       # 训练评估指标截图
│   ├── 图片测试结果/       # 测试图片检测结果
│   └── 视频检测结果.mp4    # 视频验证输出
│
└── B2/                    # 任务B2
    ├── best_model.pt      # BERT分类模型权重
    ├── 训练日志/           # 训练过程日志
    ├── 评估结果/           # 验证评估报告
    └── 文本分类预测结果/    # 预测结果
```

### 裁判评判检查清单

**B1图像模型训练评判时需展示：**

| 序号 | 评判内容 | 要求 |
|------|----------|------|
| 1 | 训练成绩展示 | val命令在终端展示训练指标 |
| 2 | 训练图像数量 | 展示数据集图像数量 |
| 3 | 标签类别 | 8个类别正确展示 |
| 4 | instances | 检测实例总数 |
| 5 | 精确率 | precision值 |
| 6 | 召回率 | recall值 |
| 7 | mAP50 | IoU@0.5的平均精度 |
| 8 | mAP50-95 | 多IoU阈值的平均精度 |
| 9 | 图片测试结果 | 裁判提供测试集验证 |
| 10 | 视频验证结果 | 保存的视频文件 |

**B2文本模型训练评判时需展示：**

| 序号 | 评判内容 | 要求 |
|------|----------|------|
| 1 | 训练成绩展示 | 验证指令在终端展示训练指标 |
| 2 | 训练文本数量 | 展示数据集文本数量 |
| 3 | 标签类别 | 3个类别（咨询、投诉、报修） |
| 4 | 样本实例数 | 各类别实例数 |
| 5 | 精确率 | precision值 |
| 6 | 召回率 | recall值 |
| 7 | F1值 | F1-score |
| 8 | 准确率 | accuracy值 |
| 9 | 文本测试结果 | 裁判提供测试集验证 |

***

## 常见问题与解决方案

### B1 常见问题

| 问题 | 解决方案 |
|------|----------|
| 训练中断，模型丢失 | 使用`last.pt`，训练会从中断处继续 |
| mAP值过低 | 增加epochs或使用更大模型（yolo11m） |
| 显存不足 | 减小batch_size或imgsz |
| 训练太慢 | 使用yolo11n或减小imgsz |
| 视频检测卡顿 | 使用模型导出为ONNX格式加速 |

### B2 常见问题

| 问题 | 解决方案 |
|------|----------|
| CUDA out of memory | 减小batch_size（8或4） |
| 精确率过低 | 检查数据集标注质量，增加样本量 |
| F1值过低 | 可能是类别不平衡，使用加权损失函数 |
| 模型无法加载 | 检查PyTorch和transformers版本兼容性 |
| 中文BERT下载失败 | 配置代理或使用镜像源 |

### 训练加速建议

**YOLO11训练加速：**

```bash
# 使用更大的batch和更小的imgsz
yolo detect train data=data.yaml model=yolo11s.pt epochs=100 imgsz=320 batch=32
```

**BERT训练加速：**

```python
# 使用混合精度训练
from torch.cuda.amp import GradScaler, autocast

scaler = GradScaler()

for batch in data_loader:
    with autocast():
        outputs = model(**inputs)
        loss = outputs.loss

    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

***

## 竞赛备赛提示

1. **时间管理**：模块B有25分钟左右的比赛时间，训练和验证需要合理安排
2. **模型选择**：竞赛环境推荐使用yolo11s/yolo11m，平衡精度和速度
3. **评估指标**：比赛评判主要看mAP和F1值，确保达到优秀标准
4. **结果保存**：务必保存best.pt和best_model.pt，这是裁判检查的重点
5. **提前准备**：在模块A制作数据集时，确保划分比例正确，格式规范
