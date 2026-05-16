import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

print("=" * 50)
print("练习5-1: 张量创建与基本操作")
print("=" * 50)

t1 = torch.tensor([1, 2, 3, 4, 5])
print(f"从列表创建: {t1}")

zeros = torch.zeros(3, 4)
ones = torch.ones(2, 3)
randn = torch.randn(3, 3)
arange = torch.arange(0, 10, 2)

print(f"全零 (3x4):\n{zeros}")
print(f"全一 (2x3):\n{ones}")
print(f"随机正态 (3x3):\n{randn}")
print(f"范围: {arange}")

print("\n" + "=" * 50)
print("练习5-2: 张量属性")
print("=" * 50)

t = torch.randn(4, 5)
print(f"形状: {t.shape}")
print(f"维度: {t.ndim}")
print(f"数据类型: {t.dtype}")
print(f"设备: {t.device}")

print("\n" + "=" * 50)
print("练习5-3: NumPy与Tensor互转")
print("=" * 50)

np_arr = np.array([1, 2, 3, 4, 5])
t_from_np = torch.from_numpy(np_arr)
print(f"NumPy数组: {np_arr}")
print(f"转Tensor: {t_from_np}")

t_back = t_from_np.numpy()
print(f"转回NumPy: {t_back}")

print("\n" + "=" * 50)
print("练习5-4: 张量运算")
print("=" * 50)

a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([4.0, 5.0, 6.0])

print(f"a + b = {a + b}")
print(f"a * b = {a * b}")
print(f"点积: {torch.dot(a, b)}")

A = torch.randn(2, 3)
B = torch.randn(3, 2)
print(f"矩阵乘法 (2x3) @ (3x2):\n{A @ B}")

print("\n" + "=" * 50)
print("练习5-5: 索引与切片")
print("=" * 50)

t = torch.tensor([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(f"原始:\n{t}")
print(f"t[0, :]: {t[0, :]}")
print(f"t[:, 1]: {t[:, 1]}")
print(f"t[0:2, 0:2]:\n{t[0:2, 0:2]}")

print("\n" + "=" * 50)
print("练习5-6: 形状变换")
print("=" * 50)

t = torch.randn(3, 4)
print(f"原始形状: {t.shape}")
print(f"reshape(4, 3): {t.reshape(4, 3).shape}")
print(f"view(12): {t.view(12).shape}")
print(f"unsqueeze/squeeze: {t.unsqueeze(0).squeeze().shape}")

print("\n" + "=" * 50)
print("练习5-7: GPU支持检查")
print("=" * 50)

print(f"CUDA可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU数量: {torch.cuda.device_count()}")
    print(f"GPU名称: {torch.cuda.get_device_name(0)}")
else:
    print("无GPU，使用CPU")

print("\n" + "=" * 50)
print("练习5-8: 定义神经网络")
print("=" * 50)

class SimpleNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

model = SimpleNet(784, 256, 10)
print(model)

total_params = sum(p.numel() for p in model.parameters())
print(f"总参数量: {total_params:,}")

print("\n" + "=" * 50)
print("练习5-9: 定义CNN模型")
print("=" * 50)

class CNN(nn.Module):
    def __init__(self, num_classes=10):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 8 * 8, 256)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 8 * 8)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

cnn_model = CNN(num_classes=4)
print(cnn_model)

x = torch.randn(1, 3, 32, 32)
output = cnn_model(x)
print(f"输入形状: {x.shape}")
print(f"输出形状: {output.shape}")

print("\n" + "=" * 50)
print("练习5-10: 训练循环")
print("=" * 50)

X_train = torch.randn(1000, 20)
y_train = torch.randn(1000, 1)
dataset = TensorDataset(X_train, y_train)
train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

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
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

print("开始训练...")
for epoch in range(5):
    model.train()
    total_loss = 0

    for batch_x, batch_y in train_loader:
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / len(train_loader)
    print(f"Epoch {epoch+1}/5, Loss: {avg_loss:.4f}")

print("\n" + "=" * 50)
print("练习5-11: 模型保存与加载")
print("=" * 50)

torch.save(model.state_dict(), 'model.pth')
print("模型已保存到 model.pth")

model.load_state_dict(torch.load('model.pth'))
print("模型已加载")

print("\n" + "=" * 50)
print("练习5-12: 梯度计算与反向传播")
print("=" * 50)

x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
y = x ** 2
z = y.sum()

print(f"x: {x}")
print(f"y = x^2: {y}")
print(f"z = sum(y): {z}")

z.backward()
print(f"dz/dx: {x.grad}")

print("\n" + "=" * 50)
print("练习5-13: 使用训练好的模型预测")
print("=" * 50)

model.eval()
with torch.no_grad():
    x_test = torch.randn(1, 20)
    prediction = model(x_test)
    print(f"输入: {x_test.shape}")
    print(f"预测值: {prediction}")

print("\n" + "=" * 50)
print("练习5-14: 学习率调度")
print("=" * 50)

model = RegressionNet()
optimizer = optim.Adam(model.parameters(), lr=0.1)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

print("学习率调度:")
for epoch in range(5):
    scheduler.step()
    print(f"Epoch {epoch+1}: lr = {optimizer.param_groups[0]['lr']:.6f}")

print("\n" + "=" * 50)
print("练习5-15: Dropout与正则化")
print("=" * 50)

class NetWithDropout(nn.Module):
    def __init__(self):
        super(NetWithDropout, self).__init__()
        self.fc1 = nn.Linear(10, 20)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(20, 10)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

net = NetWithDropout()
print(net)

net.train()
x = torch.randn(5, 10)
output_train = net(x)
print(f"训练模式输出均值: {output_train.mean():.4f}")

net.eval()
output_eval = net(x)
print(f"评估模式输出均值: {output_eval.mean():.4f}")

print("\n" + "=" * 50)
print("练习5-16: 批归一化")
print("=" * 50)

class NetWithBN(nn.Module):
    def __init__(self):
        super(NetWithBN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)

    def forward(self, x):
        x = self.bn1(F.relu(self.conv1(x)))
        x = self.bn2(F.relu(self.conv2(x)))
        return x

net_bn = NetWithBN()
print(net_bn)

x = torch.randn(2, 3, 32, 32)
output = net_bn(x)
print(f"输入形状: {x.shape}")
print(f"输出形状: {output.shape}")

print("\n" + "=" * 50)
print("练习5-17: 迁移学习-冻结参数")
print("=" * 50)

model = CNN(num_classes=10)
print("冻结所有参数:")
for name, param in model.named_parameters():
    if 'conv1' in name or 'conv2' in name:
        param.requires_grad = False

trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
frozen = sum(p.numel() for p in model.parameters() if not p.requires_grad)
print(f"可训练参数: {trainable:,}")
print(f"冻结参数: {frozen:,}")

print("\n" + "=" * 50)
print("练习5-18: 自定义数据集")
print("=" * 50)

class CustomDataset(TensorDataset):
    def __init__(self, X, y, transform=None):
        super().__init__(X, y)
        self.transform = transform

    def __getitem__(self, index):
        x, y = super().__getitem__(index)
        if self.transform:
            x = self.transform(x)
        return x, y

X = torch.randn(100, 20)
y = torch.randint(0, 2, (100,))
dataset = CustomDataset(X, y)
loader = DataLoader(dataset, batch_size=10)

print(f"数据集大小: {len(dataset)}")
batch_x, batch_y = next(iter(loader))
print(f"批次形状: x={batch_x.shape}, y={batch_y.shape}")

print("\n" + "=" * 50)
print("练习5-19: 早停策略")
print("=" * 50)

best_loss = float('inf')
patience = 3
counter = 0

losses = [0.5, 0.4, 0.35, 0.36, 0.34, 0.33]
print("模拟训练损失:")
for epoch, loss in enumerate(losses, 1):
    if loss < best_loss:
        best_loss = loss
        counter = 0
    else:
        counter += 1

    print(f"Epoch {epoch}: loss={loss:.4f}, counter={counter}")

    if counter >= patience:
        print(f"早停! Epoch {epoch}")
        break

print("\n" + "=" * 50)
print("练习5-20: GPU数据传输")
print("=" * 50)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用设备: {device}")

model = SimpleNet(20, 50, 10)
model = model.to(device)
print(f"模型已移动到: {next(model.parameters()).device}")

x = torch.randn(5, 20).to(device)
output = model(x)
print(f"输入设备: {x.device}")
print(f"输出设备: {output.device}")

print("\n" + "=" * 50)
print("PyTorch练习完成! 共20个练习题目")
print("=" * 50)
