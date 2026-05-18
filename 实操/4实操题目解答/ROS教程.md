# ROS机器人操作系统教程

## 一、ROS简介

ROS（Robot Operating System，机器人操作系统）是一个开源的机器人软件框架，提供硬件抽象、底层设备控制、进程间通信等功能，广泛应用于机器人、自动驾驶等领域。

---

## 二、核心概念

### 2.1 节点（Node）

- **定义**：ROS中独立的可执行程序
- **特点**：模块化、单一功能
- **示例**：键盘控制节点、摄像头节点、灯光控制节点

### 2.2 话题（Topic）

- **定义**：节点间异步通信的通道
- **特点**：发布/订阅模式，发布者和订阅者不需要直接连接
- **示例**：
  - `/cmd_vel` - 运动命令话题
  - `/camera/image_raw` - 摄像头图像话题

### 2.3 消息（Message）

- **定义**：话题中传输的数据结构
- **格式**：字段（字段名+类型）

```python
# 示例：String消息
std_msgs.msg import String
msg = String()
msg.data = "forward"
```

### 2.4 服务（Service）

- **定义**：同步请求/响应通信模式
- **特点**：一问一答，类似于函数调用

---

## 三、基本命令

### 3.1 ROS命令

| 命令 | 功能 |
|------|------|
| `roscore` | 启动ROS主节点 |
| `rosrun <pkg> <node>` | 运行指定包中的节点 |
| `roslaunch <pkg> <file.launch>` | 启动launch文件 |
| `rosnode list` | 列出所有运行中的节点 |
| `rostopic list` | 列出所有话题 |
| `rostopic echo <topic>` | 显示话题消息内容 |
| `rospack find <pkg>` | 查找包路径 |

### 3.2 示例

```bash
# 启动ROS主节点
roscore

# 运行节点
rosrun ai_platform keyboard_control.py

# 启动launch文件
roslaunch ai_platform platform_test.launch

# 查看话题列表
rostopic list

# 查看某个话题的消息
rostopic echo /cmd_vel
```

---

## 四、Launch文件详解

### 4.1 基本结构

```xml
<launch>
    <!-- 启动节点 -->
    <node name="节点名" pkg="包名" type="可执行文件" output="screen"/>

    <!-- 设置参数 -->
    <param name="参数名" value="参数值"/>

    <!-- 定义变量 -->
    <arg name="变量名" default="默认值"/>
</launch>
```

### 4.2 常用标签

#### node标签

```xml
<!-- 基本用法 -->
<node name="my_node" pkg="my_package" type="my_script.py" output="screen"/>

<!-- 带参数启动 -->
<node name="my_node" pkg="my_package" type="my_script.py" args="arg1 arg2"/>
```

| 属性 | 说明 |
|------|------|
| name | 节点名称 |
| pkg | 包名 |
| type | 可执行文件名 |
| output | 输出方式（screen/log） |
| args | 传递给节点的参数 |

#### param标签

```xml
<!-- 设置参数 -->
<param name="speed" value="0.5"/>
<param name="debug" value="true"/>
```

#### arg标签

```xml
<!-- 定义变量 -->
<arg name="config_file" default="default.yaml"/>

<!-- 使用变量 -->
<param name="config" value="$(arg config_file)"/>
```

#### include标签

```xml
<!-- 包含其他launch文件 -->
<include file="$(find other_package)/launch/other.launch"/>
```

---

## 五、Python编程示例

### 5.1 发布者（Publisher）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String

class PublisherNode:
    def __init__(self):
        # 创建发布者
        self.pub = rospy.Publisher('/cmd_vel', String, queue_size=10)
        rospy.init_node('publisher_node', anonymous=True)
        self.rate = rospy.Rate(10)  # 10Hz

    def publish_message(self, message):
        """发布消息"""
        msg = String()
        msg.data = message
        self.pub.publish(msg)
        rospy.loginfo(f"发布: {message}")

    def run(self):
        while not rospy.is_shutdown():
            self.publish_message("forward")
            self.rate.sleep()

if __name__ == '__main__':
    try:
        node = PublisherNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
```

### 5.2 订阅者（Subscriber）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String

def callback(data):
    """回调函数处理接收到的消息"""
    rospy.loginfo(f"收到: {data.data}")

def subscriber_node():
    """订阅者节点"""
    rospy.init_node('subscriber_node', anonymous=True)

    # 创建订阅者
    rospy.Subscriber('/cmd_vel', String, callback)

    # 保持节点运行
    rospy.spin()

if __name__ == '__main__':
    subscriber_node()
```

### 5.3 服务服务端（Service Server）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from std_srv.srv import Trigger, TriggerResponse

def handle_request(req):
    """处理服务请求"""
    rospy.loginfo("收到服务请求")
    return TriggerResponse(success=True, message="处理完成")

def service_server():
    """服务服务端"""
    rospy.init_node('service_server')
    s = rospy.Service('/my_service', Trigger, handle_request)
    rospy.loginfo("服务已启动: /my_service")
    rospy.spin()

if __name__ == '__main__':
    service_server()
```

### 5.4 服务客户端（Service Client）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from std_srv.srv import Trigger

def service_client():
    """服务客户端"""
    rospy.init_node('service_client')
    rospy.wait_for_service('/my_service')

    try:
        proxy = rospy.ServiceProxy('/my_service', Trigger)
        response = proxy()
        rospy.loginfo(f"响应: {response.message}")
    except rospy.ServiceException as e:
        rospy.logerr(f"服务调用失败: {e}")

if __name__ == '__main__':
    service_client()
```

### 5.5 Python类与self详解

#### 类（Class）的基本概念

```python
class KeyboardControl:  # 定义一个类（类似制造机器人的图纸）
    def __init__(self):  # 构造函数，创建对象时自动调用
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', String, queue_size=10)
        self.rate = rospy.Rate(10)
        self.current_cmd = "stop"
        self.running = True
```

#### self是什么？

`self` 是**类的实例对象本身**，类似于其他语言中的 `this`。

| 写法 | 含义 |
|------|------|
| `self.cmd_vel_pub` | 这个对象的"发布者"属性 |
| `self.current_cmd` | 这个对象的"当前命令"属性 |
| `self.running` | 这个对象的"运行状态"属性 |

#### self与属性的关系

```python
class Robot:
    def __init__(self):
        self.speed = 10        # 实例属性：通过self.属性名定义
        self.name = "robot"    # 每个对象独立拥有

    def set_speed(self, new_speed):
        self.speed = new_speed  # 通过self访问或修改属性

# 创建对象
robot1 = Robot()   # robot1是实例
robot2 = Robot()   # robot2是另一个实例

robot1.speed = 20  # 修改robot1的speed，不影响robot2
```

#### 使用self的方法

```python
class KeyboardControl:
    def __init__(self):
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', String, queue_size=10)

    def publish_cmd(self, direction):  # 方法：类里面的函数
        cmd = String()
        cmd_map = {'w': "forward", 's': "backward", 'a': "left", 'd': "right", 'q': "stop"}
        cmd.data = cmd_map.get(direction, "stop")
        self.current_cmd = cmd.data        # 使用self访问属性
        self.cmd_vel_pub.publish(cmd)      # 使用self访问发布者

# 调用方法
controller = KeyboardControl()  # 创建实例
controller.publish_cmd('w')      # 通过实例调用方法
```

#### 局部变量 vs 实例属性

```python
class Example:
    def __init__(self):
        self.value = 100  # self.value 是实例属性，可跨方法使用

    def process(self):
        temp = 50        # temp 是局部变量，只在process()内有效
        result = temp + self.value  # 可以混合使用
        return result

obj = Example()
print(obj.value)   # 可以访问：100
print(obj.process())  # 调用方法：150
# print(temp)       # 错误！temp是局部变量，无法访问
```

---

## 六、竞赛平台应用

### 6.1 运动控制

```python
import rospy
from std_msgs.msg import String

class MotionControl:
    def __init__(self):
        self.cmd_pub = rospy.Publisher('/cmd_vel', String, queue_size=10)

    def move_forward(self):
        self.cmd_pub.publish("forward")

    def move_backward(self):
        self.cmd_pub.publish("backward")

    def turn_left(self):
        self.cmd_pub.publish("left")

    def turn_right(self):
        self.cmd_pub.publish("right")

    def stop(self):
        self.cmd_pub.publish("stop")
```

### 6.2 灯光控制

```python
import rospy
from std_msgs.msg import String

class LightControl:
    def __init__(self):
        self.light_pub = rospy.Publisher('/light_control', String, queue_size=10)

    def left_turn_signal(self):
        """左转向灯闪烁"""
        self.light_pub.publish("left_turn")

    def right_turn_signal(self):
        """右转向灯闪烁"""
        self.light_pub.publish("right_turn")

    def red_light(self):
        """红灯"""
        self.light_pub.publish("red_on")

    def green_light(self):
        """绿灯"""
        self.light_pub.publish("green_on")

    def all_off(self):
        """关闭所有灯"""
        self.light_pub.publish("all_off")
```

### 6.3 摄像头获取

```python
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraSubscriber:
    def __init__(self):
        self.bridge = CvBridge()
        rospy.Subscriber('/camera_head/image_raw', Image, self.callback)

    def callback(self, data):
        """处理图像消息"""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            cv2.imshow("Camera", cv_image)
            cv2.waitKey(1)
        except Exception as e:
            rospy.logerr(e)

### 6.4 Twist消息与运动控制

#### Twist消息类型

`geometry_msgs/Twist` 是ROS中描述机器人线速度和角速度的标准消息类型：

```python
from geometry_msgs.msg import Twist

twist = Twist()
twist.linear.x = 0.5   # 线速度 (m/s) - 前进方向
twist.linear.y = 0.0
twist.linear.z = 0.0
twist.angular.x = 0.0
twist.angular.y = 0.0
twist.angular.z = 0.3   # 角速度 (rad/s) - 左转
```

#### 坐标系理解

```
机器人视角（俯视）：
                    
        上（Y轴负方向）
           ↑
           |
           |
  ←-------●------→  右（X轴正方向）
           |
           |
           ↓
        下（Y轴正方向）
```

| 速度分量 | 方向 | 正值动作 |
|---------|------|---------|
| `linear.x` | 机器人正前方 | 前进 |
| `linear.y` | 机器人正左侧 | 左移 |
| `angular.z` | 绕垂直轴 | 左转（逆时针） |

#### 为什么有xyz三个参数？

Twist是**三维空间的速度消息**，需要描述6个自由度的运动状态：

```python
twist.linear.x = ...   # X轴线速度（前进/后退）
twist.linear.y = ...   # Y轴线速度（左/右平移）
twist.linear.z = ...   # Z轴线速度（上/下）
twist.angular.x = ...  # 绕X轴旋转（翻滚）
twist.angular.y = ...  # 绕Y轴旋转（俯仰）
twist.angular.z = ...  # 绕Z轴旋转（偏航/转向）
```

| 类型 | 分量 | 运动 | 适用场景 |
|------|------|------|---------|
| **linear** | x | 前进/后退 | 机器人前后移动 |
| **linear** | y | 左移/右移 | 机器人侧向移动 |
| **linear** | z | 上升/下降 | 无人机升降 |
| **angular** | x | 翻滚 | 滚筒运动 |
| **angular** | y | 俯仰 | 抬头/低头 |
| **angular** | z | 偏航 | 原地左/右转向 |

**为什么代码中其他分量设为0？** 因为竞赛平台是**地面移动机器人**，只能在二维平面运动，不需要垂直移动或翻滚俯仰。

| 机器人类型 | 使用的分量 |
|-----------|-----------|
| 地面移动机器人 | linear.x, angular.z |
| 麦克纳姆轮机器人 | linear.x, linear.y, angular.z |
| 无人机 | 所有6个分量都可能用到 |

#### 线速度与角速度配合

| 期望运动 | linear.x | angular.z | 效果 |
|---------|----------|-----------|------|
| 匀速前进 | 0.5 | 0.0 | 直线前进 |
| 定半径左转 | 0.5 | 0.3 | 左前方弧线 |
| 原地左转 | 0.0 | 0.5 | 原地左转 |
| 急刹停 | 0.0 | 0.0 | 停止 |

**核心原理**：
- `linear.x` 控制"往前走多快"
- `angular.z` 控制"转得多快"
- 两者独立可叠加：同时给值就走弧线

#### 运动学方程（差速机器人）

```
左轮速度 = linear.x - angular.z ×轮间距/2
右轮速度 = linear.x + angular.z ×轮间距/2
```

#### 键盘控制示例

```python
class KeyboardControl:
    def __init__(self):
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.speed = 0.5
        self.turn = 1.0
        
        # 移动绑定: 按键 -> (线速度系数, 角速度系数)
        self.moveBindings = {
            'w': (1, 0),    # 前进
            's': (-1, 0),   # 后退
            'a': (0, 1),    # 左转
            'd': (0, -1),   # 右转
        }
        
        # 速度调节绑定
        self.speedBindings = {
            'q': (1.1, 1.1),  # 加速
            'z': (0.9, 0.9),  # 减速
        }
    
    def publish_cmd(self, lin_vel, ang_vel):
        twist = Twist()
        twist.linear.x = lin_vel
        twist.angular.z = ang_vel
        self.cmd_vel_pub.publish(twist)

#### moveBindings 参数详解

元组中的参数是**方向系数**，需要与`speed`和`turn`相乘后才变成实际速度：

```python
self.moveBindings = {
    'w': (1, 0),    # (线速度系数, 角速度系数)
    's': (-1, 0),
    'a': (0, 1),
    'd': (0, -1),
}
```

| 按键 | 元组(线速度系数, 角速度系数) | 计算方式 | 最终效果 |
|------|---------------------------|---------|---------|
| W/w | (1, 0) | speed×1, turn×0 | `linear.x=0.5`, `angular.z=0` → 前进 |
| S/s | (-1, 0) | speed×-1, turn×0 | `linear.x=-0.5`, `angular.z=0` → 后退 |
| A/a | (0, 1) | speed×0, turn×1 | `linear.x=0`, `angular.z=1.0` → 左转 |
| D/d | (0, -1) | speed×0, turn×-1 | `linear.x=0`, `angular.z=-1.0` → 右转 |

#### 自定义组合示例

如果想让A键实现**前进左转**（弧线运动）：

```python
self.moveBindings = {
    'w': (1, 0),      # 前进（直线）
    's': (-1, 0),     # 后退（直线）
    'a': (1, 1),      # 前进+左转（弧线）← 修改这里
    'd': (1, -1),     # 前进+右转（弧线）
}
```

**计算过程**：按A键时 `linear.x = speed × 1 = 0.5`，`angular.z = turn × 1 = 1.0`

#### speedBindings 参数详解

| 按键 | 缩放因子 | 效果 |
|------|---------|------|
| Q/q | (1.1, 1.1) | 线速度和角速度同时×1.1（加速） |
| Z/z | (0.9, 0.9) | 线速度和角速度同时×0.9（减速） |

#### 常用控制方案对比

```python
# 方案1：标准差速
'w': (1, 0), 's': (-1, 0), 'a': (0, 1), 'd': (0, -1)

# 方案2：带弧线前进
'w': (1, 0), 's': (-1, 0), 'a': (1, 0.5), 'd': (1, -0.5)

# 方案3：漂移风格
'w': (1, 0), 's': (-1, 0), 'a': (0.5, 1), 'd': (0.5, -1)
```

---

## 七、Launch文件示例（竞赛平台）

### platform_test.launch

```xml
<launch>
    <!-- 键盘控制节点 -->
    <node name="keyboard_control"
          pkg="ai_platform"
          type="keyboard_control.py"
          output="screen"
          required="true"/>

    <!-- 摄像头查看节点 -->
    <node name="camera_viewer"
          pkg="ai_platform"
          type="camera_viewer.py"
          output="screen"/>

    <!-- 灯光控制节点 -->
    <node name="light_control"
          pkg="ai_platform"
          type="light_control.py"
          output="screen"/>
</launch>
```

### model_deploy.launch

```xml
<launch>
    <!-- 加载模型 -->
    <param name="model_path" value="$(find ai_platform)/models/yolov8n.pt"/>

    <!-- 目标检测节点 -->
    <node name="object_detection"
          pkg="ai_platform"
          type="detector.py"
          output="screen"/>

    <!-- 运动控制节点 -->
    <node name="motion_control"
          pkg="ai_platform"
          type="motion.py"
          output="screen"/>

    <!-- 灯光控制节点 -->
    <node name="light_control"
          pkg="ai_platform"
          type="light_control.py"
          output="screen"/>

    <!-- 语音播报节点 -->
    <node name="voice_control"
          pkg="ai_platform"
          type="voice.py"
          output="screen"/>
</launch>
```

---

## 八、调试技巧

### 8.1 查看节点状态

```bash
# 列出所有运行中的节点
rosnode list

# 查看节点信息
rosnode info /keyboard_control

# 查看节点间连接
rosnode ping /keyboard_control
```

### 8.2 查看话题数据

```bash
# 列出所有话题
rostopic list

# 查看话题消息类型
rostopic type /cmd_vel

# 实时显示话题消息
rostopic echo /cmd_vel

# 测量话题发布频率
rostopic hz /cmd_vel
```

### 8.3 rqt工具

```bash
# 打开可视化计算图
rqt_graph

# 打开参数服务器查看器
rqt_reconfigure

# 打开消息发布器（用于测试）
rqt_publisher
```

---

## 九、常见问题解决

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| `roscore` 无法启动 | 端口被占用 | 检查是否有其他roscore运行 |
| 节点通信失败 | 节点未注册 | 检查roscore状态和网络配置 |
| 话题无数据 | 话题名称不匹配 | 使用 `rostopic list` 确认话题名 |
| 权限错误 | 文件无执行权限 | `chmod +x script.py` |

---

## 十、学习资源

- ROS官方文档：https://docs.ros.org
- ROS Wiki：http://wiki.ros.org
- ROS机器人编程实战（书籍）
