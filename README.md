# 世界指南 - 用户认证系统

这是一个基于Flask和MongoDB的用户认证系统，提供了用户注册和登录功能。

## 系统要求

- Python 3.7+
- MongoDB

## 安装

1. 克隆或下载此仓库到本地

2. 安装依赖包
```
pip install -r requirements.txt
```

3. 配置环境变量
   - 可以直接使用项目中的.env文件
   - 在生产环境中，请修改密钥

## 运行项目

```
python run.py
```

应用将运行在 http://127.0.0.1:5000/

## 功能

- 用户注册：创建新账户
- 用户登录：使用账户凭证登录
- 用户个人资料：查看个人信息

## 项目结构

```
├── app/                      # 应用主目录
│   ├── __init__.py          # 应用初始化
│   ├── blueprints/          # 蓝图目录
│   │   └── auth/            # 认证蓝图
│   │       ├── __init__.py  # 蓝图初始化
│   │       └── routes.py    # 路由定义
│   ├── static/              # 静态文件
│   │   ├── css/             # CSS样式
│   │   └── js/              # JavaScript脚本
│   └── templates/           # HTML模板
├── .env                     # 环境变量配置
├── README.md                # 项目说明
├── requirements.txt         # 项目依赖
└── run.py                   # 应用入口点
```

## API端点

- `/auth/login` - 登录页面
- `/auth/register` - 注册页面
- `/auth/home` - 用户主页
- `/auth/api/register` - 注册API
- `/auth/api/login` - 登录API
- `/auth/api/profile` - 用户资料API (需要JWT认证) 