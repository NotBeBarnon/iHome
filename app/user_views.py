import os
import re


from flask import request, render_template, jsonify, Blueprint, session
from werkzeug.security import generate_password_hash, check_password_hash


from app.models import User, db
from utils.settings import MEDIA_PATH

user_blue = Blueprint('user', __name__)


@user_blue.route('/register/', methods=['GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')


@user_blue.route('/register/', methods=['POST'])
def my_register():
    if request.method == 'POST':
        username = request.form.get('username')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        user = User.query.filter(User.phone == mobile).first()
        # 校验信息
        tel = re.compile('^0\d{2,3}\d{7,8}$|^1[358]\d{9}$|^147\d{8}')
        if not re.fullmatch(tel, mobile):
            return jsonify({'code': 1003, 'msg': '手机号格式不对'})
        if user:
            return jsonify({'code': 1004, 'msg': '这个手机号已被注册'})
        if password != password2:
            return jsonify({'code': 1004, 'msg': '两次密码不一致'})

        user = User()
        user.name = username
        user.phone = mobile
        user.pwd_hash = generate_password_hash(password)
        user.add_update()
        return jsonify({'code': 200, 'msg': '注册成功'})


@user_blue.route('/login/', methods=['GET'])
def login():
    # form = UserRegisterForm()
    if request.method == 'GET':
        return render_template('login.html')


@user_blue.route('/login/', methods=['POST'])
def my_login():
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        user = User.query.filter(User.phone == mobile).first()
        if not user:
            return jsonify({'code': 1005, 'msg': '该手机号未注册'})
        if not check_password_hash(user.pwd_hash, password):
            return jsonify({'code': 1006, 'msg': '密码不正确'})

        session['user_id'] = user.id
        return jsonify({'code': 200, 'msg': '登陆成功'})


@user_blue.route('/my_info/', methods=['GET'])
def my_info():
    if request.method == 'GET':
        user_id = session.get('user_id')
        if not user_id:
            return render_template('login.html')
        return render_template('my.html')


@user_blue.route('/my_info_min/', methods=['GET'])
def my_info_min():
    if request.method == 'GET':
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        user_avatar = user.avatar
        return jsonify({'code': 1007, 'user_name': user.name, 'user_phone': user.phone, 'user_avatar': user_avatar})


@user_blue.route('/profile/')
def profile():
    if request.method == 'GET':
        user_id = session.get('user_id')
        if not user_id:
            return render_template('login.html')
        return render_template('profile.html')


@user_blue.route('/fix_avatar/', methods=['POST'])
def fix_avatar():
    if request.method == 'POST':
        avatar = request.files.get('avatar')
        avatar_path = os.path.join(MEDIA_PATH, avatar.filename)
        avatar.save(avatar_path)
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        user.avatar = "/static/media/" + avatar.filename
        user.add_update()
        return jsonify({'code': 200})


@user_blue.route('/fix_username/', methods=['POST'])
def fix_username():
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        user.name = new_username
        db.session.add(user)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '修改成功  '})


@user_blue.route('/logout/')
def logout():
    if request.method == 'GET':
        session.clear()
        return jsonify({'code': 200})


@user_blue.route('/auth/')
def auth():
    if request.method == 'GET':
        return render_template('auth.html')


@user_blue.route('/my_auth/')
def my_auth():
    if request.method == 'GET':
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        # user.
        real_name = user.id_name
        id_card = user.id_card
        return jsonify({'code': 200, 'msg': '修改成功', 'real_name': real_name, 'id_card': id_card})


@user_blue.route('/auth/', methods=['POST'])
def fix_auth():
    if request.method == 'POST':
        real_name = request.form.get('real_name')
        id_card = request.form.get('id_card')
        # 姓名校验
        name_test = re.compile('[\u4e00-\u9fa5]{2,4}')
        result = re.fullmatch(name_test, real_name)
        # 身份证号校验
        id_card_test = re.compile("^[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$")
        result2 = re.fullmatch(id_card_test, id_card)
        if not result:
            return jsonify({'code': 1008, 'msg': '姓名输入不合法'})

        if not result2:
            return jsonify({'code': 1009, 'msg': '身份证号输入不合法'})

        user = User.query.filter_by(id_card=id_card).first()
        if user:
            return jsonify({'code': 1010, 'msg': '该身份证号已经被注册'})

        user_id = session.get('user_id')
        user = User.query.get(user_id)
        user.id_name = real_name
        user.id_card = id_card
        user.add_update()
        return jsonify({'code': 200, 'msg': '修改成功  '})







