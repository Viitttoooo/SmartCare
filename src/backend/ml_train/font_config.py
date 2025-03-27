"""
中文字体配置工具

提供多种配置matplotlib显示中文的方法，可以根据不同的系统环境选择合适的方法
"""

import matplotlib.pyplot as plt
import matplotlib
import os
import sys
import platform
from matplotlib.font_manager import FontProperties

def method1_set_rcparams():
    """方法1: 设置matplotlib的rcParams参数"""
    print("使用方法1配置中文字体...")
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS'] + plt.rcParams['font.sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    return True

def method2_use_fontproperties():
    """方法2: 查找系统中的中文字体并返回FontProperties对象"""
    print("使用方法2配置中文字体...")
    
    # 查找系统中的中文字体
    fonts = [f.name for f in matplotlib.font_manager.fontManager.ttflist if '黑体' in f.name or 'SimHei' in f.name]
    if not fonts:
        fonts = [f.name for f in matplotlib.font_manager.fontManager.ttflist if '宋体' in f.name or 'SimSun' in f.name]
    if not fonts:
        fonts = [f.name for f in matplotlib.font_manager.fontManager.ttflist if '微软雅黑' in f.name or 'Microsoft YaHei' in f.name]
    
    if fonts:
        print(f"找到中文字体: {fonts[0]}")
        return FontProperties(fonts[0])
    else:
        print("未找到中文字体")
        return None

def method3_download_font():
    """方法3: 下载并使用开源中文字体"""
    print("使用方法3配置中文字体...")
    
    # 检查字体是否已存在
    font_path = './SimHei.ttf'
    if not os.path.exists(font_path):
        try:
            # 如果没有字体，可以从网络下载或者包含在项目中
            # 这里只是一个示例，实际下载代码需要根据实际情况调整
            print("需要下载中文字体，请确保网络连接...")
            import urllib.request
            # 下载开源中文字体文件
            url = 'https://github.com/StellarCN/scp_zh/raw/master/fonts/SimHei.ttf'
            urllib.request.urlretrieve(url, font_path)
            print(f"成功下载字体到 {font_path}")
        except Exception as e:
            print(f"下载字体失败: {e}")
            return False
    
    # 配置matplotlib使用这个字体
    from matplotlib.font_manager import FontProperties
    plt.rcParams['font.sans-serif'] = ['SimHei'] + plt.rcParams['font.sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 手动加载字体
    font_manager = matplotlib.font_manager.FontManager()
    font_manager.addfont(font_path)
    matplotlib.font_manager.fontManager = font_manager
    
    return True

def method4_use_ttc_font():
    """方法4: 尝试使用系统TTC字体"""
    print("使用方法4配置中文字体...")
    
    system = platform.system()
    if system == 'Windows':
        # Windows系统字体路径
        font_path = 'C:/Windows/Fonts/simhei.ttf'
        if not os.path.exists(font_path):
            font_path = 'C:/Windows/Fonts/msyh.ttc'  # 尝试微软雅黑
    elif system == 'Darwin':  # macOS
        # macOS系统字体路径
        font_path = '/System/Library/Fonts/PingFang.ttc'
    else:  # Linux
        # Linux系统字体路径
        font_path = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
        if not os.path.exists(font_path):
            # 尝试其他可能的位置
            candidates = [
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc'
            ]
            for path in candidates:
                if os.path.exists(path):
                    font_path = path
                    break
    
    if os.path.exists(font_path):
        print(f"使用系统字体: {font_path}")
        # 配置matplotlib使用这个字体
        font_properties = FontProperties(fname=font_path)
        plt.rcParams['font.sans-serif'] = [font_properties.get_name()] + plt.rcParams['font.sans-serif']
        return font_properties
    else:
        print(f"找不到系统字体")
        return None

def configure_chinese_font():
    """尝试多种方法配置中文字体，直到成功"""
    
    # 方法1: 设置rcParams
    method1_set_rcparams()
    
    # 方法2: 使用FontProperties
    chinese_font = method2_use_fontproperties()
    
    # 如果方法2失败，尝试方法3
    if chinese_font is None:
        success = method3_download_font()
        if not success:
            # 如果方法3失败，尝试方法4
            chinese_font = method4_use_ttc_font()
    
    # 打印所有可用字体，帮助调试
    print("\n可用字体列表:")
    fonts = sorted([f.name for f in matplotlib.font_manager.fontManager.ttflist])
    for i, font in enumerate(fonts):
        if '黑体' in font or '宋体' in font or '微软' in font or 'SimHei' in font or 'SimSun' in font:
            print(f"- {font} (中文字体)")
        elif i < 10:  # 只打印前10个非中文字体
            print(f"- {font}")
    
    if chinese_font is not None:
        print("\n成功配置中文字体!")
        return chinese_font
    else:
        print("\n警告: 所有配置中文字体的方法都失败了。图表中的中文可能无法正常显示。")
        print("您可以手动安装SimHei.ttf或其他中文字体到系统字体目录中。")
        return None

# 简单测试函数
def test_chinese_display():
    """测试中文显示是否正常"""
    plt.figure(figsize=(10, 6))
    plt.title('中文显示测试')
    plt.xlabel('横坐标')
    plt.ylabel('纵坐标')
    plt.plot([1, 2, 3, 4], [10, 20, 30, 40], label='测试数据')
    plt.legend()
    plt.savefig('./test_chinese.png')
    plt.close()
    print("已生成测试图片: test_chinese.png")

if __name__ == "__main__":
    # 配置中文字体
    chinese_font = configure_chinese_font()
    
    # 测试中文显示
    test_chinese_display() 