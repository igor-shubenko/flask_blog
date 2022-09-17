from flask import Blueprint
from flask import request, render_template, redirect, session, flash, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import AdminLoginForm, AddPostForm, AddFileForm
from .admin_db_worker import AdminDBWorker
from werkzeug.utils import secure_filename
import os

admin = Blueprint('admin', __name__, static_folder='static', template_folder='templates')

menu = [['Головна', 'index'], ['Статті', 'posts'], ['Про сайт', 'about'],
        ["Зворотній зв'язок", 'contact'], ]

def admin_logged():
    return True if session.get('admin_logged') else False

def admin_login(admin_name):
    session['userLogged'] = admin_name
    session['admin_logged'] = 1

def admin_logout():
    session.pop('userLogged')
    session.pop('admin_logged')

dbase = None
@admin.before_request
def before_request():
    global dbase
    db = g.get('link_db')
    dbase = AdminDBWorker(db)

@admin.teardown_request
def teardown_request(request):
    global dbase
    dbase = None
    return request

@admin.route('/')
def index():
    if admin_logged() == False:
        return redirect(url_for('.login'))
    return redirect(url_for('index'))

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if admin_logged() == True:
        return redirect(url_for('index'))
    form = AdminLoginForm()
    if request.method == 'POST':
        if dbase.check_admin_exist() == False:
            psw_hash = generate_password_hash(form.password.data)
            admin_name = form.admin_name.data
            dbase.add_admin(admin_name, psw_hash)
            admin_login(form.admin_name.data)
            return redirect(url_for('index'))
        else:
            if dbase.get_admin_name() != form.admin_name.data:
                flash("Невірне ім'я", category='error')
            elif not check_password_hash(dbase.get_admin_psw_hash(), form.password.data):
                flash('Неправильний пароль', category='error')
            else:
                admin_login(form.admin_name.data)
                return redirect(url_for('index'))
    return render_template('admin_panel/login.html', form=form, title="Вхід", menu=menu)

@admin.route('/logout')
def logout():
    admin_logout()
    return redirect(url_for('.login'))

@admin.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if admin_logged() == False:
        return redirect(url_for('.login'))
    form = AddPostForm()
    if request.method == 'POST':
        title = form.title.data
        slug = form.slug.data
        text = form.text.data
        if dbase.check_post_slug(slug) == False:
            flash('Такий слаг вже існує', category='error')
        else:
            dbase.add_post(title, slug, text)
            flash('Стаття опублікована', category='success')
            return redirect(url_for('posts'))
    return render_template('admin_panel/add_post.html', form=form, title='Додати статю', menu=menu)

@admin.route('/edit_post/<post_slug>', methods=['GET', 'POST'])
def edit_post(post_slug):
    if admin_logged() == False:
        return redirect(url_for('.login'))
    form = AddPostForm()
    uploadform = AddFileForm()
    if request.method != 'POST':
        post = dbase.get_post(post_slug)[0]
        form.title.data = post['title']
        form.slug.data = post['post_slug']
        form.text.data = post['post_text']
        return render_template('admin_panel/edit_post.html', form=form, uploadform=uploadform, menu=menu, title='Редагування посту')
    else:
        title = form.title.data
        slug = post_slug
        text = form.text.data
        dbase.edit_post(title, slug, text)
        flash('Стаття змінена', category='success')
        return redirect(url_for('post', post_slug=post_slug))


@admin.route('/upload/<post_slug>', methods=['GET', 'POST'])
def uploader(post_slug):
    if admin_logged() == False:
        return redirect(url_for('.login'))
    uploadform = AddFileForm()
    if request.method == 'POST':
        filename = secure_filename(uploadform.fileinput.data.filename)
        try:
            os.mkdir(f'static/images/{post_slug}')
        except FileExistsError:
            pass
        uploadform.fileinput.data.save(f'static/images/{post_slug}/' + filename)
        flash('Завантажено', category='success')
        return redirect(request.referrer)

@admin.route('/feedbacks')
def feedbacks():
    if admin_logged() == False:
        return redirect(url_for('.login'))
    return render_template('admin_panel/feedbacks.html', menu=menu, title='Feedbacks', feedbacks=dbase.get_all_feedbacks())