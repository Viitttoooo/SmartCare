import os
import pickle
from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """Django启动时自动加载模型"""
        # 声明类变量用于存储加载的资源
        self.model = None
        self.label_encoders = None
        self.scaler = None
        self.feature_selector = None
        self.selected_features = None
        try:
            metabolic_syndrome_model_path = os.path.join(settings.MODELS_DIR, 'metabolic_syndrome_model.pkl')
            label_encoders_path = os.path.join(settings.MODELS_DIR, 'label_encoders.pkl')
            scaler_path = os.path.join(settings.MODELS_DIR, 'scaler.pkl')
            feature_selector_path = os.path.join(settings.MODELS_DIR, 'feature_selector.pkl')
            selected_features_path = os.path.join(settings.MODELS_DIR, 'selected_features.pkl')

            with open(metabolic_syndrome_model_path, 'rb') as f:
                self.model = pickle.load(f)

            with open(label_encoders_path, 'rb') as f:
                self.label_encoders = pickle.load(f)

            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

            with open(feature_selector_path, 'rb') as f:
                self.feature_selector = pickle.load(f)

            with open(selected_features_path, 'rb') as f:
                self.selected_features = pickle.load(f)

        except FileNotFoundError as e:
            raise ImproperlyConfigured(f"Model file missing: {str(e)}")
        except Exception as e:
            raise ImproperlyConfigured(f"Model loading error: {str(e)}")
