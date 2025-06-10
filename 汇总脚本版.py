import math
import matplotlib.pyplot as plt
import numpy as np

def generate_data():
    # 输入参数
    B2 = float(input("请输入初始价位(B2): "))   # 初始价位
    H2 = float(input("请输入杠杆倍数(G2): "))        # 杠杆倍数
    I2 = float(input("请输入新入价-强平距(I2): "))  # 新入价-强平距
    J2 = int(input("请输入迭代次数(J2): "))     # 生成行数（改为int类型）

    # 初始化数据结构
    data_rows = [['序号','价位','筹码','均价','强平线','新入价-强平']]
    prev_strong = None  # 记录上一行的强平线值
    cumulative_sum = 0   # 累计求和

    for i in range(1, J2 + 1):
        # 计算当前行价格
        if i == 1:
            price = B2
        else:
            # 确保prev_strong有值
            if prev_strong is None:
                prev_strong = data_rows[-1][4]  # 从上一行获取强平线值
            price = math.ceil(prev_strong) + I2  # 上行强平线向上取整
        
        chips = 1  # 筹码固定为1
        cumulative_sum += price
        average = cumulative_sum / i  # 计算累加均价
        
        # 避免除零错误（杠杆倍数至少为1）
        lever = max(1.0, H2)
        strong = average * (1 - 1/lever)  # 强平线计算
        distance = price - strong  # 新价距离基本点
        
        # 更新为下轮准备的变量
        prev_strong = strong
        
        # 添加到结果列表
        row = [i, price, chips, average, strong, distance]
        data_rows.append(row)   
    return data_rows

def plot_chip_distribution(data):
    # 跳过表头行（第一行是标题，从第二行开始是数据）
    data_rows = data[1:]  
    
    # 提取价位和筹码数据
    positions = [row[1] for row in data_rows]
    frequencies = [row[2] for row in data_rows]
    
    # 创建图表
    plt.figure(figsize=(18, 6))
    
    # 绘制柱状图（直方图）
    # 设置宽度为1避免重叠
    plt.bar(range(len(positions)), frequencies, width=0.3, 
            color='skyblue', edgecolor='black', alpha=0.7,
            label='chip')
    
    # 绘制折线图（连接柱状图顶部）
    plt.plot(range(len(positions)), frequencies, 
             marker='o', markersize=8, color='red', linewidth=2,
             label='chip line')
    
    # 添加数据标签
    for i, freq in enumerate(frequencies):
        plt.text(i, freq + 0.3, str(freq), 
                 ha='center', va='bottom', fontsize=10)
    
    # 设置图表标题和标签
    plt.title('lever lab', fontsize=16, pad=20)
    plt.xlabel('price', fontsize=12)
    plt.ylabel('chip', fontsize=12)
    
    # 设置x轴刻度
    plt.xticks(range(len(positions)), 
               [f"{pos:.1f}" for pos in positions], 
               rotation=45)
    
    # 添加网格线和图例
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    
    # 调整布局
    plt.tight_layout()
    
    # 显示图表
    plt.show()
    print("图片已生成")

# 主程序
if __name__ == "__main__":
    # 生成数据
    result = generate_data()
    
    # 绘制图表
    plot_chip_distribution(result)
    
    # 打印数据
    print("\n详细数据:")
    for row in result:
        print(row)
