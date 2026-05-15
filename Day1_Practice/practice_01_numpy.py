import numpy as np

print("=" * 50)
print("练习1-1: 创建不同类型的数组")
print("=" * 50)

arr1 = np.array([1, 2, 3, 4, 5])
print(f"一维数组: {arr1}")

arr2 = np.array([[1, 2, 3], [4, 5, 6]])
print(f"二维数组:\n{arr2}")

zeros = np.zeros((3, 4))
ones = np.ones((2, 3))
random_arr = np.random.randn(3, 3)

print(f"全零数组 (3x4):\n{zeros}")
print(f"全一数组 (2x3):\n{ones}")
print(f"随机数组 (3x3):\n{random_arr}")

print("\n" + "=" * 50)
print("练习1-2: 数组基本操作")
print("=" * 50)

arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

print(f"数组形状: {arr.shape}")
print(f"数组维度: {arr.ndim}")
print(f"数组数据类型: {arr.dtype}")
print(f"数组元素总数: {arr.size}")

print("\n" + "=" * 50)
print("练习1-3: 数组索引与切片")
print("=" * 50)

print(f"访问元素 arr[0,0]: {arr[0, 0]}")
print(f"访问第一行: {arr[0, :]}")
print(f"访问第一列: {arr[:, 0]}")
print(f"访问子矩阵 [0:2, 1:3]:\n{arr[0:2, 1:3]}")

print("\n" + "=" * 50)
print("练习1-4: 数组运算")
print("=" * 50)

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

print(f"a + b = {a + b}")
print(f"a * b = {a * b}")
print(f"点积 np.dot(a, b) = {np.dot(a, b)}")
print(f"求和 a.sum() = {a.sum()}")
print(f"均值 a.mean() = {a.mean():.2f}")
print(f"最大值 a.max() = {a.max()}")
print(f"标准差 a.std() = {a.std():.2f}")

print("\n" + "=" * 50)
print("练习1-5: 形状变换")
print("=" * 50)

arr = np.array([[1, 2], [3, 4], [5, 6]])
print(f"原始形状 (3x2):\n{arr}")
print(f"reshape(2,3):\n{arr.reshape(2, 3)}")
print(f"flatten(): {arr.flatten()}")
print(f"转置:\n{arr.T}")

print("\n" + "=" * 50)
print("练习1-6: 矩阵运算")
print("=" * 50)

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

print(f"矩阵加法:\n{A + B}")
print(f"矩阵乘法 np.matmul(A, B):\n{np.matmul(A, B)}")
print(f"矩阵乘法 A @ B:\n{A @ B}")
print(f"矩阵的逆:\n{np.linalg.inv(A)}")

print("\n" + "=" * 50)
print("练习1-7: 布尔索引")
print("=" * 50)

arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print(f"原数组: {arr}")
print(f"arr > 5: {arr > 5}")
print(f"arr[arr > 5]: {arr[arr > 5]}")
print(f"arr[(arr > 3) & (arr < 8)]: {arr[(arr > 3) & (arr < 8)]}")

print("\n" + "=" * 50)
print("练习1-8: 广播机制")
print("=" * 50)

A = np.array([[1, 2, 3], [4, 5, 6]])
b = np.array([10, 20, 30])

print(f"A:\n{A}")
print(f"b: {b}")
print(f"A + b (广播):\n{A + b}")

print("\n" + "=" * 50)
print("练习1-9: 创建5x5单位矩阵")
print("=" * 50)

identity = np.eye(5)
print(f"5x5单位矩阵:\n{identity}")

print("\n" + "=" * 50)
print("练习1-10: 矩阵乘法实战")
print("=" * 50)

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
C = np.matmul(A, B)
print(f"A @ B =\n{C}")

print("\n" + "=" * 50)
print("练习1-11: 找最大值最小值")
print("=" * 50)

arr = np.array([3, 1, 4, 1, 5, 9, 2, 6])
max_val = arr.max()
min_val = arr.min()
max_idx = arr.argmax()
min_idx = arr.argmin()
print(f"原数组: {arr}")
print(f"Max: {max_val}, Min: {min_val}")
print(f"MaxIdx: {max_idx}, MinIdx: {min_idx}")

print("\n" + "=" * 50)
print("练习1-12: 随机数组与统计")
print("=" * 50)

arr = np.random.randn(100)
print(f"生成了100个随机数")
print(f"均值: {arr.mean():.4f}")
print(f"标准差: {arr.std():.4f}")
print(f"最大值: {arr.max():.4f}")
print(f"最小值: {arr.min():.4f}")

print("\n" + "=" * 50)
print("练习1-13: 数组拼接")
print("=" * 50)

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(f"a: {a}")
print(f"b: {b}")
print(f"np.concatenate([a, b]): {np.concatenate([a, b])}")
print(f"np.vstack([a, b]):\n{np.vstack([a, b])}")
print(f"np.hstack([a, b]): {np.hstack([a, b])}")

print("\n" + "=" * 50)
print("练习1-14: 数组排序")
print("=" * 50)

arr = np.array([5, 2, 8, 1, 9])
print(f"原数组: {arr}")
print(f"排序后: {np.sort(arr)}")
print(f"从小到大索引: {np.argsort(arr)}")

print("\n" + "=" * 50)
print("练习1-15: 唯一值与计数")
print("=" * 50)

arr = np.array([1, 2, 2, 3, 3, 3, 4, 4, 4, 4])
unique, counts = np.unique(arr, return_counts=True)
print(f"原数组: {arr}")
print(f"唯一值: {unique}")
print(f"计数: {counts}")

print("\n" + "=" * 50)
print("练习1-16: 条件筛选与替换")
print("=" * 50)

arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print(f"原数组: {arr}")
arr[arr > 5] = 0
print(f"arr[arr > 5] = 0 后的数组: {arr}")

print("\n" + "=" * 50)
print("练习1-17: 计算范数")
print("=" * 50)

v = np.array([3, 4])
print(f"向量: {v}")
print(f"L2范数: {np.linalg.norm(v)}")
print(f"L1范数: {np.abs(v).sum()}")

print("\n" + "=" * 50)
print("练习1-18: 生成等差数组")
print("=" * 50)

arr1 = np.linspace(0, 10, 5)
arr2 = np.arange(0, 10, 2)
print(f"linspace(0, 10, 5): {arr1}")
print(f"arange(0, 10, 2): {arr2}")

print("\n" + "=" * 50)
print("练习1-19: 对角矩阵")
print("=" * 50)

arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(f"矩阵:\n{arr}")
print(f"对角线: {np.diag(arr)}")
print(f"从对角线创建矩阵:\n{np.diag([1, 2, 3])}")

print("\n" + "=" * 50)
print("练习1-20: 特征值与特征向量")
print("=" * 50)

A = np.array([[1, 2], [2, 1]])
eigenvalues, eigenvectors = np.linalg.eig(A)
print(f"矩阵A:\n{A}")
print(f"特征值: {eigenvalues}")
print(f"特征向量:\n{eigenvectors}")

print("\n" + "=" * 50)
print("练习1-21: 批量操作")
print("=" * 50)

arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(f"矩阵:\n{arr}")
print(f"每列求和: {arr.sum(axis=0)}")
print(f"每行求和: {arr.sum(axis=1)}")
print(f"每列均值: {arr.mean(axis=0)}")

print("\n" + "=" * 50)
print("练习1-22: 复制与视图")
print("=" * 50)

arr1 = np.array([1, 2, 3, 4, 5])
arr2 = arr1.copy()
arr3 = arr1.view()

arr1[0] = 100
print(f"修改arr1[0]=100后:")
print(f"arr1: {arr1}")
print(f"arr2 (copy): {arr2}")
print(f"arr3 (view): {arr3}")

print("\n" + "=" * 50)
print("练习1-23: 改变数组类型")
print("=" * 50)

arr = np.array([1.5, 2.7, 3.9])
print(f"原始数组: {arr}, dtype: {arr.dtype}")
arr_int = arr.astype(int)
print(f"转换为int: {arr_int}, dtype: {arr_int.dtype}")

print("\n" + "=" * 50)
print("练习1-24: 条件统计")
print("=" * 50)

arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print(f"数组: {arr}")
print(f"大于5的元素数量: {np.sum(arr > 5)}")
print(f"大于5的元素占比: {np.mean(arr > 5):.2%}")

print("\n" + "=" * 50)
print("练习1-25: 创建复数数组")
print("=" * 50)

real = np.array([1, 2, 3])
imag = np.array([4, 5, 6])
complex_arr = real + 1j * imag
print(f"实部: {real}")
print(f"虚部: {imag}")
print(f"复数数组: {complex_arr}")
print(f"复数的模: {np.abs(complex_arr)}")
print(f"复数的角度: {np.angle(complex_arr)}")

print("\n" + "=" * 50)
print("练习1-26: 累加与累乘")
print("=" * 50)

arr = np.array([1, 2, 3, 4, 5])
print(f"数组: {arr}")
print(f"累加: {np.cumsum(arr)}")
print(f"累乘: {np.cumprod(arr)}")

print("\n" + "=" * 50)
print("练习1-27: 梯度计算")
print("=" * 50)

arr = np.array([1, 3, 6, 10, 15])
gradient = np.gradient(arr)
print(f"数组: {arr}")
print(f"梯度: {gradient}")

print("\n" + "=" * 50)
print("练习1-28: 创建网格坐标")
print("=" * 50)

x = np.linspace(0, 4, 5)
y = np.linspace(0, 3, 4)
X, Y = np.meshgrid(x, y)
print(f"X:\n{X}")
print(f"Y:\n{Y}")

print("\n" + "=" * 50)
print("练习1-29: 距离计算")
print("=" * 50)

p1 = np.array([0, 0])
p2 = np.array([3, 4])
distance = np.linalg.norm(p1 - p2)
print(f"点1: {p1}")
print(f"点2: {p2}")
print(f"欧氏距离: {distance}")

print("\n" + "=" * 50)
print("练习1-30: 随机种子与复现")
print("=" * 50)

np.random.seed(42)
arr1 = np.random.randn(5)
print(f"随机种子42: {arr1}")

np.random.seed(42)
arr2 = np.random.randn(5)
print(f"再次随机种子42: {arr2}")

print(f"两次结果相同: {np.array_equal(arr1, arr2)}")

print("\n" + "=" * 50)
print("NumPy练习完成! 共30个练习题目")
print("=" * 50)
