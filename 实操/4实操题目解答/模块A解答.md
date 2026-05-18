# 模块A：人工智能应用数据集制作 解答与解析

## 概述

模块A占总分的35%，包含4个子任务：

- A1：平台配置与测试
- A2：数据集采集与清洗
- A3：图像数据集标注
- A4：文本数据集标注

***

## 任务A1：人工智能标注、训练算法、部署及验证平台的配置与测试

### 一、任务目标

1. 测试运动单元：使用键盘控制平台前进、后退、左转、右转
2. 测试感知单元：获取头部摄像头和底部摄像头的实时图像
3. 测试交互单元：实现左转/右转的灯光闪烁控制

### 二、软件环境检查

竞赛平台应已预装以下软件：

- ROS机器人操作系统
- Python 3.x
- OpenCV
- Jupyter Notebook

**环境验证步骤：**

```bash
# 1. 检查ROS是否安装
rosversion -d

# 2. 检查Python版本
python --version

# 3. 检查OpenCV
python -c "import cv2; print(cv2.__version__)"

# 4. 检查Jupyter Notebook
jupyter --version
```

### 三、Jupyter Notebook环境配置（ROS 1 Noetic）

竞赛平台已安装ROS 1 Noetic，Jupyter Notebook直接配置即可使用。

**步骤1：导入ROS库（第一个单元格）**

```python
# Jupyter Notebook 第一个单元格：ROS 1环境配置
import rospy
from std_msgs.msg import String

print(f"rospy位置: {rospy.__file__}")
print("ROS 1 环境配置完成 ✓")
```

**步骤2：初始化节点并测试**

```python
# Jupyter Notebook 第二个单元格：初始化ROS节点
import rospy
from std_msgs.msg import String

# 初始化节点
rospy.init_node('jupyter_control', anonymous=True)
print("ROS节点已初始化: jupyter_control")

# 创建发布者
cmd_pub = rospy.Publisher('/cmd_vel', String, queue_size=10)
print("发布者已创建: /cmd_vel")
```

**步骤3：测试发布消息**

```python
# Jupyter Notebook 第三个单元格：测试发布
import rospy
from std_msgs.msg import String

# 发布消息函数
def publish_command(cmd):
    msg = String()
    msg.data = cmd
    cmd_pub.publish(msg)
    print(f"发布指令: {cmd}")

# 测试发送
publish_command("forward")
```

**⚠️ 注意：使用前需要先在终端启动roscore**

```bash
# 在终端运行：
source /opt/ros/noetic/setup.bash
roscore
```

### 四、运动控制程序编写（Jupyter Notebook版本）

**程序功能：** 监听键盘输入，控制平台运动

**Python程序示例（keyboard\_control.ipynb）：**

```python
# Jupyter Notebook 单元格: 非阻塞键盘控制程序
import rospy
from geometry_msgs.msg import Twist
import sys
import select

class KeyboardControl:
    def __init__(self):
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.rate = rospy.Rate(10)
        
        self.speed = rospy.get_param('~speed', 0.5)
        self.turn = rospy.get_param('~turn', 1.0)
        
        self.max_speed = 1.5
        self.max_turn = 2.0
        self.min_speed = 0.1
        
        self.lin_vel = 0.0
        self.ang_vel = 0.0
        self.running = True
        
        self.moveBindings = {
            'w': (1, 0),
            's': (-1, 0),
            'a': (0, 1),
            'd': (0, -1),
            'W': (1, 0),
            'S': (-1, 0),
            'A': (0, 1),
            'D': (0, -1),
        }
        
        self.speedBindings = {
            'q': (1.1, 1.1),
            'z': (0.9, 0.9),
            'Q': (1.1, 1.1),
            'Z': (0.9, 0.9),
        }
        
        self.stop_keys = {'x', 'X', ' ', '\x03'}
    
    def get_key(self):
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            return sys.stdin.read(1)
        return ''
    
    def update_velocity(self, key):
        if key in self.moveBindings:
            dx, dy = self.moveBindings[key]
            self.lin_vel = self.speed * dx
            self.ang_vel = self.turn * dy
            return True, f"移动: 线速度={self.lin_vel:.2f}, 角速度={self.ang_vel:.2f}"
        
        elif key in self.speedBindings:
            scale_lin, scale_ang = self.speedBindings[key]
            self.speed = max(self.min_speed, min(self.max_speed, self.speed * scale_lin))
            self.turn = max(self.min_speed, min(self.max_turn, self.turn * scale_ang))
            return True, f"速度调节: 线速度={self.speed:.2f}, 角速度={self.turn:.2f}"
        
        elif key in self.stop_keys:
            self.lin_vel = 0.0
            self.ang_vel = 0.0
            return True, "停止"
        
        return False, None
    
    def publish_cmd(self):
        twist = Twist()
        twist.linear.x = self.lin_vel
        twist.linear.y = 0.0
        twist.linear.z = 0.0
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = self.ang_vel
        self.cmd_vel_pub.publish(twist)
    
    def print_help(self):
        print("=" * 60)
        print("键盘控制已启动 (非阻塞版本)")
        print("-" * 60)
        print("移动控制:           速度调节:")
        print("  W/w = 前进          Q/q = 加速 (×1.1)")
        print("  S/s = 后退          Z/z = 减速 (×0.9)")
        print("  A/a = 左转")
        print("  D/d = 右转")
        print("-" * 60)
        print("其他: X/x/空格 = 紧急停止, Ctrl+C = 退出")
        print(f"当前速度: 线速度={self.speed:.2f}, 角速度={self.turn:.2f}")
        print("=" * 60)
    
    def run(self):
        self.print_help()
        
        while self.running and not rospy.is_shutdown():
            key = self.get_key()
            
            if key:
                if key in ['\x03']:
                    print("\n[键盘控制] 退出程序")
                    self.lin_vel = 0.0
                    self.ang_vel = 0.0
                    self.publish_cmd()
                    self.running = False
                    break
                
                updated, msg = self.update_velocity(key)
                if updated and msg:
                    print(f"[键盘控制] {msg}")
            
            self.publish_cmd()
            self.rate.sleep()
        
        self.lin_vel = 0.0
        self.ang_vel = 0.0
        self.publish_cmd()
        print("[键盘控制] 程序已停止，机器人已停止")

try:
    rospy.init_node('keyboard_teleop', anonymous=True)
except:
    pass

controller = KeyboardControl()
controller.run()
```

**Jupyter Notebook交互式键盘控制（推荐使用ipywidgets）**

```python
# Jupyter Notebook 单元格: 使用ipywidgets实现交互式控制
# 先安装: pip install ipywidgets

import ipywidgets as widgets
from IPython.display import display, clear_output
import rospy
from std_msgs.msg import String

# 初始化ROS节点
try:
    rospy.init_node('keyboard_control_widgets', anonymous=True)
except:
    pass

cmd_vel_pub = rospy.Publisher('/cmd_vel', String, queue_size=10)

def on_button_click(direction):
    """按钮点击事件"""
    cmd = String()
    cmd_map = {
        'forward': "forward",
        'backward': "backward",
        'left': "left",
        'right': "right",
        'stop': "stop"
    }
    cmd.data = cmd_map.get(direction, "stop")
    cmd_vel_pub.publish(cmd)
    with output:
        clear_output(was_added=True)
        print(f"发送指令: {cmd.data}")

# 创建控制按钮
button_forward = widgets.Button(description='前进(W)', button_style='success')
button_backward = widgets.Button(description='后退(S)', button_style='info')
button_left = widgets.Button(description='左转(A)', button_style='warning')
button_right = widgets.Button(description='右转(D)', button_style='warning')
button_stop = widgets.Button(description='停止(Q)', button_style='danger')

# 绑定事件
button_forward.on_click(lambda x: on_button_click('forward'))
button_backward.on_click(lambda x: on_button_click('backward'))
button_left.on_click(lambda x: on_button_click('left'))
button_right.on_click(lambda x: on_button_click('right'))
button_stop.on_click(lambda x: on_button_click('stop'))

# 布局
button_box = widgets.HBox([button_left, button_forward, button_stop, button_backward, button_right])
output = widgets.Output()

print("=" * 50)
print("交互式键盘控制面板 (Jupyter Notebook)")
print("点击按钮控制平台移动")
print("=" * 50)
display(button_box, output)
```

### 五、摄像头图像获取与自动驾驶视觉感知程序（Jupyter Notebook版本）

**程序功能：** 获取并显示头部和底部摄像头图像，支持自动驾驶视觉感知处理

**Python程序示例（camera\_viewer.ipynb）：**

```python
# ============================================================
# Jupyter Notebook 单元格: 摄像头查看程序
# 功能: 订阅两个摄像头话题，显示实时画面
# 话题: /camera_head/image_raw (头部), /camera_bottom/image_raw (底部)
# ============================================================

# -------------------- 第一部分：导入依赖库 --------------------
import rospy                      # ROS Python库，用于节点通信
import cv2                        # OpenCV计算机视觉库，用于图像处理
from sensor_msgs.msg import Image  # ROS图像消息类型（sensor_msgs包）
from cv_bridge import CvBridge     # ROS图像格式 ↔ OpenCV图像格式 转换桥梁
import numpy as np                # 数值计算库，用于数组和矩阵运算
from IPython.display import display, clear_output  # Jupyter显示输出控制
import ipywidgets as widgets       # Jupyter交互式控件库（按钮、滑块等）

# -------------------- 第二部分：定义自动驾驶视觉感知类 --------------------
class AutonomousVision:
    """自动驾驶视觉感知类：负责图像采集、处理和显示"""

    def __init__(self):
        self.bridge = CvBridge()
        self.head_image = None
        self.bottom_image = None
        self.frame_count = 0
        self.fps = 0
        self.last_time = time.time()

        self.head_sub = rospy.Subscriber('/camera_head/image_raw', Image, self.head_callback)
        self.bottom_sub = rospy.Subscriber('/camera_bottom/image_raw', Image, self.bottom_callback)

    def head_callback(self, data):
        try:
            self.head_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except Exception as e:
            print(f"头部摄像头错误: {e}")

    def bottom_callback(self, data):
        try:
            self.bottom_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except Exception as e:
            print(f"底部摄像头错误: {e}")

    def preprocess_image(self, frame):
        """图像预处理：对比度增强"""
        if frame is None:
            return None
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    def detect_edges(self, frame):
        """边缘检测（Canny算法）"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        return edges

    def detect_lane_lines(self, frame):
        """车道线检测（霍夫变换）"""
        edges = self.detect_edges(frame)
        height, width = edges.shape
        mask = np.zeros_like(edges)
        polygon = np.array([[
            [0, height], [width // 3, height // 2],
            [2 * width // 3, height // 2], [width, height]
        ]], np.int32)
        cv2.fillPoly(mask, polygon, 255)
        masked = cv2.bitwise_and(edges, mask)
        lines = cv2.HoughLinesP(masked, 1, np.pi / 180, 50,
                                minLineLength=50, maxLineGap=50)
        return lines

    def draw_lane_lines(self, frame, lines):
        """绘制车道线"""
        if lines is None:
            return frame
        line_img = np.zeros_like(frame)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_img, (x1, y1), (x2, y2), (0, 255, 0), 3)
        return cv2.addWeighted(frame, 0.8, line_img, 0.2, 0)

    def detect_vehicles(self, frame):
        """车辆检测（基于颜色特征）"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask_red = cv2.inRange(hsv, lower_red, upper_red)
        contours, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        vehicle_count = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                vehicle_count += 1
        return frame, vehicle_count

    def get_display_with_info(self):
        """获取带自动驾驶感知信息的合并显示图像"""
        if self.head_image is None and self.bottom_image is None:
            return None

        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_time = current_time

        height, width = 360, 640
        display_img = np.zeros((height * 2, width, 3), dtype=np.uint8)

        if self.head_image is not None:
            head = cv2.resize(self.head_image, (width, height))
            head_processed = self.preprocess_image(head)
            lines = self.detect_lane_lines(head_processed)
            head_display = self.draw_lane_lines(head_processed, lines)
            cv2.putText(head_display, "Head - Lane Detection", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(head_display, f"FPS: {self.fps}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            display_img[:height, :] = head_display

        if self.bottom_image is not None:
            bottom = cv2.resize(self.bottom_image, (width, height))
            bottom_processed = self.preprocess_image(bottom)
            bottom_display, vehicle_count = self.detect_vehicles(bottom_processed)
            cv2.putText(bottom_display, "Bottom - Vehicle Detection", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(bottom_display, f"Vehicles: {vehicle_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            display_img[height:, :] = bottom_display

        return display_img

# -------------------- 第三部分：初始化和显示 --------------------
vision = AutonomousVision()
image_widget = widgets.Image()
display_widget = widgets.VBox([
    widgets.HTML("<h3>自动驾驶视觉感知系统</h3>"),
    widgets.HTML("<p>Head: Lane Detection | Bottom: Vehicle Detection</p>"),
    image_widget
])

print("=" * 50)
print("自动驾驶视觉感知系统已启动")
print("功能: 车道线检测 + 车辆检测 + 实时FPS")
print("=" * 50)

display(display_widget)

# -------------------- 第四部分：主循环 --------------------
try:
    while True:
        display_img = vision.get_display_with_info()
        if display_img is not None:
            _, buffer = cv2.imencode('.jpg', display_img)
            image_widget.value = buffer.tobytes()
        time.sleep(0.05)
except KeyboardInterrupt:
    print("视觉感知系统已停止")
```

**新增功能说明：**

| 功能 | 方法 | 说明 |
|------|------|------|
| 图像增强 | `preprocess_image()` | CLAHE对比度增强 |
| 边缘检测 | `detect_edges()` | Canny边缘提取 |
| 车道线检测 | `detect_lane_lines()` | 霍夫变换+ROI掩码 |
| 车辆检测 | `detect_vehicles()` | HSV红色特征+轮廓分析 |
| 实时FPS | `get_display_with_info()` | 帧率计算与显示 |

### 五-补充：cv2.VideoCapture摄像头测试代码

**程序功能：** 使用OpenCV直接打开摄像头进行测试（不依赖ROS话题）

**适用场景：** 调试本地摄像头、验证摄像头编号、测试图像采集

**Python程序示例：**

```python
# ============================================================
# Jupyter Notebook 单元格: cv2.VideoCapture摄像头测试
# 功能: 直接打开摄像头测试，无需ROS环境
# ============================================================

import cv2
import numpy as np
from IPython.display import display, clear_output
import ipywidgets as widgets

class CameraTest:
    """摄像头测试类：使用cv2.VideoCapture直接测试摄像头"""

    def __init__(self):
        self.cap = None
        self.cap1 = None
        self.running = False

    def find_available_cameras(self):
        """自动检测可用摄像头"""
        available = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available

    def open_cameras(self, cam0=0, cam1=2):
        """打开指定编号的摄像头"""
        self.cap = cv2.VideoCapture(cam0)
        self.cap1 = cv2.VideoCapture(cam1)

        if not self.cap.isOpened():
            print(f"警告：无法打开摄像头{cam0}")
        if not self.cap1.isOpened():
            print(f"警告：无法打开摄像头{cam1}")

    def read_frames(self):
        """读取双摄像头画面"""
        ret0, frame0 = self.cap.read() if self.cap else (False, None)
        ret1, frame1 = self.cap1.read() if self.cap1 else (False, None)
        return ret0, frame0, ret1, frame1

    def get_combined_display(self, width=640, height=360):
        """获取合并显示图像"""
        ret0, frame0, ret1, frame1 = self.read_frames()
        if not ret0 and not ret1:
            return None

        display_img = np.zeros((height * 2, width, 3), dtype=np.uint8)

        if ret0:
            frame0_resized = cv2.resize(frame0, (width, height))
            cv2.putText(frame0_resized, f"Camera 0 - Bottom", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            display_img[:height, :] = frame0_resized

        if ret1:
            frame1_resized = cv2.resize(frame1, (width, height))
            cv2.putText(frame1_resized, f"Camera 1 - Head", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            display_img[height:, :] = frame1_resized

        return display_img

    def release(self):
        """释放摄像头资源"""
        if self.cap:
            self.cap.release()
        if self.cap1:
            self.cap1.release()
        print("摄像头已关闭")

# -------------------- 测试代码 --------------------
test = CameraTest()

# 方式1：自动检测可用摄像头
print("检测可用摄像头...")
available = test.find_available_cameras()
print(f"可用摄像头编号: {available}")

# 方式2：手动指定摄像头编号
print("\n打开摄像头0和摄像头2...")
test.open_cameras(cam0=0, cam1=2)

# 创建显示控件
image_widget = widgets.Image()
display(widgets.HTML("<h3>cv2.VideoCapture 摄像头测试</h3>"))
display(image_widget)

print("=" * 50)
print("摄像头测试已启动")
print("按 Ctrl+C 停止")
print("=" * 50)

# 主循环
try:
    while True:
        display_img = test.get_combined_display()
        if display_img is not None:
            _, buffer = cv2.imencode('.jpg', display_img)
            image_widget.value = buffer.tobytes()
except KeyboardInterrupt:
    print("\n停止测试")
finally:
    test.release()
```

**两种摄像头获取方式对比：**

| 方式 | 代码 | 优点 | 缺点 |
|------|------|------|------|
| **cv2.VideoCapture** | `cv2.VideoCapture(0)` | 简单直接、无需ROS、可离线使用 | 无法跨设备、需手动管理 |
| **ROS话题订阅** | `rospy.Subscriber(...)` | 跨进程、设备无关、已封装 | 需ROS环境、依赖话题发布 |

**摄像头编号说明：**
- `VideoCapture(0)` - 系统默认摄像头
- `VideoCapture(1)` - 第二个摄像头
- `VideoCapture(2)` - 第三个摄像头（通常USB摄像头）
- 可用 `find_available_cameras()` 自动检测

### 六、灯光控制程序（Jupyter Notebook版本）

**程序功能：** 控制左右转向灯闪烁、交通灯控制

**Python程序示例（light\_control.ipynb）：**

```python
# ============================================================
# Jupyter Notebook 单元格: 灯光控制程序
# 功能: 通过交互按钮控制车辆转向灯和交通灯
# 话题: /light_control (发布灯光控制指令)
# ============================================================

# -------------------- 第一部分：导入依赖库 --------------------
import rospy                      # ROS Python库，用于节点通信
from std_msgs.msg import String    # ROS字符串消息类型
import ipywidgets as widgets       # Jupyter交互式控件库（按钮等）
from IPython.display import display, clear_output  # Jupyter显示控制

# -------------------- 第二部分：初始化ROS节点和发布者 --------------------
# 初始化ROS节点（注意：Jupyter中不能重复初始化，所以用try包裹）
try:
    # rospy.init_node()用于注册节点到ROS Master
    # anonymous=True: 如果有同名节点会自动添加后缀避免冲突
    rospy.init_node('light_control_jupyter', anonymous=True)
except:
    pass  # 如果节点已经初始化过，则跳过

# 创建灯光控制话题的发布者
# 参数1: 话题名  参数2: 消息类型  参数3: 队列大小
light_pub = rospy.Publisher('/light_control', String, queue_size=10)

# -------------------- 第三部分：定义灯光控制器类 --------------------
class LightControl:
    """灯光控制器类：封装所有灯光控制功能"""
    
    def __init__(self):
        """
        构造函数：保存发布者引用
        """
        self.light_pub = light_pub  # 引用外部创建的发布者

    def publish_light(self, command):
        """
        发送灯光指令（内部方法）
        参数: command - 灯光命令字符串（如"left_turn", "red_on"等）
        """
        cmd = String()          # 创建String消息对象
        cmd.data = command      # 设置消息内容为命令字符串
        self.light_pub.publish(cmd)  # 通过发布者发送消息到ROS话题
        print(f"[灯光控制] 发送指令: {command}")  # 打印日志

    def turn_left_flash(self):
        """
        左转向灯闪烁方法：发送15次左转信号，间隔0.2秒
        总时长 = 15次 * 0.2秒 = 3秒
        """
        print("[灯光控制] 左转向灯闪烁...")
        for _ in range(15):           # 循环15次
            self.publish_light("left_turn")  # 发送"left_turn"指令
            import time               # 导入时间库（循环内导入避免全局污染）
            time.sleep(0.2)           # 休眠0.2秒，控制闪烁频率

    def turn_right_flash(self):
        """
        右转向灯闪烁方法：发送15次右转信号，间隔0.2秒
        总时长 = 15次 * 0.2秒 = 3秒
        """
        print("[灯光控制] 右转向灯闪烁...")
        for _ in range(15):
            self.publish_light("right_turn")  # 发送"right_turn"指令
            import time
            time.sleep(0.2)

    def red_light(self):
        """红灯常亮方法：发送"red_on"指令"""
        self.publish_light("red_on")

    def yellow_light(self):
        """黄灯常亮方法：发送"yellow_on"指令"""
        self.publish_light("yellow_on")

    def green_light(self):
        """绿灯常亮方法：发送"green_on"指令"""
        self.publish_light("green_on")

    def all_off(self):
        """关闭所有灯方法：发送"all_off"指令"""
        self.publish_light("all_off")

# -------------------- 第四部分：创建交互界面 --------------------
# 创建灯光控制实例（必须在按钮创建之前）
controller = LightControl()

# 创建转向灯控制按钮
# Button: ipywidgets按钮控件
# description: 按钮显示文字
# button_style: 按钮样式 ('warning'=黄色, 'danger'=红色, 'success'=绿色, 'info'=蓝色)
# layout: 按钮布局设置（宽度150像素）
button_left = widgets.Button(
    description='左转向灯',           # 按钮文字
    button_style='warning',           # 黄色样式（表示警示）
    layout=widgets.Layout(width='150px')  # 按钮宽度150像素
)
button_right = widgets.Button(
    description='右转向灯',
    button_style='warning',
    layout=widgets.Layout(width='150px')
)

# 创建交通灯控制按钮（红、黄、绿）
button_red = widgets.Button(
    description='红灯',                # 红色按钮
    button_style='danger',            # 红色样式
    layout=widgets.Layout(width='100px')
)
button_yellow = widgets.Button(
    description='黄灯',
    button_style='warning',
    layout=widgets.Layout(width='100px')
)
button_green = widgets.Button(
    description='绿灯',
    button_style='success',          # 绿色样式
    layout=widgets.Layout(width='100px')
)
button_off = widgets.Button(
    description='关闭所有灯',
    button_style='info',
    layout=widgets.Layout(width='100px')
)

# -------------------- 第五部分：绑定按钮事件 --------------------
# on_click: 按钮点击事件，绑定回调函数
# lambda x: ... : 匿名函数，x是按钮对象（点击时触发）
button_left.on_click(lambda x: controller.turn_left_flash())    # 左转按钮 -> 左转闪烁
button_right.on_click(lambda x: controller.turn_right_flash())  # 右转按钮 -> 右转闪烁
button_red.on_click(lambda x: controller.red_light())           # 红灯按钮 -> 红灯常亮
button_yellow.on_click(lambda x: controller.yellow_light())       # 黄灯按钮 -> 黄灯常亮
button_green.on_click(lambda x: controller.green_light())        # 绿灯按钮 -> 绿灯常亮
button_off.on_click(lambda x: controller.all_off())              # 关闭按钮 -> 关闭所有灯

# -------------------- 第六部分：界面布局和显示 --------------------
# HBox: 水平布局容器，将多个控件水平排列
traffic_lights = widgets.HBox([button_red, button_yellow, button_green, button_off])
turn_signals = widgets.HBox([button_left, button_right])

# Output: Jupyter输出控件，用于显示程序打印的信息
output = widgets.Output()

def show_status(message):
    """
    在Output控件中显示状态信息
    参数: message - 要显示的消息字符串
    """
    # with output: 将print输出重定向到Output控件
    with output:
        clear_output(wait=True)  # 清空之前的输出，wait=True防止闪烁
        print(message)          # 打印消息

# 打印界面标题
print("=" * 50)
print("灯光控制面板 (Jupyter Notebook)")
print("=" * 50)

# VBox: 垂直布局容器，将多个控件垂直排列
display(widgets.VBox([
    widgets.HTML("<h3>转向灯控制</h3>"),  # 转向灯区域标题
    turn_signals,                         # 转向灯按钮（左右）
    widgets.HTML("<h3>交通灯控制</h3>"),  # 交通灯区域标题
    traffic_lights,                        # 交通灯按钮（红黄绿+关闭）
    output                                  # 输出信息区域
]))
```

**灯光指令对照表：**

| 指令           | 功能     |
| ------------ | ------ |
| `left_turn`  | 左转向灯闪烁 |
| `right_turn` | 右转向灯闪烁 |
| `red_on`     | 红灯常亮   |
| `yellow_on`  | 黄灯常亮   |
| `green_on`   | 绿灯常亮   |
| `all_off`    | 关闭所有灯  |

```
                      layout=widgets.Layout(width='150px'))
```

# 绑定事件

button\_left.on\_click(lambda x: controller.turn\_left\_flash())
button\_right.on\_click(lambda x: controller.turn\_right\_flash())
button\_red.on\_click(lambda x: controller.red\_light())
button\_yellow\.on\_click(lambda x: controller.yellow\_light())
button\_green.on\_click(lambda x: controller.green\_light())
button\_off.on\_click(lambda x: controller.all\_off())

# 布局

traffic\_lights = widgets.HBox(\[button\_red, button\_yellow, button\_green, button\_off])
turn\_signals = widgets.HBox(\[button\_left, button\_right])

output = widgets.Output()

def show\_status(message):
with output:
clear\_output(was\_added=True)
print(message)

print("=" \* 50)
print("灯光控制面板 (Jupyter Notebook)")
print("=" \* 50)
display(widgets.VBox(\[
widgets.HTML("<h3>转向灯控制</h3>"),
turn\_signals,
widgets.HTML("<h3>交通灯控制</h3>"),
traffic\_lights,
output
]))

````

### 七、Jupyter Notebook操作步骤汇总

| 步骤 | 操作                 | 说明                          |
| -- | ------------------ | --------------------------- |
| 1  | 创建结果存储文件夹          | 在桌面创建AI0102文件夹              |
| 2  | 打开Jupyter Notebook | jupyter notebook            |
| 3  | 新建notebook         | New → Python3               |
| 4  | 运行ROS环境配置单元格       | 配置rospy环境                   |
| 5  | 运行键盘控制程序           | 使用交互式按钮或input()             |
| 6  | 按A/D/W/S测试左右前后运动   | 观察平台运动                      |
| 7  | 运行摄像头程序            | 在Notebook中显示双摄像头            |
| 8  | 测试转向灯控制            | 使用交互式按钮                     |
| 9  | 保存notebook到结果文件夹   | File → Download as → Python |

### 八、Launch文件编写（备选方案）

如果需要在终端运行而非Jupyter Notebook，可使用launch文件：

**launch文件示例（platform\_test.launch）：**

```xml
<launch>
    <node name="keyboard_control" pkg="ai_platform" type="keyboard_control.py" output="screen"/>
    <node name="camera_viewer" pkg="ai_platform" type="camera_viewer.py" output="screen"/>
    <node name="light_control" pkg="ai_platform" type="light_control.py" output="screen"/>
</launch>
````

**运行launch文件：**

```bash
source /opt/ros/noetic/setup.bash
roslaunch ai_platform platform_test.launch
```

### 九、评判要点

1. **运动控制**：按A/D/W/S键时平台正确运动，松开停止
2. **摄像头显示**：头部和底部摄像头画面清晰
3. **灯光控制**：左转左灯闪，右转右灯闪，每种≥3秒

***

## 任务A2：人工智能应用数据集采集与清洗

### 一、任务目标

1. 采集8类目标图像（红灯、黄灯、绿灯、限速20、限速100、左转、右转、行人）
2. 图像总数≥400张
3. 按奇数序号重命名（AI0001.jpg、AI0003.jpg...）
4. 生成分类统计柱状图

### 二、标注类别（8类）

| 类别序号 | 类别名称          | 说明      |
| ---- | ------------- | ------- |
| 0    | person        | 行人模型    |
| 1    | turn\_left    | 左转向标志   |
| 2    | turn\_right   | 右转向标志   |
| 3    | limit\_20     | 限速20标志  |
| 4    | limit\_100    | 限速100标志 |
| 5    | red\_light    | 红灯      |
| 6    | yellow\_light | 黄灯      |
| 7    | green\_light  | 绿灯      |

### 三、图像采集程序

**Python程序示例（image\_capture.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像采集程序
功能：从摄像头或素材目录采集8类目标图像
类别：红灯、黄灯、绿灯、限速20、限速100、左转、右转、行人
"""

# -------------------- 第一部分：导入依赖库 --------------------
import cv2                          # OpenCV计算机视觉库，用于图像读取和写入
import os                           # 操作系统库，用于文件和目录操作
import time                         # 时间库，用于控制采集间隔
from datetime import datetime       # 日期时间库（未使用，保留扩展）
import shutil                       # 文件操作库，用于复制文件

# -------------------- 第二部分：定义图像采集类 --------------------
class ImageCapture:
    """图像采集器类：支持从摄像头和目录两种方式采集图像"""
    
    def __init__(self, save_dir="captured_images"):
        """
        构造函数：初始化保存目录和计数器
        参数: save_dir - 图像保存目录路径
        """
        self.save_dir = save_dir                      # 保存目录路径
        self.counter = 1                              # 文件计数器，从1开始
        os.makedirs(save_dir, exist_ok=True)          # 创建保存目录（如果不存在）

        # 尝试打开摄像头（0表示第一个摄像头设备）
        self.cap = cv2.VideoCapture(0)                # VideoCapture: OpenCV视频捕获对象
        if not self.cap.isOpened():                   # isOpened(): 检查摄像头是否打开成功
            print("警告：无法打开摄像头，将从素材目录读取")

    def capture_from_camera(self, num_images=50):
        """
        从摄像头采集图像方法
        参数: num_images - 采集图像数量，默认50张
        """
        print(f"开始从摄像头采集{num_images}张图像...")  # 打印开始信息
        for i in range(num_images):                   # 循环采集指定数量图像
            ret, frame = self.cap.read()              # read(): 读取一帧图像
                                                     # ret: 读取是否成功(True/False)
                                                     # frame: 读取的图像矩阵（numpy数组）
            if ret:                                    # 如果读取成功
                # 生成文件名：raw_0001.jpg, raw_0002.jpg...
                # {self.counter:04d} 表示4位数字，不足前面补0
                filename = f"raw_{self.counter:04d}.jpg"
                filepath = os.path.join(self.save_dir, filename)  # 拼接完整路径
                cv2.imwrite(filepath, frame)        # imwrite(): 保存图像到文件
                print(f"已保存: {filename}")         # 打印保存信息
                self.counter += 1                   # 计数器加1
            time.sleep(0.1)                          # 休眠0.1秒，控制采集速度（约10FPS）

    def capture_with_keypress(self):
        """
        按键保存模式：实时预览摄像头，按P键保存图像
        按ESC键退出
        """
        print("=" * 50)
        print("按键保存模式已启动")
        print("操作说明:")
        print("  P - 保存当前帧到本地")
        print("  ESC - 退出程序")
        print("=" * 50)

        while True:
            ret, frame = self.cap.read()  # 读取摄像头帧
            if not ret:
                print("无法读取摄像头画面")
                break

            cv2.imshow("Camera - Press P to Save, ESC to Exit", frame)

            key = cv2.waitKey(1) & 0xFF  # 等待按键，1ms超时
            if key == ord('p') or key == ord('P'):
                filename = f"raw_{self.counter:04d}.jpg"
                filepath = os.path.join(self.save_dir, filename)
                cv2.imwrite(filepath, frame)
                print(f"[已保存] {filename} (共{self.counter}张)")
                self.counter += 1
            elif key == 27:  # ESC键的ASCII码是27
                print("退出按键保存模式")
                break

        cv2.destroyAllWindows()

    def capture_from_directory(self, source_dir, num_per_class=50):
        """
        从素材目录复制图像方法（用于没有摄像头时）
        参数: 
            source_dir - 素材目录路径
            num_per_class - 每个类别采集的数量
        """
        # 定义8个类别（与A3标注任务一致）
        categories = ['red_light', 'yellow_light', 'green_light',  # 交通灯类
                      'limit_20', 'limit_100',                     # 限速标志类
                      'turn_left', 'turn_right',                   # 转向标志类
                      'person']                                    # 行人类

        for category in categories:                   # 遍历每个类别目录
            cat_dir = os.path.join(source_dir, category)  # 拼接类别目录路径
            if not os.path.exists(cat_dir):            # 检查目录是否存在
                print(f"目录不存在: {cat_dir}")
                continue                              # 跳过不存在的目录

            # 列出目录中所有jpg和png文件
            # endswith(): 检查文件扩展名
            images = [f for f in os.listdir(cat_dir) if f.endswith(('.jpg', '.png'))]
            count = 0                                   # 该类别已采集数量
            for img_file in images[:num_per_class]:    # 只取前num_per_class张
                src_path = os.path.join(cat_dir, img_file)   # 源文件路径
                filename = f"raw_{self.counter:04d}.jpg"      # 新文件名
                dst_path = os.path.join(self.save_dir, filename)  # 目标路径

                shutil.copy2(src_path, dst_path)       # copy2(): 复制文件并保留元数据
                print(f"已复制: {filename} <- {img_file}")  # 打印复制信息
                self.counter += 1                      # 计数器加1
                count += 1                             # 该类别计数加1

            print(f"{category}: 已采集{count}张")      # 打印该类别统计

    def release(self):
        """释放摄像头资源"""
        if self.cap:                                   # 如果摄像头对象存在
            self.cap.release()                         # release(): 释放摄像头资源
            print("摄像头已关闭")

# -------------------- 第三部分：主程序入口 --------------------
if __name__ == '__main__':
    # __name__ == '__main__' 表示直接运行此脚本（而非被导入）
    capture = ImageCapture("captured_images")         # 创建采集器实例

    # 根据实际情况选择采集方式
    # 方式1：自动采集指定数量
    # capture.capture_from_camera(100)

    # 方式2：按键保存模式（推荐！）实时预览，按P键保存
    capture.capture_with_keypress()

    # 方式3：从素材目录采集（每个类别50张）
    # capture.capture_from_directory("素材目录", 50)
    
    capture.release()                                  # 释放资源
```

### 四、图像清洗程序

**Python程序示例（image\_cleaner.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像清洗程序
功能：过滤掉无效、模糊、过小的图像
保留有效图像到清洗后的目录
"""

# -------------------- 第一部分：导入依赖库 --------------------
import os                               # 操作系统库，文件和目录操作
import cv2                              # OpenCV库，图像处理和分析
import shutil                           # 文件操作库，移动文件

# -------------------- 第二部分：定义图像清洗类 --------------------
class ImageCleaner:
    """图像清洗器类：检测并过滤无效图像"""
    
    def __init__(self, source_dir, dest_dir):
        """
        构造函数：设置源目录和目标目录
        参数:
            source_dir - 原始图像目录（待清洗）
            dest_dir - 清洗后图像保存目录
        """
        self.source_dir = source_dir                      # 源目录路径
        self.dest_dir = dest_dir                        # 目标目录路径
        os.makedirs(dest_dir, exist_ok=True)            # 创建目标目录

    def is_valid_image(self, image_path):
        """
        检查图像是否有效（核心检测方法）
        参数: image_path - 图像文件路径
        返回: (是否有效, 原因描述) 元组
        """
        try:
            # cv2.imread(): 读取图像文件
            # 如果读取失败或文件损坏，返回None
            img = cv2.imread(image_path)
            if img is None:                             # None表示读取失败
                return False, "无法读取图像"

            # img.shape[:2] 获取图像尺寸 (高度, 宽度)
            height, width = img.shape[:2]
            
            # 过滤条件1：图像尺寸必须大于100x100像素
            if height < 100 or width < 100:
                return False, f"图像尺寸过小: {width}x{height}"

            # 过滤条件2：检测图像模糊程度（使用Laplacian算子）
            # Laplacian算子可以检测图像边缘，模糊图像边缘不明显
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换为灰度图
            # Laplacian(): 计算Laplacian梯度
            # CV_64F: 64位浮点数输出（为了精度）
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # 方差越小表示图像越模糊，通常阈值为100
            if laplacian_var < 100:
                return False, f"图像模糊: Laplacian={laplacian_var:.2f}"

            # 所有检查通过
            return True, "正常"
            
        except Exception as e:                          # 捕获任何异常
            return False, str(e)

    def clean_images(self):
        """
        执行图像清洗
        返回: (有效图像数量, 无效图像数量)
        """
        valid_count = 0                                # 有效图像计数器
        invalid_count = 0                              # 无效图像计数器
        invalid_log = []                               # 无效图像日志列表

        # 列出源目录中所有图像文件
        images = [f for f in os.listdir(self.source_dir)  # 遍历源目录文件
                  if f.endswith(('.jpg', '.png', '.jpeg'))]  # 只选择图片格式

        for img_file in images:                         # 遍历每张图像
            src_path = os.path.join(self.source_dir, img_file)  # 源文件路径
            is_valid, reason = self.is_valid_image(src_path)  # 检查图像有效性

            if is_valid:                                # 如果图像有效
                dst_path = os.path.join(self.dest_dir, img_file)  # 目标路径
                shutil.move(src_path, dst_path)        # move(): 移动文件到目标目录
                valid_count += 1                       # 有效计数加1
            else:                                       # 如果图像无效
                invalid_count += 1                     # 无效计数加1
                invalid_log.append(f"{img_file}: {reason}")  # 记录无效原因

        # 打印统计信息
        print(f"\n清洗完成:")
        print(f"  有效图像: {valid_count}张")
        print(f"  无效图像: {invalid_count}张")
        print(f"\n无效图像列表:")
        for log in invalid_log:                        # 遍历并打印无效图像日志
            print(f"  {log}")

        return valid_count, invalid_count

# -------------------- 第三部分：主程序入口 --------------------
if __name__ == '__main__':
    # 创建清洗器实例：源目录 -> 目标目录
    cleaner = ImageCleaner("captured_images", "cleaned_images")
    # 执行清洗
    cleaner.clean_images()
```

**Laplacian模糊检测原理：**

| Laplacian方差 | 图像状态 | 说明        |
| ----------- | ---- | --------- |
| > 200       | 清晰   | 边缘明显，纹理清晰 |
| 100 \~ 200  | 正常   | 可接受的清晰度   |
| < 100       | 模糊   | 边缘模糊，细节丢失 |

### 五、重命名程序

**Python程序示例（rename.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像重命名程序
功能：将图像按奇数序号重命名
格式：AI0001.jpg, AI0003.jpg, AI0005.jpg...
"""

# -------------------- 第一部分：导入依赖库 --------------------
import os                               # 操作系统库，文件和目录操作
import shutil                           # 文件操作库，复制/移动文件

# -------------------- 第二部分：定义图像重命名类 --------------------
class ImageRenamer:
    """图像重命名器类：将图像按奇数序号重命名"""
    
    def __init__(self, source_dir, dest_dir=None):
        """
        构造函数：设置源目录和目标目录
        参数:
            source_dir - 源图像目录
            dest_dir - 目标目录（默认与源目录相同，即原地重命名）
        """
        self.source_dir = source_dir                      # 源目录路径
        self.dest_dir = dest_dir if dest_dir else source_dir  # 如果未指定目标目录，则使用源目录
        os.makedirs(self.dest_dir, exist_ok=True)        # 创建目标目录

    def rename_to_odd_sequence(self, start_num=1):
        """
        按奇数序号重命名方法（核心功能）
        参数: start_num - 起始序号，默认从1开始
        
        示例：start_num=1 -> 1, 3, 5, 7...
        示例：start_num=2 -> 2, 4, 6, 8...
        """
        # 列出源目录中所有图像文件（不区分大小写扩展名）
        images = [f for f in os.listdir(self.source_dir)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        # sort(): 按文件名排序，保证处理顺序一致（避免随机顺序）
        images.sort()

        print(f"开始重命名，共{len(images)}张图像")

        # enumerate(): 遍历列表，同时获取索引和元素
        for i, old_name in enumerate(images):
            # 计算奇数序号的公式：
            # i=0 -> odd_num=1, i=1 -> odd_num=3, i=2 -> odd_num=5, ...
            odd_num = start_num + (i * 2)

            # os.path.splitext(): 分离文件名和扩展名
            # 返回 (文件名, 扩展名) 元组，如 ("image", ".jpg")
            ext = os.path.splitext(old_name)[1].lower()  # 获取扩展名并转为小写

            # 生成新文件名：AI + 4位数字 + 扩展名
            # :04d 表示4位数字，不足前面补0，如 1->0001, 10->0010
            new_name = f"AI{odd_num:04d}{ext}"

            # 拼接完整的源路径和目标路径
            src_path = os.path.join(self.source_dir, old_name)  # 原始文件路径
            dst_path = os.path.join(self.dest_dir, new_name)    # 新文件路径

            # 判断是重命名还是复制
            if self.source_dir == self.dest_dir:
                # 原地重命名：使用os.rename
                os.rename(src_path, dst_path)
            else:
                # 复制到新目录：使用shutil.copy2保留元数据
                shutil.copy2(src_path, dst_path)

            print(f"{old_name} -> {new_name}")  # 打印重命名日志

        print(f"\n重命名完成，共{len(images)}张图像")

    def get_statistics(self):
        """
        获取重命名后的统计信息
        返回: 以AI开头的图像文件数量
        """
        # 列出目标目录中以AI开头且为图片格式的文件
        images = [f for f in os.listdir(self.dest_dir)
                  if f.lower().startswith('ai') and       # startswith(): 检查是否以'ai'开头
                     f.lower().endswith(('.jpg', '.png'))]  # endswith(): 检查扩展名
        return len(images)                                 # 返回文件数量

# -------------------- 第三部分：主程序入口 --------------------
if __name__ == '__main__':
    # 创建重命名器实例：cleaned_images -> renamed_images
    renamer = ImageRenamer("cleaned_images", "renamed_images")
    
    # 执行奇数序号重命名（从1开始）
    renamer.rename_to_odd_sequence(start_num=1)
    
    # 获取并打印统计信息
    count = renamer.get_statistics()
    print(f"统计：共{count}张图像已重命名")
```

**重命名示例：**

| 原始文件名         | 新文件名       |
| ------------- | ---------- |
| raw\_0001.jpg | AI0001.jpg |
| raw\_0002.jpg | AI0003.jpg |
| raw\_0003.jpg | AI0005.jpg |
| ...           | ...        |

### 六、分类统计柱状图程序

**Python程序示例（visualization.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分类统计柱状图程序
功能：统计各类别图像数量并绘制柱状图
用于可视化数据集分布情况
"""

# -------------------- 第一部分：导入依赖库 --------------------
import matplotlib.pyplot as plt                 # matplotlib绘图库，用于生成柱状图
import os                                       # 操作系统库，文件操作
from collections import Counter                 # 计数器容器，统计元素出现次数

# -------------------- 第二部分：定义数据可视化类 --------------------
class DataVisualizer:
    """数据可视化类：统计图像类别并绘制柱状图"""
    
    def __init__(self, image_dir):
        """
        构造函数：设置图像目录
        参数: image_dir - 图像所在目录路径
        """
        self.image_dir = image_dir                               # 图像目录路径

    def extract_category_from_filename(self, filename):
        """
        从文件名提取类别名称（核心方法）
        参数: filename - 图像文件名，如 "AI0001_red_light.jpg"
        返回: 类别名称字符串，如 "red_light"
        
        注意：此方法假设文件命名包含类别关键词
        """
        # 定义8个类别列表
        categories = ['red_light', 'yellow_light', 'green_light',  # 交通灯类
                      'limit_20', 'limit_100',                    # 限速标志类
                      'turn_left', 'turn_right',                   # 转向标志类
                      'person']                                    # 行人类

        filename_lower = filename.lower()  # 转为小写，避免大小写匹配问题

        # 遍历类别列表，查找文件名中是否包含类别关键词
        for cat in categories:
            if cat in filename_lower:     # 如果文件名中包含该类别关键词
                return cat                 # 返回该类别名称

        # 如果没有匹配到任何类别，返回'unknown'
        return 'unknown'

    def count_categories(self):
        """
        统计各类别图像数量
        返回: 字典 {类别名称: 数量}，如 {'red_light': 50, 'person': 30, ...}
        """
        # 列出目录中所有图像文件
        images = [f for f in os.listdir(self.image_dir)
                  if f.endswith(('.jpg', '.png', '.jpeg'))]

        categories = []                    # 存储所有图像的类别列表
        for img in images:                 # 遍历每张图像
            cat = self.extract_category_from_filename(img)  # 提取类别
            categories.append(cat)         # 添加到列表

        # Counter(): 统计列表中每个元素出现的次数
        # 如 ['a', 'b', 'a'] -> Counter({'a': 2, 'b': 1})
        counter = Counter(categories)
        return dict(counter)               # 转换为普通字典返回

    def plot_bar_chart(self, save_path="category_distribution.png"):
        """
        绘制并保存分类统计柱状图
        参数: save_path - 图片保存路径
        返回: 统计字典
        """
        stats = self.count_categories()   # 获取统计结果

        # -------------------- 配置中文字体 --------------------
        # matplotlib默认不支持中文，需要设置中文字体
        # rcParams: 运行时配置参数（类似全局设置）
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 优先使用黑体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        # -------------------- 准备绘图数据 --------------------
        categories = list(stats.keys())   # 类别名称列表
        counts = list(stats.values())     # 数量列表

        # -------------------- 创建画布和坐标轴 --------------------
        # figsize=(12, 6): 画布尺寸12英寸宽、6英寸高
        fig, ax = plt.subplots(figsize=(12, 6))

        # -------------------- 绘制柱状图 --------------------
        # ax.bar(): 绘制柱状图
        # color参数：根据类别名称自动设置颜色
        bars = ax.bar(categories, counts,
                     color=['red' if 'red' in c else           # 红色类 -> 红色
                            'yellow' if 'yellow' in c else    # 黄色类 -> 黄色
                            'green' if 'green' in c else      # 绿色类 -> 绿色
                            'steelblue' for c in categories])  # 其他 -> 蓝色

        # -------------------- 设置标题和轴标签 --------------------
        ax.set_title('图像数据集分类统计', fontsize=16)  # 图表标题，16号字
        ax.set_xlabel('类别', fontsize=12)               # X轴标签（类别名称）
        ax.set_ylabel('数量', fontsize=12)               # Y轴标签（图像数量）

        # -------------------- 设置X轴刻度标签 --------------------
        # rotation=45: 标签旋转45度避免重叠
        # ha='right': 右对齐
        ax.set_xticklabels(categories, rotation=45, ha='right')

        # -------------------- 在柱子上显示数量 --------------------
        # zip(bars, counts): 配对柱子和对应数量
        for bar, count in zip(bars, counts):
            height = bar.get_height()     # get_height(): 获取柱子高度（Y值）
            # text(): 在指定位置添加文本
            # bar.get_x() + bar.get_width()/2: 柱子中心X坐标
            # height: Y坐标（在柱子顶部）
            # f'{int(count)}': 显示的数量（整数）
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(count)}',
                    ha='center', va='bottom', fontsize=10)  # 居中显示

        # -------------------- 保存和显示 --------------------
        plt.tight_layout()                # tight_layout(): 自动调整子图参数防止重叠
        plt.savefig(save_path, dpi=150)  # 保存图片，分辨率150 DPI
        print(f"柱状图已保存至: {save_path}")

        plt.show()                       # 显示图形窗口

        return stats

# -------------------- 第三部分：主程序入口 --------------------
if __name__ == '__main__':
    # 创建可视化器实例
    visualizer = DataVisualizer("renamed_images")
    
    # 绘制柱状图并保存
    stats = visualizer.plot_bar_chart("category_distribution.png")

    # 打印分类统计结果
    print("\n分类统计结果:")
    
    # sorted(): 排序
    # key=lambda x: x[1], reverse=True: 按数量降序排列
    for cat, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}张")
```

**柱状图示例输出：**

```
分类统计结果:
  red_light: 55张
  person: 52张
  turn_left: 51张
  green_light: 50张
  ...
```

### 七、操作步骤汇总

| 步骤 | 操作       | 命令/方法                             |
| -- | -------- | --------------------------------- |
| 1  | 创建目录结构   | mkdir -p A2/图像清洗 A2/柱状图           |
| 2  | 采集原始图像   | python image\_capture.py          |
| 3  | 清洗不合格图像  | python image\_cleaner.py          |
| 4  | 重命名为奇数序号 | python rename.py                  |
| 5  | 生成统计柱状图  | python visualization.py           |
| 6  | 复制到结果文件夹 | cp -r renamed\_images/\* A2/图像清洗/ |

### 八、评判要点

1. **图像数量**：≥400张（红灯、黄灯、绿灯、限速20、限速100、左转、右转、行人）
2. **命名规范**：AI0001.jpg、AI0003.jpg...奇数序号
3. **柱状图要求**：
   - 横坐标为类别
   - 柱子底部显示类别名称
   - 柱子顶部显示数量

***

## 任务A3：图像数据集标注

### 一、任务目标

1. 使用Label-Studio对8类目标进行标注
2. 输出VOC、COCO、YOLO格式数据集
3. 图像拼接可视化（10×10网格）
4. 数据集划分（训练集:验证集:测试集 = 7:2:1）

### 二、标注类别（必须严格按此顺序）

| 类别序号 | 类别名称          | 说明      |
| ---- | ------------- | ------- |
| 0    | person        | 行人模型    |
| 1    | turn\_left    | 左转向标志   |
| 2    | turn\_right   | 右转向标志   |
| 3    | limit\_20     | 限速20标志  |
| 4    | limit\_100    | 限速100标志 |
| 5    | red\_light    | 红灯      |
| 6    | yellow\_light | 黄灯      |
| 7    | green\_light  | 绿灯      |

### 三、Label-Studio安装与配置

**安装步骤：**

```bash
# 1. 使用pip安装
pip install label-studio

# 2. 启动Label-Studio
label-studio start

# 3. 首次启动会提示创建管理员账户

# 4. 访问Web界面（通常为 http://localhost:8080）
```

**配置步骤：**

1. 登录后创建新项目
2. 项目名称：`自动驾驶交通标志标注`
3. 选择标注模板：Object Detection
4. 添加标注类别（按表4顺序）
5. 导入图像数据集

### 四、Label-Studio标注界面操作

**标注流程：**

1. 登录Label-Studio Web界面
2. 进入项目 -> 导入 -> 选择`A2/图像清洗`文件夹
3. 开始标注：
   - 选择图像
   - 点击`Create Region`
   - 拖动绘制边界框
   - 选择对应标签
   - 保存
4. 导出标注结果

### 五、数据集格式导出（Label-Studio原生支持）

**推荐：使用Label-Studio直接导出YOLO格式（最简单）**

#### Label-Studio导出YOLO步骤：

1. 进入Label-Studio项目
2. 点击右上角 **"Export"** 按钮
3. 在格式选择列表中选择 **"YOLO"**
4. 点击 **"Export"** 下载ZIP包
5. 解压后得到完整的YOLO格式数据集

#### 导出后的YOLO数据集结构：

```
yolo_export.zip
├── classes.txt              # 类别文件
├── images/                   # 图像文件夹
│   ├── img001.jpg
│   ├── img002.jpg
│   └── ...
├── labels/                   # 标注文件夹
│   ├── img001.txt
│   ├── img002.txt
│   └── ...
└── README.txt               # 说明文件
```

#### YOLO标注文件格式说明：

```
# 每行表示一个目标：class_id x_center y_center width height
# 所有值都归一化到0-1
0 0.512 0.483 0.156 0.312   # class 0: person
1 0.234 0.567 0.089 0.123   # class 1: turn_left
```

***

### 备选方案：手动转换（如果原生导出有问题）

**YOLO格式手动转换（yolo\_converter.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import shutil

class YOLOConverter:
    def __init__(self, image_dir, output_dir):
        self.image_dir = image_dir
        self.output_dir = output_dir
        os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "labels"), exist_ok=True)

        self.categories = [
            "person", "turn_left", "turn_right", "limit_20",
            "limit_100", "red_light", "yellow_light", "green_light"
        ]

    def convert(self, labelstudio_export_file):
        """转换Label-Studio导出文件为YOLO格式"""
        with open(labelstudio_export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            image_filename = item['data']['image'].split('/')[-1]
            img_width = item['meta']['image_width']
            img_height = item['meta']['image_height']

            annotations = item['annotations'][0]['result']
            yolo_labels = []

            for ann in annotations:
                if ann['type'] == 'rectanglelabels':
                    bbox = ann['value']
                    x_center = (bbox['x'] + bbox['width']/2) / 100
                    y_center = (bbox['y'] + bbox['height']/2) / 100
                    width = bbox['width'] / 100
                    height = bbox['height'] / 100

                    label_name = bbox['rectanglelabels'][0]
                    class_id = self.categories.index(label_name)

                    yolo_labels.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

            label_filename = image_filename.replace('.jpg', '.txt').replace('.png', '.txt')
            label_path = os.path.join(self.output_dir, "labels", label_filename)
            with open(label_path, 'w') as f:
                f.write('\n'.join(yolo_labels))

            src_img = os.path.join(self.image_dir, image_filename)
            dst_img = os.path.join(self.output_dir, "images", image_filename)
            if os.path.exists(src_img):
                shutil.copy2(src_img, dst_img)

        with open(os.path.join(self.output_dir, "classes.txt"), 'w') as f:
            f.write('\n'.join(self.categories))

        print(f"YOLO格式转换完成，保存至: {self.output_dir}")
```

**使用示例：**

```python
converter = YOLOConverter("A2/图像清洗", "A3/YOLO格式")
converter.convert("labelstudio_export.json")
```

### 六、图像拼接可视化程序

**Python程序示例（image\_stitch.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
import numpy as np
from pathlib import Path

def stitch_images(image_dir, output_path='stitched_result.jpg', cols=3):
    """拼接多张图像为网格形式"""
    image_paths = sorted(Path(image_dir).glob('*.jpg'))
    if not image_paths:
        print(f"未找到图像文件: {image_dir}")
        return

    images = []
    for path in image_paths:
        img = cv2.imread(str(path))
        if img is not None:
            images.append(img)

    if not images:
        print("没有可读的图像")
        return

    rows = (len(images) + cols - 1) // cols
    h, w = images[0].shape[:2]

    stitched = np.zeros((rows * h, cols * w, 3), dtype=np.uint8)

    for idx, img in enumerate(images):
        row = idx // cols
        col = idx % cols
        stitched[row*h:(row+1)*h, col*w:(col+1)*w] = img

    cv2.imwrite(output_path, stitched)
    print(f"图像拼接完成: {output_path}")
    return output_path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='图像拼接工具')
    parser.add_argument('--input', '-i', default='A2/图像清洗', help='输入图像目录')
    parser.add_argument('--output', '-o', default='stitched_result.jpg', help='输出文件路径')
    parser.add_argument('--cols', '-c', type=int, default=3, help='列数')
    args = parser.parse_args()

    stitch_images(args.input, args.output, args.cols)
```

### 七、数据集划分

**训练集、验证集、测试集划分脚本（split\_dataset.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据集划分程序
功能：将YOLO格式数据集按比例划分为训练集、验证集、测试集
比例：训练集70% / 验证集20% / 测试集10%
"""

# -------------------- 第一部分：导入依赖库 --------------------
import os                               # 操作系统库，文件和目录操作
import shutil                           # 文件操作库，复制文件
import random                           # 随机数库，打乱数据顺序

# -------------------- 第二部分：定义数据集划分类 --------------------
class DatasetSplitter:
    """数据集划分器类：将图像和标注文件按比例划分"""
    
    def __init__(self, source_dir, output_dir, 
                 train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
        """
        构造函数：设置数据集路径和划分比例
        参数:
            source_dir - 原始数据集目录（包含images和labels子目录）
            output_dir - 划分后数据集保存目录
            train_ratio - 训练集比例，默认0.7（70%）
            val_ratio - 验证集比例，默认0.2（20%）
            test_ratio - 测试集比例，默认0.1（10%）
        """
        self.source_dir = source_dir                      # 原始数据集路径
        self.output_dir = output_dir                    # 输出数据集路径
        self.train_ratio = train_ratio                  # 训练集比例
        self.val_ratio = val_ratio                     # 验证集比例
        self.test_ratio = test_ratio                    # 测试集比例

    def split(self):
        """
        执行数据集划分（核心方法）
        
        划分逻辑：
        1. 列出所有图像文件
        2. 打乱顺序（随机）
        3. 按比例切割为训练/验证/测试集
        4. 复制图像和标注文件到对应目录
        """
        # -------------------- 第一步：定义路径 --------------------
        images_dir = os.path.join(self.source_dir, "images")  # 原始图像目录
        labels_dir = os.path.join(self.source_dir, "labels")  # 原始标注目录

        # -------------------- 第二步：获取图像文件列表 --------------------
        # os.listdir(): 列出目录下所有文件
        # sorted(): 按文件名排序，保证顺序一致
        # endswith(): 筛选jpg和png格式
        image_files = sorted([f for f in os.listdir(images_dir) 
                             if f.endswith(('.jpg', '.png'))])

        # -------------------- 第三步：打乱数据顺序 --------------------
        # random.seed(42): 设置随机种子，保证结果可复现
        # 42是经典随机种子，任何人用都会得到相同的划分结果
        random.seed(42)
        
        # random.shuffle(): 就地打乱列表顺序
        # 这是为了保证数据随机分配到各个集合
        random.shuffle(image_files)

        # -------------------- 第四步：计算划分边界 --------------------
        total = len(image_files)                        # 总图像数量
        print(f"总图像数量: {total}")
        
        # 计算各集合的边界索引
        # int(): 取整数部分（向下取整）
        train_end = int(total * self.train_ratio)        # 训练集结束索引
        val_end = train_end + int(total * self.val_ratio)  # 验证集结束索引
        
        # 切片示例（假设total=100）：
        # train: [0:70] -> 70张
        # val: [70:90] -> 20张
        # test: [90:100] -> 10张

        # -------------------- 第五步：划分数据集 --------------------
        # 使用切片将图像列表划分为三部分
        splits = {
            'train': image_files[:train_end],           # 训练集切片
            'val': image_files[train_end:val_end],      # 验证集切片
            'test': image_files[val_end:]               # 测试集切片
        }

        # -------------------- 第六步：复制文件到对应目录 --------------------
        for split_name, files in splits.items():        # 遍历每个集合
            # 创建子目录：output_dir/train/images, output_dir/train/labels 等
            split_img_dir = os.path.join(self.output_dir, split_name, "images")
            split_lbl_dir = os.path.join(self.output_dir, split_name, "labels")
            
            # os.makedirs(..., exist_ok=True): 创建目录，如果存在也不报错
            os.makedirs(split_img_dir, exist_ok=True)
            os.makedirs(split_lbl_dir, exist_ok=True)

            # 遍历该集合中的每个图像文件
            for img_file in files:
                # -------------------- 复制图像文件 --------------------
                # 源图像路径
                src_img = os.path.join(images_dir, img_file)
                # 目标图像路径
                dst_img = os.path.join(split_img_dir, img_file)
                # shutil.copy2(): 复制文件并保留元数据（创建时间等）
                shutil.copy2(src_img, dst_img)

                # -------------------- 复制标注文件 --------------------
                # YOLO标注文件是.txt格式，文件名与图像文件对应
                # 将 .jpg 或 .png 替换为 .txt
                lbl_file = img_file.replace('.jpg', '.txt').replace('.png', '.txt')
                # 源标注文件路径
                src_lbl = os.path.join(labels_dir, lbl_file)
                
                # 检查标注文件是否存在（YOLO格式中图像和标注必须一一对应）
                if os.path.exists(src_lbl):
                    # 目标标注文件路径
                    dst_lbl = os.path.join(split_lbl_dir, lbl_file)
                    shutil.copy2(src_lbl, dst_lbl)

            # 打印该集合的统计信息
            print(f"{split_name}: {len(files)} images")

# -------------------- 第三部分：主程序入口 --------------------
if __name__ == '__main__':
    # 创建数据集划分器实例
    # 源目录: A3/YOLO格式（包含images和labels子目录）
    # 输出目录: A3/数据集划分（会自动创建train/val/test子目录）
    splitter = DatasetSplitter("A3/YOLO格式", "A3/数据集划分")
    
    # 执行划分
    splitter.split()
```

**数据集划分结果示例：**

```
总图像数量: 400
train: 280 images   (70%)
val: 80 images      (20%)
test: 40 images     (10%)
```

**输出目录结构：**

```
A3/数据集划分/
├── train/
│   ├── images/      # 280张训练图像
│   └── labels/      # 280个训练标注
├── val/
│   ├── images/      # 80张验证图像
│   └── labels/      # 80个验证标注
└── test/
    ├── images/      # 40张测试图像
    └── labels/      # 40个测试标注
```

### 八、YOLO模型训练

**YOLO训练配置文件（data.yaml）：**

```yaml
path: A3/数据集划分
train: train/images
val: val/images
test: test/images

nc: 8
names: ['person', 'turn_left', 'turn_right', 'limit_20', 'limit_100', 'red_light', 'yellow_light', 'green_light']
```

**YOLO训练命令：**

```bash
yolo detect train data=data.yaml model=yolov8n.pt epochs=100 imgsz=640
```

### 九、模型部署与应用

**ROS节点发布检测结果示例：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String

def main():
    rospy.init_node('yolo_detector')
    pub = rospy.Publisher('/detections', String, queue_size=10)
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        pub.publish("Detection result")
        rate.sleep()

if __name__ == '__main__':
    main()
```

### 十、思考与扩展

**思考题：**

1. 如何优化数据集标注质量？
2. 如何提升YOLO模型在小目标检测上的性能？

**Python程序示例（dataset\_split.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import random

class DatasetSplitter:
    def __init__(self, source_dir, output_dir, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio

    def split_dataset(self, image_dir, label_dir=None):
        """划分数据集（7:2:1）"""
        # 创建输出目录
        for split in ['train', 'val', 'test']:
            os.makedirs(os.path.join(self.output_dir, split, "images"), exist_ok=True)
            os.makedirs(os.path.join(self.output_dir, split, "labels"), exist_ok=True)

        # 获取所有图像文件
        images = [f for f in os.listdir(image_dir)
                  if f.endswith(('.jpg', '.png'))]
        random.shuffle(images)

        # 计算划分数量
        total = len(images)
        train_count = int(total * self.train_ratio)
        val_count = int(total * self.val_ratio)

        # 划分
        train_images = images[:train_count]
        val_images = images[train_count:train_count + val_count]
        test_images = images[train_count + val_count:]

        # 复制文件
        self.copy_files(train_images, image_dir, label_dir, "train")
        self.copy_files(val_images, image_dir, label_dir, "val")
        self.copy_files(test_images, image_dir, label_dir, "test")

        # 生成划分统计
        stats = {
            "train": len(train_images),
            "val": len(val_images),
            "test": len(test_images),
            "total": total,
            "ratio": f"{self.train_ratio}:{self.val_ratio}:{self.test_ratio}"
        }

        print(f"\n数据集划分完成:")
        print(f"  训练集: {stats['train']}张 ({self.train_ratio*100:.0f}%)")
        print(f"  验证集: {stats['val']}张 ({self.val_ratio*100:.0f}%)")
        print(f"  测试集: {stats['test']}张 ({self.test_ratio*100:.0f}%)")
        print(f"  总计: {stats['total']}张")

        # 保存划分信息
        with open(os.path.join(self.output_dir, "split_info.txt"), 'w') as f:
            for split, img_list in [("train", train_images),
                                    ("val", val_images),
                                    ("test", test_images)]:
                f.write(f"\n{split.upper()}:\n")
                for img in img_list:
                    f.write(f"  {img}\n")

        return stats

    def copy_files(self, images, image_dir, label_dir, split):
        """复制文件到对应目录"""
        for img in images:
            src_img = os.path.join(image_dir, img)
            dst_img = os.path.join(self.output_dir, split, "images", img)
            shutil.copy2(src_img, dst_img)

            # 如果有标签文件，也复制
            if label_dir:
                label_ext = '.txt'  # YOLO格式
                label_name = img.replace('.jpg', label_ext).replace('.png', label_ext)
                src_label = os.path.join(label_dir, label_name)
                dst_label = os.path.join(self.output_dir, split, "labels", label_name)
                if os.path.exists(src_label):
                    shutil.copy2(src_label, dst_label)

if __name__ == '__main__':
    splitter = DatasetSplitter("A3/图像数据标注", "A3/图像数据集划分")
    splitter.split_dataset("A3/图像数据标注")
```

### 八、操作步骤汇总

| 步骤 | 操作             | 说明                   |
| -- | -------------- | -------------------- |
| 1  | 启动Label-Studio | label-studio start   |
| 2  | 创建项目并配置类别      | 按表4顺序添加8个类别          |
| 3  | 导入清洗后的图像       | 从A2/图像清洗导入           |
| 4  | 开始标注           | 为每张图绘制边界框+标签         |
| 5  | 导出标注结果         | 导出为JSON格式            |
| 6  | 转换VOC格式        | 运行voc\_converter.py  |
| 7  | 转换COCO格式       | 运行coco\_converter.py |
| 8  | 转换YOLO格式       | 运行yolo\_converter.py |
| 9  | 生成拼接图          | 运行image\_stitch.py   |
| 10 | 划分数据集          | 运行dataset\_split.py  |

### 九、评判要点

1. **标注展示**：在Label-Studio中展示8类目标的标注画面
2. **类别标签文件**：class.txt包含8个类别（按顺序）
3. **拼接效果图**：10×10网格，每张图显示标注框和类别名
4. **数据集划分**：训练集70%，验证集20%，测试集10%

***

## 任务A4：文本数据集标注

### 一、任务目标

1. 使用Label-Studio对文本数据进行语义标注
2. 标注数量≥200条
3. 类别：咨询（0）、投诉（1）、报修（2）
4. 数据集划分（训练集:验证集:测试集 = 8:1:1）

### 二、标注类别

| 类别序号 | 类别名称 | 说明      |
| ---- | ---- | ------- |
| 0    | 咨询   | 询问信息类文本 |
| 1    | 投诉   | 投诉反馈类文本 |
| 2    | 报修   | 维修申请类文本 |

### 三、Label-Studio文本标注配置

**步骤：**

1. 创建新项目：`文本语义分类`
2. 选择模板：`Text Classification`
3. 添加标注标签：
   - 咨询
   - 投诉
   - 报修
4. 导入文本数据

### 四、文本数据划分程序

**Python程序示例（text\_dataset\_split.py）：**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import random

class TextDatasetSplitter:
    def __init__(self, source_file, output_dir,
                 train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
        self.source_file = source_file
        self.output_dir = output_dir
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio

        os.makedirs(output_dir, exist_ok=True)

    def load_data(self):
        """加载标注数据"""
        with open(self.source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    def split_dataset(self):
        """划分数据集（8:1:1）"""
        data = self.load_data()

        # 打乱数据
        random.shuffle(data)

        # 计算划分数量
        total = len(data)
        train_count = int(total * self.train_ratio)
        val_count = int(total * self.val_ratio)

        # 划分
        train_data = data[:train_count]
        val_data = data[train_count:train_count + val_count]
        test_data = data[train_count + val_count:]

        # 保存各数据集
        self.save_json(train_data, "train.json")
        self.save_json(val_data, "val.json")
        self.save_json(test_data, "test.json")

        # 生成统计
        self.generate_statistics(train_data, val_data, test_data)

        print(f"\n数据集划分完成:")
        print(f"  训练集: {len(train_data)}条 ({self.train_ratio*100:.0f}%)")
        print(f"  验证集: {len(val_data)}条 ({self.val_ratio*100:.0f}%)")
        print(f"  测试集: {len(test_data)}条 ({self.test_ratio*100:.0f}%)")
        print(f"  总计: {total}条")

    def save_json(self, data, filename):
        """保存JSON文件"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def generate_statistics(self, train_data, val_data, test_data):
        """生成划分统计信息"""
        categories = ["咨询", "投诉", "报修"]

        def count_by_category(data):
            counts = {cat: 0 for cat in categories}
            for item in data:
                label = item.get('label', '')
                if label in counts:
                    counts[label] += 1
            return counts

        train_stats = count_by_category(train_data)
        val_stats = count_by_category(val_data)
        test_stats = count_by_category(test_data)

        stats_file = os.path.join(self.output_dir, "split_statistics.txt")
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("数据集划分统计\n")
            f.write("=" * 50 + "\n\n")

            f.write("训练集分布:\n")
            for cat, count in train_stats.items():
                f.write(f"  {cat}: {count}\n")

            f.write("\n验证集分布:\n")
            for cat, count in val_stats.items():
                f.write(f"  {cat}: {count}\n")

            f.write("\n测试集分布:\n")
            for cat, count in test_stats.items():
                f.write(f"  {cat}: {count}\n")

        print(f"统计信息已保存至: {stats_file}")

if __name__ == '__main__':
    splitter = TextDatasetSplitter(
        "A4/文本数据标注/labeled_text.json",
        "A4/文本数据集划分"
    )
    splitter.split_dataset()
```

### 五、操作步骤汇总

| 步骤 | 操作             | 说明                        |
| -- | -------------- | ------------------------- |
| 1  | 启动Label-Studio | label-studio start        |
| 2  | 创建文本分类项目       | 添加咨询/投诉/报修三类              |
| 3  | 导入文本素材         | 从素材库导入                    |
| 4  | 进行语义标注         | 为每条文本选择类别                 |
| 5  | 导出标注结果         | 保存为JSON格式                 |
| 6  | 划分数据集          | 运行text\_dataset\_split.py |

### 六、评判要点

1. **标注展示**：在Label-Studio中展示咨询、投诉、报修三类标注
2. **标注数量**：≥200条
3. **数据集划分**：训练集80%，验证集10%，测试集10%

***

## 模块A文件存储汇总

### 结果文件夹结构

```
AI0102/                    # 结果存储文件夹（AI+场次号+赛位号）
├── A1/                    # 任务A1
│   ├── keyboard_control.py
│   ├── camera_viewer.py
│   ├── light_control.py
│   └── platform_test.launch
│
├── A2/                    # 任务A2
│   ├── 图像清洗/          # 清洗后的图像
│   ├── rename.py          # 重命名程序
│   ├── visualization.py   # 柱状图程序
│   └── category_distribution.png  # 分类统计柱状图
│
├── A3/                    # 任务A3
│   ├── 图像数据标注/       # 标注后的图像
│   ├── class.txt          # 类别标签文件
│   ├── 拼接效果图/         # 10×10拼接图
│   ├── image_stitch.py    # 拼接程序
│   └── 图像数据集划分/    # train/val/test
│       ├── train/
│       ├── val/
│       ├── test/
│       └── dataset_split.py
│
└── A4/                    # 任务A4
    ├── 文本数据标注/       # 标注后的文本
    └── 文本数据集划分/    # train/val/test
        ├── train.json
        ├── val.json
        ├── test.json
        └── text_dataset_split.py
```

***

## 常见问题与解决方案

### A1 常见问题

| 问题        | 解决方案                 |
| --------- | -------------------- |
| 摄像头无法打开   | 检查USB连接，确认摄像头驱动已安装   |
| 键盘输入无响应   | 检查终端焦点，确保在运行窗口内输入    |
| ROS节点通信失败 | 检查roscore是否运行，检查网络配置 |

### A2 常见问题

| 问题        | 解决方案            |
| --------- | --------------- |
| 图像数量不足400 | 从多个素材源补充采集      |
| 重命名后序号不连续 | 检查是否有文件被删除或命名冲突 |
| 柱状图中文显示乱码 | 安装中文字体或使用英文标签   |

### A3 常见问题

| 问题                 | 解决方案           |
| ------------------ | -------------- |
| Label-Studio导出格式错误 | 确认导出为完整的JSON格式 |
| 标注框位置偏移            | 检查图像尺寸元数据是否正确  |
| 拼接图内存不足            | 分批处理或降低图像分辨率   |

### A4 常见问题

| 问题       | 解决方案            |
| -------- | --------------- |
| 文本标注数量不足 | 增加素材或复用部分数据进行增强 |
| 类别分布不均   | 可接受一定程度的类别不平衡   |

