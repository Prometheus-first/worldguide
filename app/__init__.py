from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化MongoDB
mongo = PyMongo()
# 初始化Bcrypt
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    
    # 配置MongoDB
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/world_guide")
    
    # 配置应用密钥
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-flask-secret-key")
    
    # 初始化扩展
    mongo.init_app(app)
    bcrypt.init_app(app)
    
    # 注册蓝图
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    return app 