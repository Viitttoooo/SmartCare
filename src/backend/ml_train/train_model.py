import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, auc, precision_recall_curve
from sklearn.feature_selection import SelectFromModel
import pickle
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib
from matplotlib.font_manager import FontProperties

# 导入字体配置工具
import font_config

# 配置中文字体
chinese_font = font_config.configure_chinese_font()

warnings.filterwarnings('ignore')

# 创建保存模型和图表的目录
if not os.path.exists('./model'):
    os.makedirs('./model')
if not os.path.exists('./plots'):
    os.makedirs('./plots')

# 读取数据集
print("读取数据集...")
df = pd.read_csv('Metabolic Syndrome.csv')

# 数据预处理
print("数据预处理...")
# 查看数据基本信息
print(f"数据集形状: {df.shape}")
print("数据集前5行:")
print(df.head())

# 处理缺失值
print("\n处理缺失值...")
print(f"缺失值统计:\n{df.isnull().sum()}")
# 用中位数填充数值型特征的缺失值
for col in df.select_dtypes(include=['float64', 'int64']).columns:
    if df[col].isnull().sum() > 0:
        df[col] = df[col].fillna(df[col].median())

# Income分类处理
print("\n处理Income字段...")
# 先处理Income列的缺失值
df['Income'] = pd.to_numeric(df['Income'], errors='coerce')
df['Income'] = df['Income'].fillna(df['Income'].median())

# 根据要求将Income分为三类
def categorize_income(income):
    if income < 3000:
        return 'Low'
    elif 3000 <= income <= 6000:
        return 'Mid'
    else:
        return 'High'

df['IncomeCategory'] = df['Income'].apply(categorize_income)
print(f"Income分类统计:\n{df['IncomeCategory'].value_counts()}")

# 对分类特征进行编码
print("\n对分类特征进行编码...")
categorical_cols = ['Sex', 'Marital', 'IncomeCategory', 'Race']
label_encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col + '_Encoded'] = le.fit_transform(df[col])
    label_encoders[col] = le

# 特征工程 - 创建新特征
print("\n特征工程 - 创建新特征...")
# 创建BMI和腰围的比率特征
df['WaistBMIRatio'] = df['WaistCirc'] / df['BMI']
# 创建血糖与HDL的比率
df['GlucoseHDLRatio'] = df['BloodGlucose'] / df['HDL']
# 创建甘油三酯与HDL的比率
df['TrigHDLRatio'] = df['Triglycerides'] / df['HDL']
# 创建年龄分组
df['AgeGroup'] = pd.cut(df['Age'], bins=[0, 30, 45, 60, 100], labels=[0, 1, 2, 3])

# 特征选择
print("\n特征选择...")
# 使用所有特征包括新创建的特征
features = ['Age', 'Sex_Encoded', 'Marital_Encoded', 'IncomeCategory_Encoded', 
           'Race_Encoded', 'WaistCirc', 'BMI', 'Albuminuria', 'UrAlbCr', 
           'UricAcid', 'BloodGlucose', 'HDL', 'Triglycerides',
           'WaistBMIRatio', 'GlucoseHDLRatio', 'TrigHDLRatio', 'AgeGroup']
X = df[features]
y = df['MetabolicSyndrome']

print(f"特征列表: {features}")

# 数据标准化
print("\n数据标准化...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 特征选择 - 使用随机森林特征重要性
print("\n使用随机森林进行特征选择...")
selector = RandomForestClassifier(n_estimators=100, random_state=42)
selector.fit(X_scaled, y)

# 特征重要性可视化
feature_importance = selector.feature_importances_
indices = np.argsort(feature_importance)[::-1]
plt.figure(figsize=(10, 6))
plt.title('特征重要性')
plt.bar(range(X.shape[1]), feature_importance[indices], align='center')
plt.xticks(range(X.shape[1]), [features[i] for i in indices], rotation=90)
plt.tight_layout()
plt.savefig('./plots/feature_importance.png')

# 选择重要特征
print("\n选择重要特征...")
sfm = SelectFromModel(selector, threshold=0.03)
sfm.fit(X_scaled, y)
X_selected = sfm.transform(X_scaled)
selected_features_indices = sfm.get_support(indices=True)
selected_features = [features[i] for i in selected_features_indices]
print(f"选择的重要特征: {selected_features}")

# 分割训练集和测试集
print("\n分割数据集...")
X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=0.2, random_state=42, stratify=y)
print(f"训练集大小: {X_train.shape}, 测试集大小: {X_test.shape}")

# 交叉验证评估不同模型
print("\n交叉验证评估不同模型...")
models = {
    "随机森林": RandomForestClassifier(random_state=42),
    "梯度提升": GradientBoostingClassifier(random_state=42),
    "逻辑回归": LogisticRegression(random_state=42, max_iter=1000),
    "支持向量机": SVC(probability=True, random_state=42)
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_results = {}

for name, model in models.items():
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
    cv_results[name] = (cv_scores.mean(), cv_scores.std())
    print(f"{name} 交叉验证准确率: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# 选择最佳单一模型
best_model_name = max(cv_results.items(), key=lambda x: x[1][0])[0]
print(f"\n最佳单一模型: {best_model_name}")

# 网格搜索优化最佳模型超参数
print("\n网格搜索优化超参数...")
if best_model_name == "随机森林":
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    best_model = RandomForestClassifier(random_state=42)
elif best_model_name == "梯度提升":
    param_grid = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'min_samples_split': [2, 5, 10]
    }
    best_model = GradientBoostingClassifier(random_state=42)
elif best_model_name == "逻辑回归":
    param_grid = {
        'C': [0.01, 0.1, 1, 10, 100],
        'penalty': ['l1', 'l2'],
        'solver': ['liblinear', 'saga']
    }
    best_model = LogisticRegression(random_state=42, max_iter=1000)
else:  # 支持向量机
    param_grid = {
        'C': [0.1, 1, 10],
        'kernel': ['linear', 'rbf', 'poly'],
        'gamma': ['scale', 'auto', 0.1, 1]
    }
    best_model = SVC(probability=True, random_state=42)

grid_search = GridSearchCV(best_model, param_grid, cv=cv, scoring='accuracy')
grid_search.fit(X_train, y_train)
print(f"最佳参数: {grid_search.best_params_}")
print(f"最佳交叉验证得分: {grid_search.best_score_:.4f}")

# 创建集成模型
print("\n创建集成模型...")
estimators = []
for name, model in models.items():
    if name == best_model_name:
        estimators.append((name, grid_search.best_estimator_))
    else:
        estimators.append((name, model))

ensemble_model = VotingClassifier(estimators=estimators, voting='soft')
ensemble_model.fit(X_train, y_train)

# 在测试集上评估单一最佳模型和集成模型
print("\n在测试集上评估模型...")
best_single_model = grid_search.best_estimator_
y_pred_best = best_single_model.predict(X_test)
y_pred_ensemble = ensemble_model.predict(X_test)

print("\n最佳单一模型评估:")
acc_best = accuracy_score(y_test, y_pred_best)
print(f"准确率: {acc_best:.4f}")
print("\n分类报告:")
print(classification_report(y_test, y_pred_best))
print("\n混淆矩阵:")
conf_matrix_best = confusion_matrix(y_test, y_pred_best)
print(conf_matrix_best)

print("\n集成模型评估:")
acc_ensemble = accuracy_score(y_test, y_pred_ensemble)
print(f"准确率: {acc_ensemble:.4f}")
print("\n分类报告:")
print(classification_report(y_test, y_pred_ensemble))
print("\n混淆矩阵:")
conf_matrix_ensemble = confusion_matrix(y_test, y_pred_ensemble)
print(conf_matrix_ensemble)

# 选择最终模型
final_model = ensemble_model if acc_ensemble > acc_best else best_single_model
final_model_name = "集成模型" if acc_ensemble > acc_best else "最佳单一模型"
print(f"\n最终选择模型: {final_model_name}")
final_acc = acc_ensemble if acc_ensemble > acc_best else acc_best
final_conf_matrix = conf_matrix_ensemble if acc_ensemble > acc_best else conf_matrix_best

# 保存特征选择器、所选择的特征列表和最终模型
print("\n保存模型和特征相关信息...")
with open('./model/feature_selector.pkl', 'wb') as f:
    pickle.dump(sfm, f)

with open('./model/selected_features.pkl', 'wb') as f:
    pickle.dump(selected_features, f)

with open('./model/metabolic_syndrome_model.pkl', 'wb') as f:
    pickle.dump(final_model, f)

with open('./model/label_encoders.pkl', 'wb') as f:
    pickle.dump(label_encoders, f)

with open('./model/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# 可视化结果
print("\n可视化结果...")

# 1. 混淆矩阵可视化
plt.figure(figsize=(8, 6))
sns.heatmap(final_conf_matrix, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['无代谢综合征', '有代谢综合征'],
            yticklabels=['无代谢综合征', '有代谢综合征'])
plt.xlabel('预测标签')
plt.ylabel('真实标签')
plt.title(f'{final_model_name}混淆矩阵 (准确率: {final_acc:.4f})')
plt.tight_layout()
plt.savefig('./plots/confusion_matrix.png')

# 2. ROC曲线
plt.figure(figsize=(8, 6))
y_pred_prob = final_model.predict_proba(X_test)[:, 1]
fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
roc_auc = auc(fpr, tpr)
plt.plot(fpr, tpr, lw=2, label=f'ROC曲线 (AUC = {roc_auc:.4f})')
plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('假阳性率')
plt.ylabel('真阳性率')
plt.title('ROC曲线')
plt.legend(loc="lower right")
plt.savefig('./plots/roc_curve.png')

# 3. 精确率-召回率曲线
plt.figure(figsize=(8, 6))
precision, recall, _ = precision_recall_curve(y_test, y_pred_prob)
plt.plot(recall, precision, lw=2)
plt.xlabel('召回率')
plt.ylabel('精确率')
plt.title('精确率-召回率曲线')
plt.savefig('./plots/precision_recall_curve.png')

# 4. 类别分布可视化
plt.figure(figsize=(8, 6))
class_counts = df['MetabolicSyndrome'].value_counts()
plt.bar(['无代谢综合征 (0)', '有代谢综合征 (1)'], class_counts.values)
plt.ylabel('样本数量')
plt.title('代谢综合征类别分布')
for i, v in enumerate(class_counts.values):
    plt.text(i, v + 5, str(v), ha='center')
plt.savefig('./plots/class_distribution.png')

# 5. 特征与目标变量的关系
numeric_features = ['Age', 'WaistCirc', 'BMI', 'BloodGlucose', 'HDL', 'Triglycerides']
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

for i, feature in enumerate(numeric_features):
    sns.boxplot(x='MetabolicSyndrome', y=feature, data=df, ax=axes[i])
    axes[i].set_title(f'{feature} vs MetabolicSyndrome')
    axes[i].set_xlabel('代谢综合征 (0: 无, 1: 有)')

plt.tight_layout()
plt.savefig('./plots/feature_vs_target.png')

print("\n模型训练完成！可视化结果已保存到'plots'文件夹。")
print(f"最终模型准确率: {final_acc:.4f}") 