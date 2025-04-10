#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from PIL import Image
import numpy as np
# 导入字体配置工具
import font_config

# 配置中文字体
chinese_font = font_config.configure_chinese_font()

def merge_images(image_paths, subplot_titles, output_path=None):
    """
    合并2-4张图片为一张图，并为每个子图添加标题
    
    参数:
        image_paths: 图片路径列表
        subplot_titles: 子图标题列表
        output_path: 输出图片的保存路径，如果为None则显示而不保存
    
    返回:
        None
    """
    # 确保输入的图片数量在2-4之间
    num_images = len(image_paths)
    if num_images < 2 or num_images > 4:
        raise ValueError("只支持2-4张图片的合并")
    
    # 确保图片路径和子图标题数量一致
    if len(subplot_titles) != num_images:
        raise ValueError("子图标题数量必须与图片数量一致")
    
    # 根据图片数量确定子图布局
    if num_images == 2:
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        axes = axes.flatten()
    elif num_images == 3:
        fig = plt.figure(figsize=(12, 9))
        gs = gridspec.GridSpec(2, 2)
        axes = [plt.subplot(gs[0, 0]), plt.subplot(gs[0, 1]), plt.subplot(gs[1, :])]
    else:  # num_images == 4
        fig, axes = plt.subplots(2, 2, figsize=(12, 9))
        axes = axes.flatten()
    
    # 读取并显示每张图片
    for i, (img_path, title) in enumerate(zip(image_paths, subplot_titles)):
        # 读取图片
        img = Image.open(img_path)
        img_array = np.array(img)
        
        # 在对应的子图中显示图片
        axes[i].imshow(img_array)
        axes[i].set_title(title, fontsize=12)
        axes[i].axis('off')  # 隐藏坐标轴
    
    # 调整子图之间的间距
    plt.tight_layout()
    
    # 保存或显示图片
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"合并图片已保存至: {output_path}")
    else:
        plt.show()

def merge_images_from_folder(folder_path, image_names, subplot_titles, output_path=None):
    """
    从指定文件夹中选择图片进行合并
    
    参数:
        folder_path: 图片所在文件夹路径
        image_names: 要合并的图片文件名列表
        subplot_titles: 子图标题列表
        output_path: 输出图片的保存路径，如果为None则显示而不保存
    
    返回:
        None
    """
    # 构建完整的图片路径
    image_paths = [os.path.join(folder_path, img_name) for img_name in image_names]
    
    # 调用合并函数
    merge_images(image_paths, subplot_titles, output_path)

if __name__ == "__main__":
    # 示例用法
    """
    示例1: 直接指定图片路径合并
    image_paths = [
        "./代码图/图片1.png",
        "./代码图/图片2.png",
        "./代码图/图片3.png"
    ]
    subplot_titles = ["图片1标题", "图片2标题", "图片3标题"]
    merge_images(image_paths, subplot_titles, "合并结果.png")
    """
    
    """
    示例2: 从文件夹选择图片合并
    folder_path = "./代码图"
    image_names = ["图片1.png", "图片2.png", "图片3.png", "图片4.png"]
    subplot_titles = ["图片1标题", "图片2标题", "图片3标题", "图片4标题"]
    merge_images_from_folder(folder_path, image_names, subplot_titles, "合并结果.png")
    """
    
    print("图片合并工具")
    print("请修改脚本中的示例代码，指定要合并的图片，然后运行此脚本") 

    # 从文件夹选择图片合并
    folder_path = "./前端截图"
    image_names = ["食谱-详情.png", "食谱-编辑.png", "食谱-新增.png", "食谱-删除.png"]
    subplot_titles = ["详情", "编辑", "新增", "删除"]
    output_path = "./前端合并图/食谱（详情、编辑、新增、删除）.png"
    merge_images_from_folder(folder_path, image_names, subplot_titles, output_path)