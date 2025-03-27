from openai import OpenAI
import pickle
from datetime import date
from django.conf import settings
import os
from django.apps import apps

client = OpenAI(
        api_key="sk-d3ccec29a26d4886a3fcb91a2877d794",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


def get_diet_recommend(diet_record, taboo_ingredients, favorite_ingredients, recipe_book, nutrition_requirements, gender,
                       age, medical_history):
    """
    根据用户的饮食记录和个人信息生成个性化的饮食建议。

    参数:
        diet_record: 用户前1-3天的膳食记录
        taboo_ingredients: 用户忌口的食材列表
        favorite_ingredients: 用户喜欢的食材列表
        recipe_book: 可选的菜谱信息，包含食材和营养成分
        nutrition_requirements: 用户所需的营养成分占比
        gender: 用户性别
        age: 用户年龄
        medical_history: 用户病史

    返回:
        str: 包含早餐、午餐、晚餐建议的个性化饮食方案
    """
    # 系统角色设定
    system_prompt = '你是一个**营养膳食专家**，专为康养中心的中老年客户服务。'
    
    # 构建用户提示词
    user_prompt = (
        f'请用不超过100个汉字的中文回答以下问题。\n\n'
        f'请参考用户前一到三天的膳食记录：{diet_record}，并在推荐新的一天饮食时，'
        f'尽量避免与最近三天内用户食用过的食物重复。\n\n'
        f'在推荐的菜谱中，请避免使用用户的忌口食材：{taboo_ingredients}，'
        f'并尽量使用用户爱吃的食材：{favorite_ingredients}。\n\n'
        f'请从提供的菜谱中选择适合的菜品，菜谱信息为：{recipe_book}，'
        f'每道菜的食材和营养成分占比均已提供。\n\n'
        f'**请为用户推荐一天的饮食，包括早餐、午餐、晚餐，并对每餐做出解释（人性化解释）'
        f'（请尽量避免一天出现重复菜品的情况）**，并确保推荐的饮食方案能够满足用户所需的'
        f'营养成分占比：{nutrition_requirements}（这里的营养占比可能会不符合常理，'
        f'这种情况下请忽略营养占比）\n\n'
        f'（用于参考的用户的个人信息：\n'
        f'性别：{gender}，年龄：{age}，病史：{medical_history}。）'
    )

    # 调用API生成饮食建议
    completion = client.chat.completions.create(
        model="qwen-max-latest",
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
    )
    
    # 返回生成的建议
    return completion.choices[0].message.content


def get_metrics_assessment(age, sex, marital, income_category, race, vital_signs, mets_probability):
    """
    给出身体建议

    参数:
    age: 年龄
    sex: 性别 ('Male' 或 'Female')
    marital: 婚姻状况 ('Single', 'Married', 'Divorced', 'Widowed'等)
    income_category: 收入类别 ('Low', 'Mid', 'High')
    race: 种族 ('White', 'Black', 'Asian'等)
    vital_signs: 身体指标
    mets_probability: 患代谢综合症的概率

    返回:
    智能建议
    """
    content = f"""
    请基于以下用户信息和身体指标，提供专业的健康建议：
    
    基本信息：
    - 年龄：{age}岁
    - 性别：{sex}
    - 婚姻状况：{marital}
    - 收入水平：{income_category}
    - 种族：{race}
    
    身体指标：
    - BMI：{vital_signs.get('bmi', {}).get('value')} {vital_signs.get('bmi', {}).get('unit')}（正常范围：{vital_signs.get('bmi', {}).get('normal_range')}）
    - 身高：{vital_signs.get('height', {}).get('value')} {vital_signs.get('height', {}).get('unit')}
    - 体重：{vital_signs.get('weight', {}).get('value')} {vital_signs.get('weight', {}).get('unit')}
    - 尿酸：{vital_signs.get('uric_acid', {}).get('value')} {vital_signs.get('uric_acid', {}).get('unit')}（正常范围：{vital_signs.get('uric_acid', {}).get('normal_range')}）
    - 心率：{vital_signs.get('heart_rate', {}).get('value')} {vital_signs.get('heart_rate', {}).get('unit')}（正常范围：{vital_signs.get('heart_rate', {}).get('normal_range')}）
    - 白蛋白尿：{vital_signs.get('albuminuria', {}).get('value')} {vital_signs.get('albuminuria', {}).get('unit')}（正常范围：{vital_signs.get('albuminuria', {}).get('normal_range')}）
    - 血糖：{vital_signs.get('blood_glucose', {}).get('value')} {vital_signs.get('blood_glucose', {}).get('unit')}（正常范围：{vital_signs.get('blood_glucose', {}).get('normal_range')}）
    - 甘油三酯：{vital_signs.get('triglycerides', {}).get('value')} {vital_signs.get('triglycerides', {}).get('unit')}（正常范围：{vital_signs.get('triglycerides', {}).get('normal_range')}）
    - 血压：收缩压 {vital_signs.get('blood_pressure', {}).get('systolic', {}).get('value')} {vital_signs.get('blood_pressure', {}).get('systolic', {}).get('unit')}（正常范围：{vital_signs.get('blood_pressure', {}).get('systolic', {}).get('normal_range')}），
            舒张压 {vital_signs.get('blood_pressure', {}).get('diastolic', {}).get('value')} {vital_signs.get('blood_pressure', {}).get('diastolic', {}).get('unit')}（正常范围：{vital_signs.get('blood_pressure', {}).get('diastolic', {}).get('normal_range')}）
    - 高密度脂蛋白胆固醇：{vital_signs.get('hdl_cholesterol', {}).get('value')} {vital_signs.get('hdl_cholesterol', {}).get('unit')}（正常范围：{vital_signs.get('hdl_cholesterol', {}).get('normal_range')}）
    - 体温：{vital_signs.get('body_temperature', {}).get('value')} {vital_signs.get('body_temperature', {}).get('unit')}（正常范围：{vital_signs.get('body_temperature', {}).get('normal_range')}）
    - 呼吸频率：{vital_signs.get('respiratory_rate', {}).get('value')} {vital_signs.get('respiratory_rate', {}).get('unit')}（正常范围：{vital_signs.get('respiratory_rate', {}).get('normal_range')}）
    - 血氧饱和度：{vital_signs.get('oxygen_saturation', {}).get('value')} {vital_signs.get('oxygen_saturation', {}).get('unit')}（正常范围：{vital_signs.get('oxygen_saturation', {}).get('normal_range')}）
    - 腰围：{vital_signs.get('waist_circumference', {}).get('value')} {vital_signs.get('waist_circumference', {}).get('unit')}（正常范围：{vital_signs.get('waist_circumference', {}).get('normal_range')}）
    - 尿白蛋白肌酐比值：{vital_signs.get('urine_albumin_creatinine_ratio', {}).get('value')} {vital_signs.get('urine_albumin_creatinine_ratio', {}).get('unit')}（正常范围：{vital_signs.get('urine_albumin_creatinine_ratio', {}).get('normal_range')}）
    
    代谢综合症风险：
    - 患代谢综合症的概率：{mets_probability*100:.2f}%
    
    请根据上述信息提供详细的健康建议，包括：
    1. 总体健康状况评估
    2. 需要改善的关键指标
    3. 具体的生活方式建议（饮食、运动等）
    4. 是否需要进一步的医疗咨询
    
    请用简单易懂的语言回答，使用中文，不超过300字。
    """

    system_prompt = '你是一个**专业医生**，专精中老年人身体慢性病领域，擅长通过各项身体数据分析出病人的身体情况。'
    completion = client.chat.completions.create(
        model="qwen-max-latest",
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': content},
        ]
    )
    return completion.choices[0].message.content


def load_model_and_encoders():
    """加载训练好的模型和编码器"""
    metabolic_syndrome_model_path = os.path.join(settings.MODELS_DIR, 'metabolic_syndrome_model.pkl')
    label_encoders_path = os.path.join(settings.MODELS_DIR, 'label_encoders.pkl')
    scaler_path = os.path.join(settings.MODELS_DIR, 'scaler.pkl')
    feature_selector_path = os.path.join(settings.MODELS_DIR, 'feature_selector.pkl')
    selected_features_path = os.path.join(settings.MODELS_DIR, 'selected_features.pkl')

    with open(metabolic_syndrome_model_path, 'rb') as f:
        model = pickle.load(f)

    with open(label_encoders_path, 'rb') as f:
        label_encoders = pickle.load(f)

    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)

    with open(feature_selector_path, 'rb') as f:
        feature_selector = pickle.load(f)

    with open(selected_features_path, 'rb') as f:
        selected_features = pickle.load(f)

    return model, label_encoders, scaler, feature_selector, selected_features


def predict_metabolic_syndrome(age, sex, marital, income_category, waist_circ,
                               bmi, albuminuria, ur_alb_cr, uric_acid, blood_glucose,
                               hdl, triglycerides, race='Asian'):
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

    app_config = apps.get_app_config('api')
    model = app_config.model
    label_encoders = app_config.label_encoders
    scaler = app_config.scaler
    feature_selector = app_config.feature_selector
    selected_features = app_config.selected_features


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


def calculate_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
