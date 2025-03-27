import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib
from matplotlib.font_manager import FontProperties

# 导入字体配置工具
import font_config

# 配置中文字体
chinese_font = font_config.configure_chinese_font()

def load_model_and_encoders():
    """加载训练好的模型和编码器"""
    with open('./model/metabolic_syndrome_model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    with open('./model/label_encoders.pkl', 'rb') as f:
        label_encoders = pickle.load(f)
    
    with open('./model/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    
    with open('./model/feature_selector.pkl', 'rb') as f:
        feature_selector = pickle.load(f)
    
    with open('./model/selected_features.pkl', 'rb') as f:
        selected_features = pickle.load(f)
    
    return model, label_encoders, scaler, feature_selector, selected_features

def predict_metabolic_syndrome(age, sex, marital, income_category, race, waist_circ, 
                              bmi, albuminuria, ur_alb_cr, uric_acid, blood_glucose, 
                              hdl, triglycerides):
    """
    预测一个人是否患有代谢综合征
    
    参数:
    age: 年龄
    sex: 性别 ('Male' 或 'Female')
    marital: 婚姻状况 ('Single', 'Married', 'Divorced', 'Widowed'等)
    income_category: 收入类别 ('Low', 'Mid', 'High')
    race: 种族 ('White', 'Black', 'Asian'等)
    waist_circ: 腰围
    bmi: 体重指数
    albuminuria: 白蛋白尿 (0或1)
    ur_alb_cr: 尿白蛋白肌酐比值
    uric_acid: 尿酸
    blood_glucose: 血糖
    hdl: 高密度脂蛋白胆固醇
    triglycerides: 甘油三酯
    
    返回:
    预测结果 (0: 无代谢综合征, 1: 有代谢综合征)
    预测概率
    """
    # 加载模型和编码器
    model, label_encoders, scaler, feature_selector, selected_features = load_model_and_encoders()
    
    # 对分类特征进行编码
    sex_encoded = label_encoders['Sex'].transform([sex])[0]
    marital_encoded = label_encoders['Marital'].transform([marital])[0]
    income_encoded = label_encoders['IncomeCategory'].transform([income_category])[0]
    race_encoded = label_encoders['Race'].transform([race])[0]
    
    # 计算额外的特征
    waist_bmi_ratio = waist_circ / bmi
    glucose_hdl_ratio = blood_glucose / hdl
    trig_hdl_ratio = triglycerides / hdl
    
    # 根据年龄确定年龄组
    if age < 30:
        age_group = 0
    elif age < 45:
        age_group = 1
    elif age < 60:
        age_group = 2
    else:
        age_group = 3
    
    # 创建特征向量（包含所有原始特征和新特征）
    all_features = [age, sex_encoded, marital_encoded, income_encoded, race_encoded, 
                   waist_circ, bmi, albuminuria, ur_alb_cr, uric_acid, blood_glucose, 
                   hdl, triglycerides, waist_bmi_ratio, glucose_hdl_ratio, trig_hdl_ratio, 
                   age_group]
    
    # 特征标准化
    features_scaled = scaler.transform([all_features])
    
    # 应用特征选择
    features_selected = feature_selector.transform(features_scaled)
    
    # 预测
    prediction = model.predict(features_selected)[0]
    probability = model.predict_proba(features_selected)[0]
    
    return prediction, probability

def visualize_prediction(prediction, probability, patient_data):
    """可视化预测结果"""
    # 创建保存预测可视化的目录
    if not os.path.exists('./predictions'):
        os.makedirs('./predictions')
    
    # 绘制预测概率条形图
    plt.figure(figsize=(10, 6))
    plt.bar(['无代谢综合征', '有代谢综合征'], probability, color=['green', 'red'])
    plt.ylim(0, 1)
    plt.ylabel('概率')
    plt.title('代谢综合征预测概率')
    for i, v in enumerate(probability):
        plt.text(i, v + 0.05, f'{v:.2f}', ha='center')
    plt.savefig('./predictions/prediction_probability.png')
    
    # 绘制关键指标的雷达图
    # 选择要在雷达图中显示的关键指标
    key_features = ['腰围', 'BMI', '血糖', 'HDL', '甘油三酯', '年龄']
    key_values = [
        patient_data['waist_circ'], 
        patient_data['bmi'], 
        patient_data['blood_glucose'],

        patient_data['hdl'],
        patient_data['triglycerides'],
        patient_data['age']
    ]
    
    # 标准化值以适应雷达图 (0-1之间)
    # 这些是参考范围，可以根据实际情况调整
    reference_ranges = {
        '腰围': (70, 110),  # 正常范围可能因性别而异
        'BMI': (18.5, 30),
        '血糖': (70, 120),
        'HDL': (40, 60),
        '甘油三酯': (50, 200),
        '年龄': (20, 80)
    }
    
    normalized_values = []
    for i, feature in enumerate(key_features):
        min_val, max_val = reference_ranges[feature]
        val = key_values[i]
        # 限制在0-1范围内
        norm_val = (val - min_val) / (max_val - min_val)
        norm_val = max(0, min(1, norm_val))
        normalized_values.append(norm_val)
    
    # 添加首个元素，以闭合雷达图
    key_features.append(key_features[0])
    normalized_values.append(normalized_values[0])
    
    # 创建雷达图
    angles = np.linspace(0, 2*np.pi, len(key_features)-1, endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))
    
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, normalized_values, 'o-', linewidth=2)
    ax.fill(angles, normalized_values, alpha=0.25)
    ax.set_thetagrids(angles * 180/np.pi, key_features)
    ax.set_ylim(0, 1)
    ax.set_title('患者关键指标雷达图')
    plt.savefig('./predictions/patient_radar.png')
    
    # 返回保存的图像文件路径
    return './predictions/prediction_probability.png', './predictions/patient_radar.png'

# 示例使用
if __name__ == "__main__":
    # 用户输入示例
    print("\n======代谢综合征预测系统======")
    print("\n请输入以下信息用于代谢综合征预测:")
    
    age = int(input("年龄: "))
    sex = input("性别 (Male/Female): ")
    marital = input("婚姻状况 (Single/Married/Divorced/Widowed): ")
    income_category = input("收入类别 (Low/Mid/High): ")
    race = input("种族 (White/Black/Asian等): ")
    waist_circ = float(input("腰围: "))
    bmi = float(input("体重指数: "))
    albuminuria = int(input("白蛋白尿 (0/1): "))
    ur_alb_cr = float(input("尿白蛋白肌酐比值: "))
    uric_acid = float(input("尿酸: "))
    blood_glucose = float(input("血糖: "))
    hdl = float(input("高密度脂蛋白胆固醇: "))
    triglycerides = float(input("甘油三酯: "))
    
    # 收集患者数据用于可视化
    patient_data = {
        'age': age, 'sex': sex, 'marital': marital, 'income_category': income_category,
        'race': race, 'waist_circ': waist_circ, 'bmi': bmi, 'albuminuria': albuminuria,
        'ur_alb_cr': ur_alb_cr, 'uric_acid': uric_acid, 'blood_glucose': blood_glucose,
        'hdl': hdl, 'triglycerides': triglycerides
    }
    
    # 进行预测
    prediction, probability = predict_metabolic_syndrome(
        age, sex, marital, income_category, race, waist_circ, 
        bmi, albuminuria, ur_alb_cr, uric_acid, blood_glucose, 
        hdl, triglycerides
    )
    
    # 可视化预测结果
    prob_chart, radar_chart = visualize_prediction(prediction, probability, patient_data)
    
    # 输出结果
    if prediction == 0:
        result = "无代谢综合征"
        risk_level = "低风险"
    else:
        result = "有代谢综合征"
        risk_level = "高风险"
    
    print("\n" + "="*40)
    print("预测结果摘要".center(40))
    print("="*40)
    print(f"预测结果: {result}")
    print(f"风险等级: {risk_level}")
    print(f"无代谢综合征的概率: {probability[0]:.4f}")
    print(f"有代谢综合征的概率: {probability[1]:.4f}")
    print("="*40)
    print(f"\n可视化结果已保存到:\n1. {prob_chart}\n2. {radar_chart}")
    
    # 提供健康建议
    print("\n健康建议:")
    if prediction == 1:
        print("1. 建议定期进行医疗检查，关注代谢指标变化")
        print("2. 保持健康的饮食习惯，减少高糖、高脂肪食物摄入")
        print("3. 增加体育锻炼，控制体重和腰围")
        print("4. 考虑咨询医生获取专业的治疗建议")
    else:
        print("1. 继续保持健康的生活方式")
        print("2. 定期体检，监测代谢指标")
        print("3. 均衡饮食，适量运动") 