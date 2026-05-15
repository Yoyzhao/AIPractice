import json
import os

print("=" * 50)
print("练习4-1: 创建模拟COCO数据")
print("=" * 50)

coco_data = {
    "info": {"year": 2026, "version": "1.0"},
    "licenses": [],
    "images": [
        {"id": 1, "file_name": "img_0001.jpg", "width": 1920, "height": 1080},
        {"id": 2, "file_name": "img_0002.jpg", "width": 1280, "height": 720},
        {"id": 3, "file_name": "img_0003.jpg", "width": 640, "height": 480},
    ],
    "annotations": [
        {"id": 1, "image_id": 1, "category_id": 1, "bbox": [100, 100, 200, 150], "area": 30000, "iscrowd": 0},
        {"id": 2, "image_id": 1, "category_id": 2, "bbox": [500, 300, 100, 200], "area": 20000, "iscrowd": 0},
        {"id": 3, "image_id": 2, "category_id": 1, "bbox": [200, 150, 180, 120], "area": 21600, "iscrowd": 0},
        {"id": 4, "image_id": 3, "category_id": 3, "bbox": [50, 50, 80, 80], "area": 6400, "iscrowd": 0},
    ],
    "categories": [
        {"id": 1, "name": "car", "supercategory": "vehicle"},
        {"id": 2, "name": "pedestrian", "supercategory": "person"},
        {"id": 3, "name": "traffic_sign", "supercategory": "object"},
    ]
}

print(f"COCO数据包含 {len(coco_data['images'])} 张图像")
print(f"COCO数据包含 {len(coco_data['annotations'])} 个标注")
print(f"类别: {[c['name'] for c in coco_data['categories']]}")

print("\n" + "=" * 50)
print("练习4-2: 保存COCO数据为JSON")
print("=" * 50)

with open('coco_data.json', 'w') as f:
    json.dump(coco_data, f, indent=2)
print("已保存到 coco_data.json")

print("\n" + "=" * 50)
print("练习4-3: 读取COCO JSON文件")
print("=" * 50)

with open('coco_data.json', 'r') as f:
    loaded_coco = json.load(f)
print(f"重新加载成功!")
print(f"图像数量: {len(loaded_coco['images'])}")
print(f"标注数量: {len(loaded_coco['annotations'])}")

print("\n" + "=" * 50)
print("练习4-4: COCO数据转换为列表格式")
print("=" * 50)

images_info = {img['id']: img for img in coco_data['images']}
categories_info = {cat['id']: cat['name'] for cat in coco_data['categories']}

rows = []
for ann in coco_data['annotations']:
    img_info = images_info[ann['image_id']]
    rows.append({
        'image_name': img_info['file_name'],
        'category': categories_info[ann['category_id']],
        'bbox_x': ann['bbox'][0],
        'bbox_y': ann['bbox'][1],
        'bbox_width': ann['bbox'][2],
        'bbox_height': ann['bbox'][3],
    })

print(f"转换了 {len(rows)} 条记录")
for row in rows:
    print(f"  {row['image_name']}: {row['category']} at ({row['bbox_x']}, {row['bbox_y']})")

print("\n" + "=" * 50)
print("练习4-5: VOC格式数据(字典形式)")
print("=" * 50)

voc_data = [
    {
        'filename': 'img_0001.jpg',
        'width': 1920,
        'height': 1080,
        'objects': [
            {'name': 'car', 'xmin': 100, 'ymin': 100, 'xmax': 300, 'ymax': 250},
            {'name': 'pedestrian', 'xmin': 500, 'ymin': 300, 'xmax': 600, 'ymax': 500},
        ]
    },
    {
        'filename': 'img_0002.jpg',
        'width': 1280,
        'height': 720,
        'objects': [
            {'name': 'car', 'xmin': 200, 'ymin': 150, 'xmax': 380, 'ymax': 270},
        ]
    },
]

print(f"VOC格式包含 {len(voc_data)} 张图像")
for item in voc_data:
    print(f"  {item['filename']}: {len(item['objects'])} 个对象")

print("\n" + "=" * 50)
print("练习4-6: COCO转VOC格式转换")
print("=" * 50)

def coco_to_voc_list(coco_data):
    images_info = {img['id']: img for img in coco_data['images']}
    categories_info = {cat['id']: cat['name'] for cat in coco_data['categories']}

    annotations_by_image = {}
    for ann in coco_data['annotations']:
        img_id = ann['image_id']
        if img_id not in annotations_by_image:
            annotations_by_image[img_id] = []
        annotations_by_image[img_id].append(ann)

    voc_list = []
    for img_id, img_info in images_info.items():
        voc_item = {
            'filename': img_info['file_name'],
            'width': img_info['width'],
            'height': img_info['height'],
            'objects': []
        }

        if img_id in annotations_by_image:
            for ann in annotations_by_image[img_id]:
                xmin, ymin, w, h = ann['bbox']
                voc_item['objects'].append({
                    'name': categories_info[ann['category_id']],
                    'xmin': int(xmin),
                    'ymin': int(ymin),
                    'xmax': int(xmin + w),
                    'ymax': int(ymin + h)
                })

        voc_list.append(voc_item)

    return voc_list

voc_list = coco_to_voc_list(coco_data)
print(f"转换为VOC格式: {len(voc_list)} 张图像")
for item in voc_list:
    print(f"  {item['filename']}: {item['objects']}")

print("\n" + "=" * 50)
print("练习4-7: VOC转COCO格式转换")
print("=" * 50)

def voc_to_coco_list(voc_data):
    categories = list(set(obj['name'] for item in voc_data for obj in item['objects']))
    categories_info = [{"id": i+1, "name": c} for i, c in enumerate(categories)]

    coco_output = {
        "images": [],
        "annotations": [],
        "categories": categories_info
    }

    ann_id = 1
    for img_id, item in enumerate(voc_data, 1):
        coco_output['images'].append({
            'id': img_id,
            'file_name': item['filename'],
            'width': item['width'],
            'height': item['height']
        })

        for obj in item['objects']:
            category_id = next(c['id'] for c in categories_info if c['name'] == obj['name'])
            xmin, ymin = obj['xmin'], obj['ymin']
            xmax, ymax = obj['xmax'], obj['ymax']

            coco_output['annotations'].append({
                'id': ann_id,
                'image_id': img_id,
                'category_id': category_id,
                'bbox': [xmin, ymin, xmax - xmin, ymax - ymin],
                'area': (xmax - xmin) * (ymax - ymin),
                'iscrowd': 0
            })
            ann_id += 1

    return coco_output

coco_from_voc = voc_to_coco_list(voc_data)
print(f"转换为COCO格式:")
print(f"  图像: {len(coco_from_voc['images'])}")
print(f"  标注: {len(coco_from_voc['annotations'])}")
print(f"  类别: {[c['name'] for c in coco_from_voc['categories']]}")

print("\n" + "=" * 50)
print("练习4-8: CSV格式操作")
print("=" * 50)

csv_content = """image_name,category,bbox_x,bbox_y,bbox_width,bbox_height
img_0001.jpg,car,100,100,200,150
img_0001.jpg,pedestrian,500,300,100,200
img_0002.jpg,car,200,150,180,120
img_0003.jpg,traffic_sign,50,50,80,80"""

with open('sample.csv', 'w') as f:
    f.write(csv_content)

print("已保存 sample.csv")
print("\nCSV内容:")
print(csv_content)

print("\n" + "=" * 50)
print("练习4-9: CSV转列表")
print("=" * 50)

lines = csv_content.strip().split('\n')
header = lines[0].split(',')
csv_rows = []
for line in lines[1:]:
    values = line.split(',')
    csv_rows.append(dict(zip(header, values)))

print(f"CSV转换为 {len(csv_rows)} 条记录")
for row in csv_rows:
    print(f"  {row}")

print("\n" + "=" * 50)
print("练习4-10: 数据集划分模拟")
print("=" * 50)

all_files = [f'img_{i:04d}.jpg' for i in range(1, 21)]
print(f"总文件数: {len(all_files)}")

train_count = int(len(all_files) * 0.7)
val_count = int(len(all_files) * 0.2)
test_count = len(all_files) - train_count - val_count

train_files = all_files[:train_count]
val_files = all_files[train_count:train_count+val_count]
test_files = all_files[train_count+val_count:]

print(f"训练集: {len(train_files)} 文件")
print(f"验证集: {len(val_files)} 文件")
print(f"测试集: {len(test_files)} 文件")

print("\n" + "=" * 50)
print("练习4-11: 批量重命名文件")
print("=" * 50)

old_names = ['image1.jpg', 'image2.jpg', 'image3.jpg']
new_names = [f'img_{i:04d}.jpg' for i in range(1, len(old_names)+1)]

print("重命名映射:")
for old, new in zip(old_names, new_names):
    print(f"  {old} -> {new}")

print("\n" + "=" * 50)
print("练习4-12: 统计各类别数量")
print("=" * 50)

categories = ['car', 'pedestrian', 'traffic_sign', 'car', 'car', 'pedestrian']
from collections import Counter
counter = Counter(categories)
print(f"类别统计: {dict(counter)}")

print("\n" + "=" * 50)
print("练习4-13: 计算BoundingBox面积")
print("=" * 50)

bboxes = [
    {'x': 100, 'y': 100, 'width': 200, 'height': 150},
    {'x': 50, 'y': 50, 'width': 80, 'height': 80},
    {'x': 200, 'y': 150, 'width': 180, 'height': 120},
]

for bbox in bboxes:
    area = bbox['width'] * bbox['height']
    print(f"BBox at ({bbox['x']}, {bbox['y']}): 面积 = {area}")

print("\n" + "=" * 50)
print("练习4-14: 计算IOU")
print("=" * 50)

def calculate_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[0] + box1[2], box2[0] + box2[2])
    y2 = min(box1[1] + box1[3], box2[1] + box2[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = box1[2] * box1[3]
    area2 = box2[2] * box2[3]
    union = area1 + area2 - intersection

    return intersection / union if union > 0 else 0

box_a = [0, 0, 100, 100]
box_b = [50, 50, 100, 100]
iou = calculate_iou(box_a, box_b)
print(f"Box A: {box_a}")
print(f"Box B: {box_b}")
print(f"IOU: {iou:.4f}")

print("\n" + "=" * 50)
print("练习4-15: 数据格式验证")
print("=" * 50)

def validate_bbox(bbox, img_width, img_height):
    x, y, w, h = bbox
    if x < 0 or y < 0:
        return False, "坐标为负"
    if x + w > img_width:
        return False, "边界超出图像宽度"
    if y + h > img_height:
        return False, "边界超出图像高度"
    if w <= 0 or h <= 0:
        return False, "宽高必须为正"
    return True, "有效"

test_cases = [
    ([100, 100, 200, 150], 1920, 1080),
    ([-10, 100, 200, 150], 1920, 1080),
    ([100, 100, 2000, 150], 1920, 1080),
]

for bbox, w, h in test_cases:
    valid, msg = validate_bbox(bbox, w, h)
    print(f"BBox {bbox}, 图像 {w}x{h}: {msg}")

print("\n" + "=" * 50)
print("Label-Studio数据转换练习完成! 共15个练习题目")
print("=" * 50)
