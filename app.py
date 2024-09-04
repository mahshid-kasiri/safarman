import os
import imghdr
import uuid
from datetime import timedelta, datetime
from flask import (
    Flask, 
    flash, 
    redirect,
    render_template,
    request, 
    send_from_directory,
    url_for
)
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError 


app = Flask(__name__)

app.secret_key = "Youareabitch"
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png"]
app.config["UPLOAD_PATH"] = os.environ.get('UPLOAD_PATH')
print("UPLOAD PATH =", app.config["UPLOAD_PATH"])
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask.db"
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

"""
functions
"""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format != "jpeg" else "jpg")

"""
Models
"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    def __repr__(self):
        return '<User %r>' % self.username

class City(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    def __repr__(self):
        return '<City %r>' % self.name
    
class Post(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    pic = db.Column(db.String(140))


class Comment(db.Model):
    _N = 6
    _id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.String(150), db.ForeignKey('post._id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    parent = db.Column(db.Integer,  db.ForeignKey('comment._id'), nullable=True)
    replies = db.relationship(
        'Comment', backref=db.backref('parent_comment', remote_side=[_id]),
        lazy='dynamic')
    timestamp = db.Column(db.DateTime,
        nullable=False, unique=False, index=False,
        default=datetime.utcnow)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        prefix = self.parent.path + '.' if self.parent else ''
        self.path = prefix + '{:0{}d}'.format(self._id, self._N)
        db.session.commit()

    def level(self):
        return len(self.path) // self._N - 1

# class ParentComment(db.Model):
#     _id = db.Column(db.Integer, primary_key=True)
#     comment_id = db.Column(db.Integer, db.ForeignKey('comment._id'), nullable=False)
#     parent_id = db.Column(db.Integer, db.ForeignKey('comment._id'), nullable=False)

with app.app_context():
    db.create_all()



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = PostForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_post = Post()
        # uploaded_file = request.form["fileInput"]
        uploaded_file = form.pic.data
        filename = secure_filename(uploaded_file.filename)
        print("filename = ", filename)
        pic_path = os.path.join(app.config['UPLOAD_PATH'], filename)
        print("pic_path = ", pic_path)
        print("app.config['UPLOAD_PATH'] = ", app.config['UPLOAD_PATH'])
        uploaded_file.save(pic_path)
        new_post.pic = pic_path
        path_list = new_post.pic.split('backend\\')[1:]
        print("path_list = ", path_list)
        new_path = '/'.join(path_list)
        print("new_path = ", new_path)
    
        # Update the database
        new_post.pic = new_path
        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('city_posts_view'))
        except:
            return 'You cannot add this post!'
    posts_list = Post.query.order_by(Post._id).all()
    return render_template('profile.html', posts=posts_list, form=form)

@app.route('/comment')
def comment():
    return render_template('comment.html')

@app.route('/post/<int:id>/', methods=['GET', 'POST'])
def post_detail_view(id):
    post_obj = Post.query.get_or_404(id)
    comments_list = Comment.query.filter_by(post_id=post_obj._id).all()
    if request.method == 'POST':
        comment_user = current_user
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        comment_content = request.form['commentText']
        new_comment = Comment(
            user_id=comment_user.id, 
            post_id=post_obj._id, 
            content=comment_content
            )
        new_comment.save()
        print("content = ", new_comment.content)
        return redirect(url_for('post_detail_view', id=post_obj._id))
    return render_template("comment.html", post=post_obj, comments=comments_list)


# id for the comment we want to reply
@app.route('/reply/<int:id>', methods=['POST'])
def reply_comment(id):
    parent = Comment.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.path.asc())


    if request.method == 'POST':
        comment_user = current_user
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        comment_post = parent.post
        comment_content = request.form['content']
        comment = Comment(
            parent = parent,
            user_id=comment_user.id, 
            post_id=comment_post._id, 
            content=comment_content
        )

        comment.save()
        return redirect(url_for('post_detail_view', id=comment_post._id))

    

"""
Forms
"""
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    email = EmailField(validators=[InputRequired(), Length(max=50)], render_kw={"placeholder": "Email"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')
    
class PostForm(FlaskForm):
    pic = FileField('Picture', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Upload')


"""
Views
"""


@app.route('/travel')
def travel():
    return render_template('travel.html')


@app.route('/', methods=['POST', 'GET'])
def home_page():
    if request.method == "POST":
        city_name = request.form['name']
        new_city = City(name=city_name)
        print("new city = ", new_city)

        try:
            db.session.add(new_city)
            db.session.commit()
            return redirect('/')
        except:
            return "City cannot be submitted"
    else:
        cities_list = City.query.order_by(City._id).all()
        return render_template('home.html', cities=cities_list)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user_username = request.form["registerUsername"]
        existing_user = User.query.filter_by(username=new_user_username).first()
        if existing_user:
            raise ValidationError(".این نام کاربری قبلا در سایت ثبت شده است")
        new_user_email = request.form["registerEmail"]
        existing_user = User.query.filter_by(email=new_user_email).first()
        if existing_user:
            raise ValidationError(".این ایمیل قبلا در سایت ثبت شده است")
        new_user_password = request.form["registerPassword"]
        hashed_password = bcrypt.generate_password_hash(new_user_password)
        new_user = User(username=new_user_username, password=hashed_password, email=new_user_email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('profile'))
    users_list = User.query.order_by(User.id).all()
    return render_template('sign_up.html', users=users_list)  

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user_obj_username = request.form['username']
        user_obj_password = request.form['password']
        user = User.query.filter_by(username=user_obj_username).first()
        if user:
            if bcrypt.check_password_hash(user.password, user_obj_password):
                login_user(user)
                flash("Login Successful!")
                return redirect(url_for('profile'))
            else: 
                flash("Wrong Password!")
        else:
            flash("Username is incorrect!")
    
    return render_template('login.html') 
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))


@app.route('/posts/<city_name>', methods=['GET', 'POST'])
def city_posts_view(city_name):
    form = PostForm()
    if request.method == 'POST':
        # post_user = User.query.filter_by(username=request.form['username'])
        if form.validate_on_submit():
            post_city = City.query.filter_by(name=city_name).first()
            post_city_id = post_city._id
            new_post = Post(city_id=post_city_id, content=form.content.data)
            uploaded_file = form.pic.data
            filename = secure_filename(uploaded_file.filename)
            pic_path = os.path.join(app.config['UPLOAD_PATH'], filename)
            uploaded_file.save(pic_path)
            new_post.pic = pic_path
            path_list = new_post.pic.split('safarman')[1:]
            new_path = '/'.join(path_list)
        
            # Update the database
            new_post.pic = new_path
            try:
                db.session.add(new_post)
                db.session.commit()
                return redirect(url_for('city_posts_view', city_name=post_city.name))
            except:
                return 'You cannot add this post!'
    city_obj= City.query.filter_by(name=city_name).first()
    posts_list = City.query.filter_by(name=city_obj.name).first().posts
    return render_template('city/city_posts.html', form=form, city=city_obj, posts=posts_list)

# @app.route('/posts/<int:id>', methods=['POST', 'GET'])
# def post_detail_view(id):
#     post_obj = Post.query.get_or_404(id)
#     if request.method == 'POST':
#         comment_user = current_user
#         if not current_user.is_authenticated:
#             return redirect(url_for('login'))
#         comment_post = Post.query.get_or_404(id)
#         comment_content = request.form['content']
#         new_comment = Comment(user_id=comment_user.id, post_id=comment_post._id, content=comment_content)
#         try:
#             db.session.add(new_comment)
#             db.session.commit()
#             comments_list = Comment.query.filter_by(post_id=id).all()
#             return redirect(url_for('post_detail_view', id=comment_post._id))
#         except:
#             return 'You cannot add this comment!'
#     comments_list = Comment.query.filter_by(post_id=id).all()
#     return render_template('comment.html', post=post_obj, comments=comments_list)



@app.route('/delete/<int:id>')
def city_delete_view(id):
    city_obj = City.query.get_or_404(id)
    try:
        db.session.delete(city_obj)
        db.session.commit()
        return redirect('/')
    except:
        return "You cannot delete this city!"

@app.route('/detail/<int:id>', methods=['GET'])
def city_detail_view(id):
    city_obj = City.query.get_or_404(id)
    return render_template('city/city_detail.html', city=city_obj)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def city_update_view(id):
    city_obj = City.query.get_or_404(id)
    if request.method == "POST":
        city_obj.name = request.form['name']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'City cannot be updated'
    return render_template('pages/city_update.html', city=city_obj)


"""
API Views
"""
@app.route('/api/post/<int:id>/comments')
def city_comments_api_view(id):
    comments = Comment.query.filter_by(post_id=id).all()
    username = User.query.get_or_404(1).username
    serializer = [{"username": username, "content": comment.content} for comment in comments]
    return render_template('api/comment.html', comments=serializer)

if __name__ == '__main__':
    app.run(debug=True)