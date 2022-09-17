from flask import Flask, render_template, url_for, request, flash, redirect, session
from flask import abort, g
import os
import sqlite3
from db_worker import DBWorker
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CommentForm
from admin_panel.admin import admin

# Конфигурация
DATABASE = '/tmp/flask-blog_database.db'
app = Flask("FlaskBlog")

app.config.from_object('flask_blog') #загружаем конфигурацию(в данном случае из самого себя
app.secret_key = os.environ.get('SECRET_KEY', 'nuio)u*riot&ruot^u43%9859$83#57_@!')
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flask_blog_database.db')))
app.register_blueprint(admin, url_prefix='/admin')


# login_manager = LoginManager(app)
# DB functions
def connect_db(): # connection to DB
    conn = sqlite3.connect(app.config['DATABASE']) # подключает БД
    conn.row_factory = sqlite3.Row      #данные из БД в виде словаря а не кортежа
    return conn    # возвращает подключение

def create_db():
    """Функция создает БД"""
    db = connect_db()    # подключаем БД
    with app.open_resource('scripts_for_site.sql', mode='r') as f:  # Открываем файл со скриптами
        db.cursor().executescript(f.read())    # выполняем скрипты
    db.commit()    # сохраняем изменения
    db.close()      # закрываем соедиение

def get_db():
    """Соединение с БД, если еще не установлено"""
    if not hasattr(g, 'link_db'):    # проверяет есть ли в глобальной переменной g подключение
        g.link_db = connect_db()
    return g.link_db

dbase = None
@app.before_request
def before_request():
    """Устанавливает содинение с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = DBWorker(db)


@app.teardown_appcontext    # срабатывает когда происходит уничтожение контекста приложения
def close_db(error):             # как правило в момент завершения запроса
    """Закрывает соединение если оно было установлено"""
    if hasattr(g, 'link_db'):
        g.link_db.close()

# menu of the site
menu = [['Головна', 'index'], ['Статті', 'posts'], ['Про сайт', 'about'],
        ["Зворотній зв'язок", 'contact'], ]

#view functions
@app.route('/')
def index():
    try:
        page_data = dbase.get_post('index')[0]
    except IndexError:
        page_data = None
    return render_template('index.html', title='Головна сторінка', menu=menu, page_data=page_data)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        if request.form['password'] != request.form['password2']:
            flash('Паролі не співпадають', category='error')
        elif dbase.check_username(request.form['username']):
            flash("Користувач з таким ім'ям вже зареєстрований", category='error')
        elif dbase.check_email(request.form['user_email']):
            flash('Користувач з таким email вже зареєстрований', category='error')
        else:
            username = request.form['username']
            user_email = request.form['user_email']
            pass_hash = generate_password_hash(request.form['password'])
            dbase.register_user(username, user_email, pass_hash)
            flash('Реєстрація успішна', category='success')
            return redirect(url_for('login'))

    return render_template('registration.html', menu=menu, title="Реєстрація")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST':
        if not dbase.check_username(request.form['username']):
            flash("Користувач з таким іменем не зареєстрований", category='error')
        elif not check_password_hash(dbase.get_pswhash(request.form['username']), request.form['password']):
            flash('Невірний пароль', category='error')
        else:
            session['userLogged'] = request.form['username']
            return redirect(url_for('profile', username=session['userLogged']))

    return render_template('login.html', title='Вхід', menu=menu)

@app.route('/logout')
def logout():
    del session['userLogged']
    return redirect(url_for('login'))

@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or username != session['userLogged']:
        abort(401)
    return render_template('profile.html', menu=menu, username=username)

@app.route('/about')
def about():
    try:
        page_data = dbase.get_post('about')[0]
    except IndexError:
        page_data = None
    return render_template('about.html', menu=menu, title='О сайте', page_data=page_data)

@app.route('/contact', methods = ['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        message = request.form['message']
        dbase.record_feedback(name, email, message)
        # with open('static/logs/all_request__dict__.txt', 'a+') as r:
        #     r.write(str(request.__dict__) + '\n')
        # with open('static/logs/messages.txt', 'a+') as m:
        #     m.write(str(request.form) + '\n')
        flash('Відправлено')
        # return render_template('thanks_for_feedback.html', title='Сообщение отправлено', menu=menu)
    return render_template('contact.html', menu=menu, title="Зворотній зв'язок")

@app.route('/posts')
def posts():
    return render_template('posts.html', menu=menu, title='Список статей', posts=dbase.get_all_posts())

@app.route('/posts/<post_slug>', methods=['GET', 'POST'])
def post(post_slug):
    form = CommentForm()
    post = dbase.get_post(post_slug)[0]
    comments = dbase.get_post_comments(post['id'])
    if request.method == 'POST':
        if 'userLogged' in session.keys():
            form.name.data = session['userLogged']
        if form.validate():
            name = form.name.data
            text = form.text.data
            dbase.add_comment(post['id'], name, text)
            flash('Коментар додано', category='success')
            return redirect(url_for('post', post_slug=post_slug))
        else:
            flash("Ім'я або комент мають бути довшими", category='error')
    return render_template('post_template.html', menu=menu, comments=comments, title=post['title'], post=post, form=form)

@app.errorhandler(404)
def pagenotfound(error):
    """Обработчик ошибки 404"""
    return render_template('pagenotfound.html', menu=menu, title='404')

#with app.test_request_context():
 #   print(url_for('other'))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # <-----
    app.run(debug=True, host='0.0.0.0', port=port)