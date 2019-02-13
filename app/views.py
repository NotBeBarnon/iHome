

from flask import Blueprint, request, jsonify, render_template, session

from app.models import User, House, Area

blue = Blueprint('app', __name__)


@blue.route('/index/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')


@blue.route('/my_index/', methods=['GET'])
def my_index():
    # form = UserRegisterForm()
    if request.method == 'GET':
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()

        # house = House.query.limit(3).all()
        house = []
        for hou in House.query.limit(3).all():
            hou_id = hou.id
            hou_title = hou.title
            hou_img = hou.index_image_url
            house.append({'house_id': hou_id, 'house_title': hou_title, 'house_img': hou_img})

        areas_list = []
        areas = Area.query.all()
        for area in areas:
            areas_list.append(area.to_dict())

        if user.name:
            return jsonify({'code': 200, 'user_name_mobile': user.name, 'houses': house, 'areas_list': areas_list})
        else:
            return jsonify({'code': 200, 'user_name_mobile': user.phone, 'houses': house, 'areas_list': areas_list})


@blue.route('/search/', methods=['GET'])
def search():
    if request.method == 'GET':
        return render_template('search.html')


@blue.route('/search_info/', methods=['POST', 'GET'])
def search_info():
    if request.method == 'POST':
        session['area_id'] = request.form.get('area_id')
        session['days'] = request.form.get('days')
        return jsonify({'code': 200, 'msg': '接受数据成功'})
    if request.method == 'GET':
        area_id = session.get('area_id')
        days = session.get('days')
        houses = House.query.filter((House.area_id == area_id) and (days >= House.min_days) and (days <= House.max_days)).all()
        hous = []
        for house in houses:
            hous.append(house.to_full_dict())
        if not houses:
            return jsonify({'code': 1112, 'msg': '没有搜索到该条件下的房源'})

        return jsonify({'code': 200, 'msg': '获取房源成功', 'houses': hous})

# @blue.route('/search_main/', methods=['GET','POST'])
# def search_main():
#     if request.method == 'POST':
