import numpy as np

print("=" * 50)
print("练习3-1: OpenCV基础操作")
print("=" * 50)

print("注意: OpenCV需要实际图像文件才能运行")
print("以下是概念演示，实际运行请确保有图像文件")

img = np.zeros((480, 640, 3), dtype=np.uint8)
print(f"创建空白图像: 形状 {img.shape}")

print("\n" + "=" * 50)
print("练习3-2: 颜色空间转换")
print("=" * 50)

img_bgr = np.zeros((100, 100, 3), dtype=np.uint8)
img_bgr[:, :] = [100, 150, 200]
print(f"BGR图像形状: {img_bgr.shape}")
print("灰度转换和RGB转换需要cv2库")

print("\n" + "=" * 50)
print("练习3-3: 模拟几何变换")
print("=" * 50)

test_img = np.zeros((200, 300, 3), dtype=np.uint8)
test_img[:, :] = [100, 150, 200]

resized_shape = (150, 100)
print(f"原始形状: {test_img.shape}")
print(f"缩放后形状(模拟): {resized_shape}")
print(f"旋转后形状(模拟): {test_img.shape[::-1]}")

print("\n" + "=" * 50)
print("练习3-4: 模拟绘制图形")
print("=" * 50)

canvas = np.zeros((400, 400, 3), dtype=np.uint8)
print(f"创建画布: 形状 {canvas.shape}")
print("矩形、圆形、文字绘制需要cv2库")
print("矩形: cv2.rectangle(canvas, (50,50), (150,150), (0,255,0), 2)")
print("圆形: cv2.circle(canvas, (250,100), 50, (0,0,255), 2)")

print("\n" + "=" * 50)
print("练习3-5: 模拟模糊和边缘检测")
print("=" * 50)

test_img = np.zeros((100, 100, 3), dtype=np.uint8)
test_img[40:60, 40:60] = [255, 255, 255]
print(f"测试图像形状: {test_img.shape}")
print("高斯模糊: cv2.GaussianBlur(img, (5,5), 0)")
print("边缘检测: cv2.Canny(img, 50, 150)")

print("\n" + "=" * 50)
print("练习3-6: ROI区域操作")
print("=" * 50)

test_img = np.zeros((240, 320, 3), dtype=np.uint8)
h, w = test_img.shape[:2]
roi_shape = (h//4, w//4, 3)
print(f"原始形状: {test_img.shape}")
print(f"ROI形状(模拟裁剪): {roi_shape}")

print("\n" + "=" * 50)
print("练习3-7: 摄像头采集检查")
print("=" * 50)

print("摄像头采集代码:")
print("cap = cv2.VideoCapture(0)")
print("ret, frame = cap.read()")
print("if ret:")
print("    cv2.imwrite('capture.jpg', frame)")
print("cap.release()")

print("\n" + "=" * 50)
print("练习3-8: 批量图像处理")
print("=" * 50)

print("创建10张模拟图像...")
for i in range(10):
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :] = [(i*25) % 256, (i*50) % 256, (i*75) % 256]
    print(f"生成: frame_{i:04d}.jpg")

print("\n" + "=" * 50)
print("练习3-9: 图像拼接")
print("=" * 50)

img1 = np.zeros((100, 100, 3), dtype=np.uint8)
img1[:, :] = [255, 0, 0]
img2 = np.zeros((100, 100, 3), dtype=np.uint8)
img2[:, :] = [0, 255, 0]

hstack = np.hstack([img1, img2])
vstack = np.vstack([img1, img2])
print(f"水平拼接后形状: {hstack.shape}")
print(f"垂直拼接后形状: {vstack.shape}")

print("\n" + "=" * 50)
print("练习3-10: 图像混合")
print("=" * 50)

img1 = np.ones((100, 100, 3), dtype=np.uint8) * 100
img2 = np.ones((100, 100, 3), dtype=np.uint8) * 200
print(f"图像1: 平均值 {img1.mean():.2f}")
print(f"图像2: 平均值 {img2.mean():.2f}")
print("图像混合需要cv2.addWeighted()")

print("\n" + "=" * 50)
print("练习3-11: 颜色统计")
print("=" * 50)

img = np.zeros((100, 100, 3), dtype=np.uint8)
img[:, :, 0] = 100
img[:, :, 1] = 150
img[:, :, 2] = 200

print(f"B通道均值: {img[:,:,0].mean():.2f}")
print(f"G通道均值: {img[:,:,1].mean():.2f}")
print(f"R通道均值: {img[:,:,2].mean():.2f}")

print("\n" + "=" * 50)
print("练习3-12: 形态学操作")
print("=" * 50)

kernel = np.ones((5, 5), np.uint8)
print(f"创建5x5卷积核")
print("膨胀: cv2.dilate(img, kernel, iterations=1)")
print("腐蚀: cv2.erode(img, kernel, iterations=1)")

print("\n" + "=" * 50)
print("练习3-13: 图像阈值处理")
print("=" * 50)

gray = np.array([[100, 150], [200, 50]], dtype=np.uint8)
print(f"灰度图像:\n{gray}")
print("阈值处理: cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)")

print("\n" + "=" * 50)
print("练习3-14: 轮廓检测")
print("=" * 50)

print("轮廓检测代码:")
print("gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)")
print("contours, hierarchy = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)")
print("cv2.drawContours(img, contours, -1, (0, 255, 0), 2)")

print("\n" + "=" * 50)
print("练习3-15: 透视变换")
print("=" * 50)

print("透视变换代码:")
print("pts1 = np.float32([[50,50], [200,50], [50,200], [200,200]])")
print("pts2 = np.float32([[0,0], [300,0], [0,300], [300,300]])")
print("M = cv2.getPerspectiveTransform(pts1, pts2)")
print("dst = cv2.warpPerspective(img, M, (300, 300))")

print("\n" + "=" * 50)
print("OpenCV练习完成! 共15个练习题目")
print("=" * 50)
print("提示: 实际运行OpenCV代码需要:")
print("1. 安装opencv-python: pip install opencv-python")
print("2. 准备图像文件")
print("3. 有GUI环境支持显示窗口")
