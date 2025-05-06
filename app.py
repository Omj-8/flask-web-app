from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db, User  # 追加：modelsからインポート

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # 適当なキーを設定してください
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLiteのDBファイル名

# データベースの初期化
db.init_app(app)

# ログインマネージャの設定
login_manager = LoginManager()
login_manager.init_app(app)

# Flask-Login用のユーザーローダー関数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 仮のトップページ（動作確認用）
@app.route('/')
def index():
    return 'Hello, Flask App Running!'

if __name__ == '__main__':
    app.run(debug=True)
