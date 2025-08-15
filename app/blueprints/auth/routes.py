from flask import render_template, request, jsonify, redirect, url_for, flash, make_response, session
from app import mongo, bcrypt
from . import auth_bp
from bson.objectid import ObjectId
import traceback
import datetime
from bs4 import BeautifulSoup

# 登录页面
@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# 注册页面
@auth_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

# 主页
@auth_bp.route('/home', methods=['GET'])
def home_page():
    # 检查用户是否已登录，通过session验证
    if 'user_id' not in session:
        # 未登录，重定向到登录页面
        return redirect(url_for('auth.login_page'))
    
    try:
        # 获取当前用户ID
        current_user_id = session['user_id']
        
        # 查找用户信息
        user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
        
        if not user:
            # 如果用户不存在，重定向到登录页面
            return redirect(url_for('auth.login_page'))
        
        return render_template('home.html', user=user)
    except Exception as e:
        # 记录错误
        print(f"访问主页时发生错误: {str(e)}")
        print(traceback.format_exc())
        # 重定向到登录页面
        return redirect(url_for('auth.login_page'))

# 用户注册API
@auth_bp.route('/api/register', methods=['POST'])
def register():
    # 获取注册表单数据
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # 表单验证
    if not username or not email or not password or not confirm_password:
        return jsonify({"success": False, "message": "所有字段都是必填的"}), 400
    
    if password != confirm_password:
        return jsonify({"success": False, "message": "两次输入的密码不一致"}), 400
    
    # 检查用户名或邮箱是否已存在
    if mongo.db.users.find_one({"$or": [{"username": username}, {"email": email}]}):
        return jsonify({"success": False, "message": "用户名或邮箱已被使用"}), 400
    
    # 哈希密码
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # 创建用户记录
    user = {
        "username": username,
        "email": email,
        "password": hashed_password
    }
    
    # 将用户添加到数据库
    result = mongo.db.users.insert_one(user)
    
    return jsonify({"success": True, "message": "注册成功"}), 201

# 用户登录API
@auth_bp.route('/api/login', methods=['POST'])
def login():
    # 获取登录表单数据
    username = request.form.get('username')
    password = request.form.get('password')
    
    # 表单验证
    if not username or not password:
        return jsonify({"success": False, "message": "请输入用户名和密码"}), 400
    
    # 查找用户
    user = mongo.db.users.find_one({"username": username})
    
    # 验证用户和密码
    if user and bcrypt.check_password_hash(user['password'], password):
        # 保存用户ID到session
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        
        # 创建响应
        return jsonify({"success": True, "message": "登录成功"}), 200
    else:
        return jsonify({"success": False, "message": "用户名或密码错误"}), 401

# 退出登录
@auth_bp.route('/logout')
def logout():
    # 清除session
    session.clear()
    return redirect(url_for('auth.login_page'))

# 用户信息API
@auth_bp.route('/api/profile', methods=['GET'])
def profile():
    # 获取当前用户ID
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "未登录"}), 401
        
    current_user_id = session['user_id']
    
    # 查找用户信息
    user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
    
    if not user:
        return jsonify({"success": False, "message": "用户不存在"}), 404
    
    # 返回用户信息，排除密码
    user_data = {
        "username": user['username'],
        "email": user['email']
    }
    
    return jsonify({"success": True, "user": user_data}), 200

# 发布文章页面
@auth_bp.route('/publish', methods=['GET'])
def publish_article_page():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    
    # 获取draft_id参数
    draft_id = request.args.get('draft_id')
    draft = None
    
    # 如果有draft_id，尝试加载草稿
    if draft_id and ObjectId.is_valid(draft_id):
        draft = mongo.db.drafts.find_one({
            "_id": ObjectId(draft_id),
            "author_id": session['user_id'],
            "is_draft": True
        })
        
        if draft:
            # 转换ID为字符串，方便在模板中使用
            draft['_id'] = str(draft['_id'])
    
    return render_template('publish_article.html', draft=draft)

# 发布文章API
@auth_bp.route('/api/article/publish', methods=['POST'])
def publish_article():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401
    
    try:
        print("收到文章发布请求")
        data = request.json
        
        if not data:
            return jsonify({"success": False, "message": "未接收到数据"}), 400
            
        print(f"接收到的数据: {data}")
        
        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        tags = data.get('tags', [])
        
        # 验证数据
        if not title or not content or not category:
            return jsonify({"success": False, "message": "文章标题、内容和分类为必填项"}), 400
        
        if len(title) < 5 or len(title) > 100:
            return jsonify({"success": False, "message": "标题长度应在5-100字之间"}), 400
        
        # 创建文章记录
        article = {
            "title": title,
            "content": content,
            "category": category,
            "tags": tags,
            "author_id": session['user_id'],
            "author_name": session['username'],
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "views": 0,
            "likes": 0,
            "comments": []
        }
        
        # 将文章添加到数据库
        result = mongo.db.articles.insert_one(article)
        article_id = str(result.inserted_id)
        
        return jsonify({
            "success": True, 
            "message": "文章发布成功", 
            "article_id": article_id,
            "redirect_url": url_for('auth.article_detail', article_id=article_id)
        }), 201
        
    except Exception as e:
        print(f"发布文章错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": f"发布文章时发生错误: {str(e)}"}), 500

# 保存草稿API
@auth_bp.route('/api/article/draft', methods=['POST'])
def save_article_draft():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401
    
    try:
        data = request.json
        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        tags = data.get('tags', [])
        draft_id = data.get('draft_id')
        
        # 如果提供了draft_id且有效，直接更新该草稿
        if draft_id and ObjectId.is_valid(draft_id):
            draft = mongo.db.drafts.find_one({
                "_id": ObjectId(draft_id),
                "author_id": session['user_id']
            })
            
            if draft:
                mongo.db.drafts.update_one(
                    {"_id": ObjectId(draft_id)},
                    {"$set": {
                        "title": title,
                        "content": content,
                        "category": category,
                        "tags": tags,
                        "updated_at": datetime.datetime.now()
                    }}
                )
                return jsonify({
                    "success": True, 
                    "message": "草稿已更新",
                    "redirect_url": url_for('auth.user_center')
                }), 200
        
        # 创建草稿记录
        draft = {
            "title": title,
            "content": content,
            "category": category,
            "tags": tags,
            "author_id": session['user_id'],
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "is_draft": True
        }
        
        # 检查用户是否已有该草稿
        existing_draft = mongo.db.drafts.find_one({
            "author_id": session['user_id'],
            "title": title,
            "is_draft": True
        })
        
        if existing_draft:
            # 更新现有草稿
            mongo.db.drafts.update_one(
                {"_id": existing_draft['_id']},
                {"$set": {
                    "content": content,
                    "category": category,
                    "tags": tags,
                    "updated_at": datetime.datetime.now()
                }}
            )
            return jsonify({
                "success": True, 
                "message": "草稿已更新",
                "redirect_url": url_for('auth.user_center')
            }), 200
        else:
            # 创建新草稿
            result = mongo.db.drafts.insert_one(draft)
            return jsonify({
                "success": True, 
                "message": "草稿已保存",
                "redirect_url": url_for('auth.user_center')
            }), 201
            
    except Exception as e:
        print(f"保存草稿错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": "保存草稿时发生错误"}), 500

# 删除草稿API
@auth_bp.route('/api/draft/delete/<draft_id>', methods=['POST'])
def delete_draft(draft_id):
    # 检查用户是否已登录
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401
    
    try:
        current_user_id = session['user_id']
        
        # 检查draft_id是否有效
        if not ObjectId.is_valid(draft_id):
            return jsonify({"success": False, "message": "无效的草稿ID"}), 400
        
        # 获取草稿信息确保归属当前用户
        draft = mongo.db.drafts.find_one({
            "_id": ObjectId(draft_id),
            "author_id": current_user_id
        })
        
        if not draft:
            return jsonify({"success": False, "message": "草稿不存在或无权限删除"}), 404
        
        # 删除草稿
        mongo.db.drafts.delete_one({"_id": ObjectId(draft_id)})
        
        return jsonify({
            "success": True,
            "message": "草稿已成功删除",
            "redirect_url": url_for('auth.user_center')
        }), 200
        
    except Exception as e:
        print(f"删除草稿错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": f"删除草稿时发生错误: {str(e)}"}), 500

# 文章详情页面
@auth_bp.route('/article/<article_id>', methods=['GET'])
def article_detail(article_id):
    try:
        print(f"\n\n============ 开始处理文章详情请求 ============")
        print(f"接收到文章详情请求，article_id: {article_id}, 类型: {type(article_id)}")
        
        # 检查article_id是否为有效的ObjectId格式
        if not ObjectId.is_valid(article_id):
            print(f"无效的文章ID格式: {article_id}")
            print(f"============ 结束处理文章详情请求 ============\n\n")
            return redirect(url_for('auth.articles'))
        
        print(f"文章ID有效，尝试查询文章数据")
        # 查找文章
        article = mongo.db.articles.find_one({"_id": ObjectId(article_id)})
        
        if not article:
            print(f"未找到ID为{article_id}的文章")
            print(f"============ 结束处理文章详情请求 ============\n\n")
            return redirect(url_for('auth.articles'))
        
        print(f"成功找到文章: {article['title']}")
        # 增加浏览量
        mongo.db.articles.update_one(
            {"_id": ObjectId(article_id)},
            {"$inc": {"views": 1}}
        )
        
        # 确保关联文章的ID是字符串
        article['_id'] = str(article['_id'])
        
        # 从文章内容中提取标题
        headings = []
        if article.get('content'):
            try:
                soup = BeautifulSoup(article['content'], 'html.parser')
                for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
                    level = int(heading.name[1])
                    headings.append({
                        'level': level,
                        'text': heading.text.strip(),
                        'id': f'heading-{i+1}'
                    })
            except Exception as e:
                print(f"解析标题时发生错误: {str(e)}")
        
        # 查找相关文章
        related_articles = list(mongo.db.articles.find({
            "category": article['category'],
            "_id": {"$ne": ObjectId(article_id)}
        }).sort("created_at", -1).limit(3))
        
        # 处理相关文章中的ID
        for related in related_articles:
            related['_id'] = str(related['_id'])
        
        # 查找作者信息
        author = None
        article_count = 0
        total_views = 0
        
        if article.get('author_id'):
            author = mongo.db.users.find_one({"_id": ObjectId(article['author_id'])})
            
            # 获取作者文章数
            article_count = mongo.db.articles.count_documents({"author_id": article['author_id']})
            
            # 获取作者所有文章的总浏览量
            author_articles = mongo.db.articles.find({"author_id": article['author_id']})
            total_views = sum(doc.get('views', 0) for doc in author_articles)
        
        return render_template('article_detail.html', 
                              article=article, 
                              related_articles=related_articles, 
                              author=author, 
                              headings=headings,
                              article_count=article_count,
                              total_views=total_views)
        
    except Exception as e:
        print(f"加载文章详情错误: {str(e)}")
        print(traceback.format_exc())
        return redirect(url_for('auth.home_page'))

# 所有文章列表页面
@auth_bp.route('/articles', methods=['GET'])
def articles():
    try:
        # 获取所有文章，按创建时间倒序排列
        articles = list(mongo.db.articles.find().sort("created_at", -1))
        
        # 添加可读的日期格式
        for article in articles:
            # 确保_id是字符串，以便在模板中使用
            article['_id'] = str(article['_id'])
            
            # 如果没有文章摘要，可以从内容生成
            if 'excerpt' not in article:
                # 从内容移除HTML标签并截取前150个字符作为摘要
                if article.get('content'):
                    soup = BeautifulSoup(article['content'], 'html.parser')
                    article['excerpt'] = soup.get_text()[:150] + '...'
        
        return render_template('article_list.html', articles=articles)
    
    except Exception as e:
        print(f"加载文章列表错误: {str(e)}")
        print(traceback.format_exc())
        return redirect(url_for('auth.home_page'))

# 个人中心页面
@auth_bp.route('/user-center', methods=['GET'])
def user_center():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    
    try:
        current_user_id = session['user_id']
        
        # 获取用户信息
        user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            return redirect(url_for('auth.login_page'))
        
        # 获取用户的文章列表
        user_articles = list(mongo.db.articles.find(
            {"author_id": current_user_id}
        ).sort("created_at", -1))
        
        # 处理文章数据
        for article in user_articles:
            article['_id'] = str(article['_id'])
            
            # 生成摘要
            if 'excerpt' not in article and article.get('content'):
                soup = BeautifulSoup(article['content'], 'html.parser')
                article['excerpt'] = soup.get_text()[:150] + '...'
            
            # 格式化时间
            if article.get('created_at'):
                article['created_at_formatted'] = article['created_at'].strftime('%Y-%m-%d %H:%M')
        
        # 获取用户的草稿列表
        user_drafts = list(mongo.db.drafts.find(
            {"author_id": current_user_id, "is_draft": True}
        ).sort("updated_at", -1))
        
        # 处理草稿数据
        for draft in user_drafts:
            draft['_id'] = str(draft['_id'])
            
            # 格式化时间
            if draft.get('updated_at'):
                draft['updated_at_formatted'] = draft['updated_at'].strftime('%Y-%m-%d %H:%M')
        
        # 计算统计数据
        total_articles = len(user_articles)
        total_views = sum(article.get('views', 0) for article in user_articles)
        total_likes = sum(article.get('likes', 0) for article in user_articles)
        
        # 用户信息
        user_info = {
            "username": user['username'],
            "email": user['email'],
            "total_articles": total_articles,
            "total_views": total_views,
            "total_likes": total_likes,
            "join_date": user.get('created_at', datetime.datetime.now()).strftime('%Y-%m-%d')
        }
        
        return render_template('user_center.html', 
                              user=user_info,
                              articles=user_articles,
                              drafts=user_drafts)
    
    except Exception as e:
        print(f"加载个人中心页面错误: {str(e)}")
        print(traceback.format_exc())
        return redirect(url_for('auth.home_page'))

# 编辑文章页面
@auth_bp.route('/edit-article/<article_id>', methods=['GET'])
def edit_article_page(article_id):
    # 检查用户是否已登录
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    
    try:
        current_user_id = session['user_id']
        
        # 检查article_id是否有效
        if not ObjectId.is_valid(article_id):
            return redirect(url_for('auth.user_center'))
        
        # 获取文章信息
        article = mongo.db.articles.find_one({
            "_id": ObjectId(article_id),
            "author_id": current_user_id
        })
        
        # 如果文章不存在或不属于当前用户
        if not article:
            return redirect(url_for('auth.user_center'))
        
        # 确保ID是字符串
        article['_id'] = str(article['_id'])
        
        return render_template('edit_article.html', article=article)
    
    except Exception as e:
        print(f"加载编辑文章页面错误: {str(e)}")
        print(traceback.format_exc())
        return redirect(url_for('auth.user_center'))

# 更新文章API
@auth_bp.route('/api/article/update/<article_id>', methods=['POST'])
def update_article(article_id):
    # 检查用户是否已登录
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401
    
    try:
        current_user_id = session['user_id']
        data = request.json
        
        # 验证请求数据
        if not data:
            return jsonify({"success": False, "message": "未接收到数据"}), 400
        
        # 检查article_id是否有效
        if not ObjectId.is_valid(article_id):
            return jsonify({"success": False, "message": "无效的文章ID"}), 400
        
        # 获取文章信息确保归属当前用户
        article = mongo.db.articles.find_one({
            "_id": ObjectId(article_id),
            "author_id": current_user_id
        })
        
        if not article:
            return jsonify({"success": False, "message": "文章不存在或无权限修改"}), 404
        
        # 获取更新数据
        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        tags = data.get('tags', [])
        
        # 验证必填字段
        if not title or not content or not category:
            return jsonify({"success": False, "message": "文章标题、内容和分类为必填项"}), 400
        
        if len(title) < 5 or len(title) > 100:
            return jsonify({"success": False, "message": "标题长度应在5-100字之间"}), 400
        
        # 更新文章
        mongo.db.articles.update_one(
            {"_id": ObjectId(article_id)},
            {"$set": {
                "title": title,
                "content": content,
                "category": category,
                "tags": tags,
                "updated_at": datetime.datetime.now()
            }}
        )
        
        return jsonify({
            "success": True,
            "message": "文章更新成功",
            "redirect_url": url_for('auth.article_detail', article_id=article_id)
        }), 200
        
    except Exception as e:
        print(f"更新文章错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": f"更新文章时发生错误: {str(e)}"}), 500

# 删除文章API
@auth_bp.route('/api/article/delete/<article_id>', methods=['POST'])
def delete_article(article_id):
    # 检查用户是否已登录
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401
    
    try:
        current_user_id = session['user_id']
        
        # 检查article_id是否有效
        if not ObjectId.is_valid(article_id):
            return jsonify({"success": False, "message": "无效的文章ID"}), 400
        
        # 获取文章信息确保归属当前用户
        article = mongo.db.articles.find_one({
            "_id": ObjectId(article_id),
            "author_id": current_user_id
        })
        
        if not article:
            return jsonify({"success": False, "message": "文章不存在或无权限删除"}), 404
        
        # 删除文章
        mongo.db.articles.delete_one({"_id": ObjectId(article_id)})
        
        return jsonify({
            "success": True,
            "message": "文章已成功删除",
            "redirect_url": url_for('auth.user_center')
        }), 200
        
    except Exception as e:
        print(f"删除文章错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": f"删除文章时发生错误: {str(e)}"}), 500 