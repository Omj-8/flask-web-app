from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

from models import db, User
from forms import RegistrationForm, LoginForm, ProblemForm
from models import Problem
from models import db, User, Problem, Vote
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# 安定したパス指定
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')

# DB初期化
db.init_app(app)

# LoginManager初期化
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_host=form.is_host.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! Please log in.', 'success')
        # 自動ログインをやめてログインページへ
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('problem_list'))  # ログイン済みなら問題一覧に遷移
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('problem_list'))  # login後に問題一覧へ遷移
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')  # ログイン失敗時
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/problems")
@login_required
def problem_list():
    problems = Problem.query.all()
    return render_template("problem_list.html", problems=problems)

@app.route("/problem/<int:problem_id>", methods=['GET', 'POST'])
@login_required
def problem_detail(problem_id):
    problem = Problem.query.get_or_404(problem_id)

    if request.method == 'POST':
        selected_tile = request.form.get('tile')
        if selected_tile:
            # 既に投票済みかチェック（1人1回答制）
            existing_vote = Vote.query.filter_by(user_id=current_user.id, problem_id=problem.id).first()
            if existing_vote:
                flash('すでにこの問題に回答済みです。', 'warning')
            else:
                vote = Vote(user_id=current_user.id, problem_id=problem.id, selected_tile=selected_tile)
                db.session.add(vote)
                db.session.commit()
                flash(f"{selected_tile} を選択しました。", 'success')
        return redirect(url_for('stats', problem_id=problem.id))

    return render_template('problem_detail.html', problem=problem)


@app.route("/stats/<int:problem_id>")
@login_required
def stats(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    votes = Vote.query.filter_by(problem_id=problem.id).all()

    vote_counts = {}
    for vote in votes:
        vote_counts[vote.selected_tile] = vote_counts.get(vote.selected_tile, 0) + 1

    total_votes = len(votes)
    return render_template("stats.html", problem=problem, vote_counts=vote_counts, total_votes=total_votes)

def host_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_host:
            flash("ホストユーザーのみがアクセス可能です。", "danger")
            return redirect(url_for('problem_list'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/create_problem", methods=['GET', 'POST'])
@login_required
@host_required
def create_problem():
    form = ProblemForm()  # フォームをインスタンス化

    if form.validate_on_submit():  # フォームが送信され、バリデーションが成功した場合
        title = form.title.data
        description = form.description.data
        options_raw = form.tile_options.data  # カンマ区切り文字列
        options = [opt.strip() for opt in options_raw.split(',') if opt.strip()]

        if not title or not description or not options:
            flash("すべての項目を入力してください。", "warning")
            return redirect(url_for('create_problem'))

        # Problemインスタンスの作成
        new_problem = Problem(
            title=title,
            description=description,
            tile_options=','.join(options)
        )
        db.session.add(new_problem)
        db.session.commit()
        flash("新しい問題を作成しました！", "success")
        return redirect(url_for('problem_list'))

    return render_template("create_problem.html", form=form)  # formをテンプレートに渡す





if __name__ == '__main__':
    app.run(debug=True)
