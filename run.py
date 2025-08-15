from app import create_app
from flask import redirect, url_for, request, session

app = create_app()

@app.route('/')
def index():
    # 检查用户是否已登录，通过session验证
    if 'user_id' in session:
        # 已登录，重定向到主页
        return redirect(url_for('auth.home_page'))
    else:
        # 未登录，重定向到登录页面
        return redirect(url_for('auth.login_page'))

if __name__ == '__main__':
    app.run(debug=True) 