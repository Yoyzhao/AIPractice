# 模块C：智能自动驾驶场景综合应用 解答与解析

## 概述

模块C占总分的35%，包含4个子任务：

- C1：模型部署验证
- C2：车道线检测功能测试
- C3：基于第一视角的综合功能测试
- C4：基于第三视角的综合功能测试

这是竞赛中最核心的综合应用模块，需要将模块B训练好的模型部署到自动驾驶平台，实现目标检测、车道线巡航和综合决策功能。

***

## 任务C1：模型部署验证

### 一、任务目标

1. 将YOLO11模型部署到人工智能部署及验证平台
2. 实现对实体红绿灯和转向标志的实时识别
3. 根据识别结果控制平台运动和灯光显示

### 二、系统架构

```
摄像头 → YOLO检测 → 识别结果 → 决策逻辑 → 运动控制+灯光控制
```

### 三、ROS节点程序结构

```
C1/
├── yolo_detector.py        # YOLO目标检测节点
├── light_controller.py     # 灯光控制节点
├── voice_player.py         # 语音播报节点
├── auto_drive.py           # 主控决策节点
└── auto_drive.launch       # 启动文件
```

### 四、YOLO目标检测节点

**Python程序示例（yolo_detector.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO目标检测ROS节点
功能：订阅摄像头图像，使用YOLO11进行目标检测，发布检测结果
"""

import rospy
import cv2
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from ultralytics import YOLO

class YOLODetector:
    """YOLO目标检测类"""

    def __init__(self, model_path='B1/best.pt'):
        self.bridge = CvBridge()

        # 加载YOLO模型
        self.model = YOLO(model_path)
        rospy.loginfo(f"YOLO模型加载成功: {model_path}")

        # 类别名称（与训练时一致）
        self.class_names = [
            'person', 'turn_left', 'turn_right',
            'limit_20', 'limit_100',
            'red_light', 'yellow_light', 'green_light'
        ]

        # 订阅摄像头话题
        self.image_sub = rospy.Subscriber(
            '/camera_head/image_raw',
            Image,
            self.image_callback
        )

        # 发布检测结果
        self.result_pub = rospy.Publisher(
            '/detection_result',
            String,
            queue_size=10
        )

        # 发布带标注的图像
        self.image_pub = rospy.Publisher(
            '/detection_image',
            Image,
            queue_size=10
        )

    def image_callback(self, msg):
        """图像回调函数"""
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            rospy.logerr(f"图像转换失败: {e}")
            return

        # YOLO推理
        results = self.model(frame, conf=0.5, iou=0.45)

        # 提取检测结果
        detections = []
        if len(results[0].boxes) > 0:
            boxes = results[0].boxes
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].cpu().numpy())
                conf = float(boxes.conf[i].cpu().numpy())
                cls_name = self.class_names[cls_id]
                detections.append({
                    'class': cls_name,
                    'confidence': conf,
                    'class_id': cls_id
                })

        # 发布检测结果
        if detections:
            result_msg = String()
            result_msg.data = str(detections)
            self.result_pub.publish(result_msg)

        # 发布带标注的图像
        annotated_frame = results[0].plot()
        image_msg = self.bridge.cv2_to_imgmsg(annotated_frame, "bgr8")
        self.image_pub.publish(image_msg)

def main():
    rospy.init_node('yolo_detector', anonymous=True)

    # 获取模型路径参数
    model_path = rospy.get_param('~model_path', 'B1/best.pt')

    detector = YOLODetector(model_path)
    rospy.loginfo("YOLO检测节点已启动")

    rospy.spin()

if __name__ == '__main__':
    main()
```

### 五、灯光控制节点

**Python程序示例（light_controller.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灯光控制ROS节点
功能：接收控制指令，控制前后左右四组灯光
"""

import rospy
from std_msgs.msg import String
import time

class LightController:
    """灯光控制器类"""

    def __init__(self):
        # 灯光控制话题（根据实际平台接口调整）
        self.light_pub = rospy.Publisher('/light_control', String, queue_size=10)

        # 订阅检测结果
        self.detection_sub = rospy.Subscriber(
            '/detection_result',
            String,
            self.detection_callback
        )

        self.current_state = 'idle'
        self.blinking = False

    def detection_callback(self, msg):
        """检测结果回调"""
        try:
            detections = eval(msg.data)
        except:
            return

        # 根据检测结果控制灯光
        light_pattern = self.decide_light_pattern(detections)
        if light_pattern:
            self.set_light(light_pattern)

    def decide_light_pattern(self, detections):
        """根据检测结果决定灯光模式"""
        detected_classes = [d['class'] for d in detections]

        # 优先级判断：红灯 > 黄灯 > 绿灯 > 转向标志
        if 'red_light' in detected_classes:
            return 'red_blink'
        elif 'yellow_light' in detected_classes:
            return 'yellow_blink'
        elif 'green_light' in detected_classes:
            return 'green_on'
        elif 'turn_left' in detected_classes:
            return 'left_blink'
        elif 'turn_right' in detected_classes:
            return 'right_blink'

        return 'all_off'

    def set_light(self, pattern):
        """设置灯光模式"""
        patterns = {
            'red_blink': 'R',
            'yellow_blink': 'Y',
            'green_on': 'G',
            'left_blink': 'L',
            'right_blink': 'R2',
            'all_off': 'OFF'
        }

        cmd = patterns.get(pattern, 'OFF')
        light_msg = String()
        light_msg.data = cmd
        self.light_pub.publish(light_msg)
        rospy.loginfo(f"灯光设置: {pattern}")

    def blink_light(self, color, duration=3):
        """闪烁灯光（用于测试）"""
        self.blinking = True
        end_time = time.time() + duration

        while time.time() < end_time and self.blinking:
            self.light_pub.publish(String(data=color))
            time.sleep(0.5)
            self.light_pub.publish(String(data='OFF'))
            time.sleep(0.5)

def main():
    rospy.init_node('light_controller', anonymous=True)
    controller = LightController()

    # 测试闪烁功能
    rospy.sleep(1)
    rospy.loginfo("灯光控制节点已启动")

    rospy.spin()

if __name__ == '__main__':
    main()
```

### 六、主控决策节点

**Python程序示例（auto_drive.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动驾驶主控ROS节点
功能：综合决策，控制运动、灯光、语音
"""

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import json

class AutoDriveController:
    """自动驾驶主控类"""

    def __init__(self):
        # 速度控制发布者
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # 灯光控制发布者
        self.light_pub = rospy.Publisher('/light_control', String, queue_size=10)

        # 语音播报发布者
        self.voice_pub = rospy.Publisher('/voice/play', String, queue_size=10)

        # 订阅检测结果
        self.detection_sub = rospy.Subscriber(
            '/detection_result',
            String,
            self.detection_callback
        )

        # 当前状态
        self.current_speed = 0.0
        self.target_speed = 0.2  # 初始速度

        # 速度映射表（类别名 -> 速度）
        self.speed_map = {
            'red_light': 0.0,
            'yellow_light': 0.05,  # 极低速度
            'green_light': 0.2,
            'limit_20': 0.1,
            'limit_100': 0.5,
            'turn_left': None,  # 转弯时不设置速度
            'turn_right': None
        }

        # 语音播报映射
        self.voice_map = {
            'red_light': '识别到红灯，停车',
            'yellow_light': '识别到黄灯，车辆减速',
            'green_light': '识别到绿灯，正式行驶',
            'turn_left': '识别到左转，车辆左转弯',
            'turn_right': '识别到右转，车辆右转弯',
            'limit_20': '请注意，车辆减速中',
            'limit_100': '请注意，车辆加速中',
            'person': '识别到行人，停车'
        }

    def detection_callback(self, msg):
        """检测结果回调"""
        try:
            detections = eval(msg.data)
        except:
            return

        if not detections:
            return

        # 获取最高置信度的检测结果
        best_detection = max(detections, key=lambda x: x['confidence'])
        cls_name = best_detection['class']

        # 执行相应动作
        self.execute_action(cls_name)

    def execute_action(self, cls_name):
        """根据类别执行动作"""
        # 速度控制
        if cls_name in self.speed_map:
            new_speed = self.speed_map[cls_name]
            if new_speed is not None:
                self.target_speed = new_speed
                self.set_speed(self.target_speed)

        # 灯光控制
        self.set_light(cls_name)

        # 语音播报
        if cls_name in self.voice_map:
            self.play_voice(self.voice_map[cls_name])

        # 转向控制
        if cls_name == 'turn_left':
            self.turn_left()
        elif cls_name == 'turn_right':
            self.turn_right()

    def set_speed(self, speed):
        """设置速度"""
        twist = Twist()
        twist.linear.x = speed
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        self.cmd_vel_pub.publish(twist)
        rospy.loginfo(f"速度设置: {speed}")

    def set_light(self, cls_name):
        """设置灯光"""
        light_cmds = {
            'red_light': 'R',
            'yellow_light': 'Y',
            'green_light': 'G',
            'turn_left': 'L',
            'turn_right': 'R2',
            'person': 'YR'  # 黄红交替
        }

        if cls_name in light_cmds:
            cmd = String(data=light_cmds[cls_name])
            self.light_pub.publish(cmd)

    def play_voice(self, text):
        """播放语音"""
        msg = String(data=text)
        self.voice_pub.publish(msg)
        rospy.loginfo(f"语音播报: {text}")

    def turn_left(self):
        """左转"""
        twist = Twist()
        twist.linear.x = 0.1
        twist.angular.z = 1.0  # 左转
        self.cmd_vel_pub.publish(twist)
        rospy.sleep(2)  # 转弯持续时间

        # 恢复直行
        twist.angular.z = 0
        self.cmd_vel_pub.publish(twist)

    def turn_right(self):
        """右转"""
        twist = Twist()
        twist.linear.x = 0.1
        twist.angular.z = -1.0  # 右转
        self.cmd_vel_pub.publish(twist)
        rospy.sleep(2)

        # 恢复直行
        twist.angular.z = 0
        self.cmd_vel_pub.publish(twist)

def main():
    rospy.init_node('auto_drive_controller', anonymous=True)
    controller = AutoDriveController()
    rospy.loginfo("自动驾驶主控节点已启动")
    rospy.spin()

if __name__ == '__main__':
    main()
```

### 七、ROS启动文件

**XML文件示例（auto_drive.launch）：**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<launch>
    <!-- YOLO检测节点 -->
    <node name="yolo_detector" pkg="autonomous_driving" type="yolo_detector.py"
          output="screen">
        <param name="model_path" value="$(find autonomous_driving)/models/best.pt" />
    </node>

    <!-- 灯光控制节点 -->
    <node name="light_controller" pkg="autonomous_driving" type="light_controller.py"
          output="screen" />

    <!-- 语音播报节点 -->
    <node name="voice_player" pkg="autonomous_driving" type="voice_player.py"
          output="screen" />

    <!-- 自动驾驶主控节点 -->
    <node name="auto_drive" pkg="autonomous_driving" type="auto_drive.py"
          output="screen" />
</launch>
```

### 八、任务C1评判标准

| 序号 | 评判内容 | 预期结果 |
|------|----------|----------|
| 1 | 红灯识别 | 速度=0，4红灯闪烁 |
| 2 | 黄灯识别 | 速度=极低，4黄灯闪烁 |
| 3 | 绿灯识别 | 速度=0.2，4绿灯常亮 |
| 4 | 左转标志识别 | 左转，2绿灯闪烁 |
| 5 | 右转标志识别 | 右转，2绿灯闪烁 |

***

## 任务C2：车道线检测功能测试

### 一、任务目标

1. 实现车道线检测功能
2. 基于车道线实现自适应巡航
3. 平台全程不得跑出车道线范围

### 二、车道线检测原理

车道线检测使用OpenCV图像处理技术：

```
图像获取 → 边缘检测 → 阈值分割 → 霍夫变换 → 车道线拟合 → 偏差计算 → 转向控制
```

### 三、车道线检测程序

**Python程序示例（lane_detection.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车道线检测ROS节点
功能：检测车道线，计算偏移量，输出转向控制指令
"""

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge

class LaneDetector:
    """车道线检测类"""

    def __init__(self):
        self.bridge = CvBridge()

        # 订阅摄像头话题
        self.image_sub = rospy.Subscriber(
            '/camera_bottom/image_raw',
            Image,
            self.image_callback
        )

        # 发布速度控制
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # 检测参数
        self.image_width = 640
        self.image_height = 480

        # 车道线检测区域（ROI）
        self.roi_top = 280
        self.roi_bottom = 480

        # PID控制参数
        self.kp = 0.5
        self.ki = 0.0
        self.kd = 0.1

        self.last_error = 0
        self.integral = 0

    def image_callback(self, msg):
        """图像回调"""
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        frame = cv2.resize(frame, (self.image_width, self.image_height))

        # 车道线检测
        deviation = self.detect_lane(frame)

        # 计算转向角度
        steering_angle = self.calculate_steering(deviation)

        # 发布控制指令
        self.publish_cmd(steering_angle)

        # 可视化
        debug_image = self.draw_debug(frame, deviation)
        cv2.imshow("Lane Detection", debug_image)
        cv2.waitKey(1)

    def detect_lane(self, frame):
        """检测车道线，返回偏移量"""
        # 转换为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ROI区域
        roi = gray[self.roi_top:self.roi_bottom, :]

        # 边缘检测
        blurred = cv2.GaussianBlur(roi, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # 霍夫变换检测直线
        lines = cv2.HoughLinesP(edges, 1, np.pi/180,
                                threshold=50,
                                minLineLength=50,
                                maxLineGap=100)

        if lines is None:
            return 0  # 未检测到车道线，返回居中

        # 分离左右车道线
        left_lines = []
        right_lines = []

        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1 + 1e-6)

            # 根据斜率判断左右车道线
            if slope < -0.3:  # 左车道线（斜率为负）
                left_lines.append(line[0])
            elif slope > 0.3:  # 右车道线（斜率为正）
                right_lines.append(line[0])

        # 计算左右车道线的中点
        left_x = np.mean([l[0] + l[2] for l in left_lines]) if left_lines else 100
        right_x = np.mean([r[0] + r[2] for r in right_lines]) if right_lines else 540

        # 车道线中心
        lane_center = (left_x + right_x) / 2

        # 图像中心
        image_center = self.image_width / 2

        # 偏移量（负值表示偏左，正值表示偏右）
        deviation = image_center - lane_center

        return deviation

    def calculate_steering(self, deviation):
        """PID控制计算转向角度"""
        # 积分项
        self.integral += deviation

        # 微分项
        derivative = deviation - self.last_error
        self.last_error = deviation

        # PID公式
        steering = self.kp * deviation + self.ki * self.integral + self.kd * derivative

        # 限制转向角度
        steering = max(-1.0, min(1.0, steering))

        return steering

    def publish_cmd(self, steering_angle):
        """发布速度控制指令"""
        twist = Twist()
        twist.linear.x = 0.2  # 恒定速度
        twist.angular.z = steering_angle
        self.cmd_vel_pub.publish(twist)

    def draw_debug(self, frame, deviation):
        """绘制调试信息"""
        output = frame.copy()

        # 绘制ROI区域
        cv2.rectangle(output, (0, self.roi_top),
                     (self.image_width, self.roi_bottom),
                     (0, 255, 0), 2)

        # 显示偏移量
        text = f"Deviation: {deviation:.1f}"
        cv2.putText(output, text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 绘制中心线
        cv2.line(output,
                (self.image_width // 2, self.roi_top),
                (self.image_width // 2, self.roi_bottom),
                (0, 0, 255), 2)

        return output

def main():
    rospy.init_node('lane_detector', anonymous=True)
    detector = LaneDetector()
    rospy.loginfo("车道线检测节点已启动")
    rospy.spin()

if __name__ == '__main__':
    main()
```

### 四、综合车道线与目标检测

**Python程序示例（lane_and_detection.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车道线巡航与目标检测综合节点
功能：结合车道线检测和YOLO目标检测，实现综合自动驾驶
"""

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from cv_bridge import CvBridge
from ultralytics import YOLO

class LaneFollowingWithDetection:
    """车道线巡航+目标检测综合类"""

    def __init__(self, model_path='B1/best.pt'):
        self.bridge = CvBridge()

        # YOLO模型
        self.model = YOLO(model_path)
        self.class_names = [
            'person', 'turn_left', 'turn_right',
            'limit_20', 'limit_100',
            'red_light', 'yellow_light', 'green_light'
        ]

        # 速度控制
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # 灯光控制
        self.light_pub = rospy.Publisher('/light_control', String, queue_size=10)

        # 语音播报
        self.voice_pub = rospy.Publisher('/voice/play', String, queue_size=10)

        # 摄像头订阅
        self.image_sub = rospy.Subscriber(
            '/camera_head/image_raw',
            Image,
            self.image_callback
        )

        # 检测结果订阅
        self.detection_sub = rospy.Subscriber(
            '/detection_result',
            String,
            self.detection_callback
        )

        # 速度参数
        self.base_speed = 0.2
        self.current_speed = self.base_speed
        self.current_angular = 0.0

        # 状态标志
        self.override_control = False

    def detection_callback(self, msg):
        """检测结果回调"""
        try:
            detections = eval(msg.data)
        except:
            return

        if not detections:
            self.override_control = False
            return

        # 最高置信度检测
        best = max(detections, key=lambda x: x['confidence'])
        cls = best['class']

        # 优先级控制
        if cls == 'red_light':
            self.current_speed = 0.0
            self.override_control = True
            self.publish_light('R')
            self.publish_voice('识别到红灯，停车')
        elif cls == 'yellow_light':
            self.current_speed = 0.05
            self.override_control = True
            self.publish_light('Y')
            self.publish_voice('识别到黄灯，车辆减速')
        elif cls == 'green_light':
            self.current_speed = self.base_speed
            self.override_control = True
            self.publish_light('G')
            self.publish_voice('识别到绿灯，正式行驶')
        elif cls == 'person':
            self.current_speed = 0.0
            self.override_control = True
            self.publish_light('YR')
            self.publish_voice('识别到行人，停车')
        else:
            self.override_control = False

    def image_callback(self, msg):
        """图像回调"""
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        frame = cv2.resize(frame, (640, 480))

        # 车道线检测
        deviation = self.detect_lane(frame)

        # 发布控制指令
        if not self.override_control:
            self.publish_cmd(self.base_speed, deviation * 0.5)

    def detect_lane(self, frame):
        """检测车道线"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi = gray[280:480, :]

        edges = cv2.Canny(roi, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180,
                                threshold=50, minLineLength=50, maxLineGap=100)

        if lines is None:
            return 0

        left_x = right_x = 320
        left_slopes = []
        right_slopes = []

        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1 + 1e-6)

            if slope < -0.3:
                left_slopes.append((x1, x2))
            elif slope > 0.3:
                right_slopes.append((x2, x2))

        if left_slopes:
            left_x = np.mean([(l[0] + l[1]) / 2 for l in left_slopes])
        if right_slopes:
            right_x = np.mean([(r[0] + r[1]) / 2 for r in right_slopes])

        center = (left_x + right_x) / 2
        return 320 - center

    def publish_cmd(self, speed, angular):
        """发布速度指令"""
        twist = Twist()
        twist.linear.x = speed
        twist.angular.z = angular
        self.cmd_vel_pub.publish(twist)

    def publish_light(self, pattern):
        """发布灯光指令"""
        self.light_pub.publish(String(data=pattern))

    def publish_voice(self, text):
        """发布语音"""
        self.voice_pub.publish(String(data=text))

def main():
    rospy.init_node('lane_following_with_detection')
    controller = LaneFollowingWithDetection()
    rospy.loginfo("综合自动驾驶节点已启动")
    rospy.spin()

if __name__ == '__main__':
    main()
```

### 五、任务C2评判标准

| 序号 | 评判内容 | 合格标准 |
|------|----------|----------|
| 1 | 车道线检测 | 正确检测出车道线 |
| 2 | 自适应巡航 | 从起点到终点完成一圈 |
| 3 | 车道保持 | 4个车轮在车道线内 |

**评判说明**：车道线在4个车轮中间（含轮子压在车道线上）为合格，任1车轮超出车道线计不合格1次。

***

## 任务C3：基于第一视角的综合功能测试

### 一、任务目标

1. 基于仿真视频素材进行自动驾驶
2. 实现车道线巡航+目标检测+灯光语音
3. 平台置于操作工位桌面调试架

### 二、系统架构

```
仿真视频 → YOLO检测+车道线检测 → 综合决策 → 动作执行
```

### 三、视频处理综合程序

**Python程序示例（video_autonomous_driving.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频自动驾驶综合程序
功能：读取仿真视频，进行目标检测和车道线检测，实现综合自动驾驶
"""

import cv2
import numpy as np
from ultralytics import YOLO
from gtts import gTTS
import pygame
import os
import time

class VideoAutonomousDriving:
    """视频自动驾驶类"""

    def __init__(self, model_path='B1/best.pt', video_path='A1/素材/仿真视频.mp4'):
        # YOLO模型
        self.model = YOLO(model_path)
        self.class_names = [
            'person', 'turn_left', 'turn_right',
            'limit_20', 'limit_100',
            'red_light', 'yellow_light', 'green_light'
        ]

        # 视频
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

        # pygame用于语音播放
        pygame.init()
        pygame.mixer.init()

        # 当前状态
        self.current_speed = 0.0
        self.current_action = 'stop'

        # 动作映射
        self.action_map = {
            'red_light': {'speed': 0.0, 'light': 'R', 'voice': '识别到红灯，停车'},
            'yellow_light': {'speed': 0.05, 'light': 'Y', 'voice': '识别到黄灯，车辆减速'},
            'green_light': {'speed': 0.2, 'light': 'G', 'voice': '识别到绿灯，正式行驶'},
            'turn_left': {'speed': 0.1, 'light': 'L', 'voice': '识别到左转，车辆左转弯', 'turn': 'left'},
            'turn_right': {'speed': 0.1, 'light': 'R2', 'voice': '识别到右转，车辆右转弯', 'turn': 'right'},
            'limit_20': {'speed': 0.1, 'light': None, 'voice': '请注意，车辆减速中'},
            'limit_100': {'speed': 0.5, 'light': None, 'voice': '请注意，车辆加速中'},
            'person': {'speed': 0.0, 'light': 'YR', 'voice': '识别到行人，停车'}
        }

    def process_frame(self, frame):
        """处理单帧图像"""
        # YOLO检测
        results = self.model(frame, conf=0.5)

        detections = []
        if len(results[0].boxes) > 0:
            for i in range(len(results[0].boxes)):
                cls_id = int(results[0].boxes.cls[i].cpu().numpy())
                conf = float(results[0].boxes.conf[i].cpu().numpy())
                detections.append({
                    'class': self.class_names[cls_id],
                    'confidence': conf
                })

        # 绘制检测结果
        annotated = results[0].plot()

        # 车道线检测
        lane deviation = self.detect_lane(frame)
        steering = deviation * 0.5

        # 综合决策
        action = self.decide_action(detections)

        # 在画面上显示信息
        info_text = f"Speed: {self.current_speed:.2f} | Action: {action}"
        cv2.putText(annotated, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        return annotated, action

    def detect_lane(self, frame):
        """车道线检测"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi = gray[280:480, :]

        edges = cv2.Canny(roi, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180,
                                threshold=50, minLineLength=50, maxLineGap=100)

        if lines is None:
            return 0

        left_x = right_x = 320
        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1 + 1e-6)

            if slope < -0.3:
                left_x = (x1 + x2) / 2
            elif slope > 0.3:
                right_x = (x1 + x2) / 2

        center = (left_x + right_x) / 2
        return 320 - center

    def decide_action(self, detections):
        """综合决策"""
        if not detections:
            self.current_speed = 0.2
            return 'cruising'

        # 按优先级排序
        priority_classes = ['red_light', 'yellow_light', 'green_light', 'person',
                          'turn_left', 'turn_right', 'limit_20', 'limit_100']

        for cls_name in priority_classes:
            for det in detections:
                if det['class'] == cls_name and det['confidence'] > 0.5:
                    action = self.action_map[cls_name]

                    # 执行动作
                    self.current_speed = action['speed']
                    light = action.get('light')
                    voice = action['voice']
                    turn = action.get('turn')

                    # 打印动作信息
                    print(f"检测到: {cls_name} | 速度: {self.current_speed}")

                    return cls_name

        self.current_speed = 0.2
        return 'cruising'

    def play_voice(self, text):
        """播放语音"""
        try:
            tts = gTTS(text=text, lang='zh')
            tts.save('/tmp/voice.mp3')
            pygame.mixer.music.load('/tmp/voice.mp3')
            pygame.mixer.music.play()
        except Exception as e:
            print(f"语音播放失败: {e}")

    def run(self):
        """运行主循环"""
        if not self.cap.isOpened():
            print(f"无法打开视频: {self.video_path}")
            return

        print("视频自动驾驶已启动...")
        last_action = None

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("视频播放完成")
                break

            # 处理帧
            display_frame, action = self.process_frame(frame)

            # 动作变化时播放语音
            if action != last_action and action in self.action_map:
                self.play_voice(self.action_map[action]['voice'])
                last_action = action

            # 显示
            cv2.imshow('Video Autonomous Driving', display_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    driving = VideoAutonomousDriving()
    driving.run()
```

### 四、任务C3动作要求汇总

| 检测目标 | 速度控制 | 灯光效果 | 语音播报 |
|----------|----------|----------|----------|
| 红灯 | 0 | 4红灯闪烁 | 识别到红灯，停车 |
| 黄灯 | 极低 | 4黄灯闪烁 | 识别到黄灯，车辆减速 |
| 绿灯 | 0.2 | 4绿灯常亮 | 识别到绿灯，正式行驶 |
| 左转标志 | 0.1 | 2绿灯闪烁(左) | 识别到左转，车辆左转弯 |
| 右转标志 | 0.1 | 2绿灯闪烁(右) | 识别到右转，车辆右转弯 |
| 限速100 | 0.5 | - | 请注意，车辆加速中 |
| 限速20 | 0.1 | - | 请注意，车辆减速中 |

***

## 任务C4：基于第三视角的综合功能测试

### 一、任务目标

1. 基于人工智能自动驾驶应用场景进行综合测试
2. 从起点到终点完成一圈巡航
3. 全程不得人工干预

### 二、综合决策逻辑

**状态机设计：**

```
START → 检测前方 → [红灯→停止] → [绿灯→行驶] → [标志→转向] → [行人→停车] → ... → END
```

### 三、完整自动驾驶程序

**Python程序示例（complete_autonomous_driving.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整自动驾驶综合程序
功能：结合YOLO检测、车道线巡航、语音灯光，实现端到端自动驾驶
"""

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from cv_bridge import CvBridge
from ultralytics import YOLO

class CompleteAutonomousDriving:
    """完整自动驾驶类"""

    def __init__(self, model_path='B1/best.pt'):
        self.bridge = CvBridge()

        # YOLO模型
        self.model = YOLO(model_path)
        self.class_names = [
            'person', 'turn_left', 'turn_right',
            'limit_20', 'limit_100',
            'red_light', 'yellow_light', 'green_light'
        ]

        # ROS发布者
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.light_pub = rospy.Publisher('/light_control', String, queue_size=10)
        self.voice_pub = rospy.Publisher('/voice/play', String, queue_size=10)

        # 订阅摄像头
        self.image_sub = rospy.Subscriber(
            '/camera_head/image_raw',
            Image,
            self.image_callback
        )

        # 速度参数
        self.base_speed = 0.2
        self.current_speed = self.base_speed
        self.target_speed = self.base_speed

        # 动作参数
        self.current_light = None
        self.turning = False

        # 优先级列表
        self.priority_classes = [
            'person', 'red_light', 'yellow_light', 'green_light',
            'turn_left', 'turn_right', 'limit_20', 'limit_100'
        ]

        # 动作映射
        self.action_map = {
            'red_light': {'speed': 0.0, 'light': 'R', 'voice': '识别到红灯，停车'},
            'yellow_light': {'speed': 0.05, 'light': 'Y', 'voice': '识别到黄灯，车辆减速'},
            'green_light': {'speed': 0.2, 'light': 'G', 'voice': '识别到绿灯，正式行驶'},
            'turn_left': {'speed': 0.1, 'light': 'L', 'voice': '识别到左转，车辆左转弯', 'turn': 'left'},
            'turn_right': {'speed': 0.1, 'light': 'R2', 'voice': '识别到右转，车辆右转弯', 'turn': 'right'},
            'limit_20': {'speed': 0.1, 'light': None, 'voice': '请注意，车辆减速中'},
            'limit_100': {'speed': 0.5, 'light': None, 'voice': '请注意，车辆加速中'},
            'person': {'speed': 0.0, 'light': 'YR', 'voice': '识别到行人，停车'}
        }

    def image_callback(self, msg):
        """图像回调"""
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")

        # YOLO检测
        results = self.model(frame, conf=0.5)
        detections = self.parse_detections(results)

        # 车道线检测
        lane_deviation = self.detect_lane(frame)

        # 综合决策
        action = self.decide_action(detections)

        # 发布控制指令
        self.publish_control(action, lane_deviation)

    def parse_detections(self, results):
        """解析检测结果"""
        detections = []
        if len(results[0].boxes) > 0:
            for i in range(len(results[0].boxes)):
                cls_id = int(results[0].boxes.cls[i].cpu().numpy())
                conf = float(results[0].boxes.conf[i].cpu().numpy())
                detections.append({
                    'class': self.class_names[cls_id],
                    'confidence': conf
                })
        return detections

    def detect_lane(self, frame):
        """车道线检测"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi = gray[280:480, :]

        edges = cv2.Canny(roi, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180,
                                threshold=50, minLineLength=50, maxLineGap=100)

        if lines is None:
            return 0

        left_x = right_x = 320
        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1 + 1e-6)

            if slope < -0.3:
                left_x = (x1 + x2) / 2
            elif slope > 0.3:
                right_x = (x1 + x2) / 2

        center = (left_x + right_x) / 2
        return 320 - center

    def decide_action(self, detections):
        """综合决策"""
        if not detections:
            return self.action_map['green_light']

        # 按优先级选择动作
        for cls_name in self.priority_classes:
            for det in detections:
                if det['class'] == cls_name and det['confidence'] > 0.5:
                    return self.action_map[cls_name]

        return self.action_map['green_light']

    def publish_control(self, action, lane_deviation):
        """发布控制指令"""
        # 速度控制
        twist = Twist()
        twist.linear.x = action['speed']
        twist.angular.z = lane_deviation * 0.5 if not self.turning else 0

        # 转向时保持速度
        if 'turn' in action:
            self.turning = True
            if action['turn'] == 'left':
                twist.angular.z = 1.0
            else:
                twist.angular.z = -1.0
            # 定时恢复
            rospy.Timer(rospy.Duration(2), self.reset_turning, oneshot=True)
        else:
            self.turning = False

        self.cmd_vel_pub.publish(twist)

        # 灯光控制
        if action['light']:
            self.light_pub.publish(String(data=action['light']))

        # 语音播报
        self.voice_pub.publish(String(data=action['voice']))

    def reset_turning(self, event):
        """重置转向标志"""
        self.turning = False

def main():
    rospy.init_node('complete_autonomous_driving')
    driver = CompleteAutonomousDriving()
    rospy.loginfo("完整自动驾驶节点已启动")
    rospy.spin()

if __name__ == '__main__':
    main()
```

### 四、任务C4完整测试流程

| 步骤 | 操作/检测 | 预期动作 |
|------|-----------|----------|
| 1 | 选手手动设置红灯 | 速度=0，4红灯闪烁 |
| 2 | 启动平台 | 初始速度0.2前行 |
| 3 | 检测到右转标志 | 右转，2绿灯闪烁 |
| 4 | 检测到红灯 | 速度=0，4红灯闪烁，语音 |
| 5 | 选手设置黄灯 | 减速，4黄灯闪烁 |
| 6 | 选手设置绿灯 | 速度0.2，绿灯常亮 |
| 7 | 检测到左转标志 | 左转，2绿灯闪烁，语音 |
| 8 | 检测到限速100 | 加速到0.5，语音 |
| 9 | 检测到行人 | 速度=0，黄红灯交替 |
| 10 | 移走行人+检测限速20 | 减速到0.1，语音 |
| 11 | 到达终点 | 停止 |

### 五、任务C4启动文件

**XML文件示例（complete_driving.launch）：**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<launch>
    <!-- YOLO检测节点 -->
    <node name="yolo_detector" pkg="autonomous_driving" type="yolo_detector.py"
          output="screen">
        <param name="model_path" value="$(find autonomous_driving)/models/best.pt" />
    </node>

    <!-- 完整自动驾驶节点 -->
    <node name="complete_driving" pkg="autonomous_driving"
          type="complete_autonomous_driving.py" output="screen">
        <param name="model_path" value="$(find autonomous_driving)/models/best.pt" />
    </node>
</launch>
```

### 六、评判标准

**任务C4综合评判标准：**

| 序号 | 评判项目 | 合格标准 |
|------|----------|----------|
| 1 | 启动响应 | 选手启动后平台自动开始 |
| 2 | 信号灯响应 | 正确识别并响应红/黄/绿灯 |
| 3 | 转向响应 | 正确识别并响应左右转标志 |
| 4 | 限速响应 | 正确识别并调整速度 |
| 5 | 行人响应 | 检测到行人立即停车 |
| 6 | 车道保持 | 全程不超出车道线 |
| 7 | 语音播报 | 各动作对应语音正确播放 |
| 8 | 灯光显示 | 各动作对应灯光正确显示 |

**扣分项：**
- 车轮超出车道线：每次扣分
- 未检测到目标：扣分
- 动作响应错误：扣分
- 人工干预：立即停止评判

***

## 模块C文件存储汇总

### 结果文件夹结构

```
AI0102/                    # 结果存储文件夹（AI+场次号+赛位号）
├── C1/                    # 任务C1
│   ├── yolo_detector.py   # YOLO检测节点
│   ├── light_controller.py # 灯光控制节点
│   ├── voice_player.py     # 语音播报节点
│   ├── auto_drive.py       # 主控决策节点
│   └── auto_drive.launch   # 启动文件
│
├── C2/                    # 任务C2
│   ├── lane_detection.py  # 车道线检测
│   ├── lane_following.py   # 车道巡航
│   └── lane_driving.launch # 启动文件
│
├── C3/                    # 任务C3
│   ├── video_autonomous_driving.py  # 视频自动驾驶
│   └── video_driving.launch          # 启动文件
│
└── C4/                    # 任务C4
    ├── complete_autonomous_driving.py # 完整自动驾驶
    └── complete_driving.launch       # 启动文件
```

### 裁判评判检查清单

**C1模型部署验证：**

| 序号 | 评判内容 | 展示要求 |
|------|----------|----------|
| 1 | 实体红灯 | 4红灯闪烁，速度=0 |
| 2 | 实体黄灯 | 4黄灯闪烁，速度极低 |
| 3 | 实体绿灯 | 4绿灯常亮，正常速度 |
| 4 | 左转标志 | 2绿灯闪烁，左转 |
| 5 | 右转标志 | 2绿灯闪烁，右转 |

**C2车道线检测：**

| 序号 | 评判内容 | 展示要求 |
|------|----------|----------|
| 1 | 车道线检测 | 从起点到终点完成一圈 |
| 2 | 车道保持 | 4轮在车道线内 |

**C3第一视角综合测试：**

| 序号 | 评判内容 | 展示要求 |
|------|----------|----------|
| 1 | 视频处理 | 实时检测和显示 |
| 2 | 灯光语音 | 各动作正确响应 |

**C4第三视角综合测试：**

| 序号 | 评判内容 | 展示要求 |
|------|----------|----------|
| 1 | 完整流程 | 从起点到终点 |
| 2 | 全程无干预 | 自动完成所有动作 |
| 3 | 车道保持 | 全程不超出 |

***

## 常见问题与解决方案

### C1 常见问题

| 问题 | 解决方案 |
|------|----------|
| 模型加载失败 | 检查模型路径是否正确 |
| 检测不到目标 | 调整置信度阈值(conf=0.3) |
| 灯光不亮 | 检查light_control话题名称 |
| 动作响应慢 | 减小图像分辨率提高帧率 |

### C2 常见问题

| 问题 | 解决方案 |
|------|----------|
| 车道线漂移 | 调整PID参数kp |
| 转弯时压线 | 增加转向角度或提前转向 |
| 直线不稳定 | 减小kp或增加kd |

### C3/C4 常见问题

| 问题 | 解决方案 |
|------|----------|
| 视频卡顿 | 使用较小的模型(yolo11n) |
| 语音延迟 | 预加载语音文件 |
| 动作冲突 | 使用优先级机制解决 |
| ROS通信延迟 | 减小图像分辨率或降低检测频率 |

### 性能优化建议

1. **实时性优化**：
   - 使用yolo11n替代yolo11m
   - 降低图像分辨率至320x320
   - 使用ROS image_transport压缩图像

2. **准确性优化**：
   - 使用yolo11s或yolo11m
   - 提高conf阈值至0.6
   - 添加NMS后处理

3. **稳定性优化**：
   - 添加状态机防抖
   - 使用速度平滑滤波器
   - 添加超时保护机制

***

## 竞赛备赛提示

1. **调试顺序**：先C1后C4，逐步集成
2. **测试重点**：灯光闪烁频率(3秒)、速度精确值(0.2/0.5)
3. **安全第一**：务必测试急停功能
4. **时间分配**：C4是综合测试，需要充分调试
5. **备份习惯**：每个节点单独测试后集成
