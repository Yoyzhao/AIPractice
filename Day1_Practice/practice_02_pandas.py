import pandas as pd
import numpy as np

print("=" * 50)
print("练习2-1: 创建DataFrame")
print("=" * 50)

data = {
    'filename': [f'img_{i:04d}.jpg' for i in range(1, 11)],
    'width': np.random.randint(640, 1920, 10),
    'height': np.random.randint(480, 1080, 10),
    'category': np.random.choice(['car', 'pedestrian', 'traffic_sign'], 10),
}
df = pd.DataFrame(data)

print(f"DataFrame:\n{df}")
print(f"\nDataFrame形状: {df.shape}")
print(f"DataFrame列名: {df.columns.tolist()}")

print("\n" + "=" * 50)
print("练习2-2: 数据查看")
print("=" * 50)

print(f"前5行 df.head():\n{df.head()}")
print(f"\n后3行 df.tail(3):\n{df.tail(3)}")
print(f"\n数据类型 df.dtypes:\n{df.dtypes}")
print(f"\n统计描述 df.describe():\n{df.describe()}")

print("\n" + "=" * 50)
print("练习2-3: 数据选择")
print("=" * 50)

print(f"选择单列 df['filename']:\n{df['filename']}")
print(f"\n选择多列 df[['filename', 'category']]:\n{df[['filename', 'category']]}")
print(f"\n位置索引 df.iloc[0]:\n{df.iloc[0]}")
print(f"\n标签索引 df.loc[0, 'filename']: {df.loc[0, 'filename']}")

print("\n" + "=" * 50)
print("练习2-4: 数据筛选")
print("=" * 50)

print(f"筛选 width > 1000:\n{df[df['width'] > 1000]}")
print(f"\n筛选 category == 'car':\n{df[df['category'] == 'car']}")
print(f"\n多条件筛选:\n{df[(df['category'] == 'car') | (df['category'] == 'pedestrian')]}")

print("\n" + "=" * 50)
print("练习2-5: 数据统计")
print("=" * 50)

print(f"各类别数量:\n{df['category'].value_counts()}")
print(f"\n宽度均值: {df['width'].mean():.2f}")
print(f"宽度标准差: {df['width'].std():.2f}")
print(f"各类别宽度均值:\n{df.groupby('category')['width'].mean()}")

print("\n" + "=" * 50)
print("练习2-6: 数据修改")
print("=" * 50)

df['area'] = df['width'] * df['height']
print(f"添加新列 'area':\n{df[['filename', 'width', 'height', 'area']].head()}")

df = df.rename(columns={'filename': 'image_name'})
print(f"\n重命名列: {df.columns.tolist()}")

df = df.drop('area', axis=1)
print(f"\n删除列后列名: {df.columns.tolist()}")

print("\n" + "=" * 50)
print("练习2-7: CSV文件读写")
print("=" * 50)

df.to_csv('annotations.csv', index=False)
print("已保存到 annotations.csv")

df_loaded = pd.read_csv('annotations.csv')
print(f"重新读取:\n{df_loaded.head()}")

print("\n" + "=" * 50)
print("练习2-8: JSON文件读写")
print("=" * 50)

df.to_json('annotations.json', orient='records', force_ascii=False, indent=2)
print("已保存到 annotations.json")

df_json = pd.read_json('annotations.json')
print(f"重新读取:\n{df_json.head()}")

print("\n" + "=" * 50)
print("练习2-9: 创建100张图像信息")
print("=" * 50)

data = {
    'filename': [f'img_{i:04d}.jpg' for i in range(1, 101)],
    'width': np.random.randint(640, 1920, 100),
    'height': np.random.randint(480, 1080, 100),
    'category': np.random.choice(['car', 'pedestrian', 'traffic_sign'], 100),
}
df = pd.DataFrame(data)
print(f"创建了 {len(df)} 条记录")
print(f"各类别数量:\n{df['category'].value_counts()}")

print("\n" + "=" * 50)
print("练习2-10: 筛选车辆图像")
print("=" * 50)

cars = df[df['category'] == 'car']
print(f"车辆图像数量: {len(cars)}")

print("\n" + "=" * 50)
print("练习2-11: 统计每类数量")
print("=" * 50)

counts = df['category'].value_counts()
print(f"各类别统计:\n{counts}")

print("\n" + "=" * 50)
print("练习2-12: 导出CSV和JSON")
print("=" * 50)

df.to_csv('images.csv', index=False)
df.to_json('images.json')
print("已导出 images.csv 和 images.json")

print("\n" + "=" * 50)
print("练习2-13: 数据排序")
print("=" * 50)

df_sorted = df.sort_values('width', ascending=False)
print(f"按宽度降序排列:\n{df_sorted[['filename', 'width']].head()}")

print("\n" + "=" * 50)
print("练习2-14: 数据去重")
print("=" * 50)

df_with_dup = pd.concat([df, df.head()], ignore_index=True)
print(f"去重前记录数: {len(df_with_dup)}")
df_unique = df_with_dup.drop_duplicates()
print(f"去重后记录数: {len(df_unique)}")

print("\n" + "=" * 50)
print("练习2-15: 缺失值处理")
print("=" * 50)

df_with_na = df.copy()
df_with_na.loc[0, 'width'] = np.nan
print(f"包含缺失值:\n{df_with_na.isna().sum()}")
df_filled = df_with_na.fillna(df_with_na['width'].mean())
print(f"填充后:\n{df_filled.head()}")

print("\n" + "=" * 50)
print("练习2-16: apply自定义函数")
print("=" * 50)

df['aspect_ratio'] = df.apply(lambda x: x['width'] / x['height'], axis=1)
print(f"添加宽高比:\n{df[['filename', 'width', 'height', 'aspect_ratio']].head()}")

print("\n" + "=" * 50)
print("练习2-17: 数据合并")
print("=" * 50)

df1 = pd.DataFrame({'id': [1, 2, 3], 'name': ['A', 'B', 'C']})
df2 = pd.DataFrame({'id': [1, 2, 3], 'score': [90, 85, 92]})
df_merged = pd.merge(df1, df2, on='id')
print(f"合并后:\n{df_merged}")

print("\n" + "=" * 50)
print("练习2-18: 数据连接")
print("=" * 50)

df3 = pd.DataFrame({'id': [4, 5], 'name': ['D', 'E']})
df_concat = pd.concat([df1, df3], ignore_index=True)
print(f"连接后:\n{df_concat}")

print("\n" + "=" * 50)
print("练习2-19: 分组统计")
print("=" * 50)

grouped = df.groupby('category').agg({
    'width': ['mean', 'min', 'max'],
    'height': ['mean', 'min', 'max']
})
print(f"分组统计:\n{grouped}")

print("\n" + "=" * 50)
print("练习2-20: 交叉表")
print("=" * 50)

df['width_range'] = pd.cut(df['width'], bins=[0, 1000, 1500, 2000], labels=['small', 'medium', 'large'])
cross_tab = pd.crosstab(df['category'], df['width_range'])
print(f"交叉表:\n{cross_tab}")

print("\n" + "=" * 50)
print("Pandas练习完成! 共20个练习题目")
print("=" * 50)
