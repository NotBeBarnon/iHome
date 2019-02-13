import os

from flask import Blueprint, request, render_template, session, jsonify, json

from app.models import User, Facility, Area, House, HouseImage, ihome_house_facility, db
from utils.settings import MEDIA_PATH

house_blue = Blueprint('house', __name__)


@house_blue.route('/myhouse/', methods=['GET'])
def myhouse():
    if request.method == 'GET':
        return render_template('myhouse.html')


@house_blue.route('/myhouse_info/', methods=['GET'])
def myhouse_info():
    if request.method == 'GET':
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        real_name = user.id_name
        id_card = user.id_card
        if real_name and id_card:
            return jsonify({'code': 200, 'msg': '已经实名制'})
        return jsonify({'code': 1011, 'msg': '未实名制'})


@house_blue.route('/newhouse/', methods=['GET'])
def newhouse():
    if request.method == 'GET':
        return render_template('newhouse.html')


@house_blue.route('/newhouse_facility/', methods=['GET'])
def newhouse_facility():
    if request.method == 'GET':

        facs = Facility.query.all()
        dic_facs = []
        for fac in facs:
            dic_facs.append({'id': fac.id, 'name': fac.name})

        if not facs:
            return jsonify({'code': 1013, 'msg': '没数据'})
        return jsonify({'code': 200, 'msg': '返回数据成功', 'facs': dic_facs})


@house_blue.route('/newhouse_area/', methods=['GET'])
def newhouse_area():
    if request.method == 'GET':

        areas = Area.query.all()
        dic_areas = []
        for area in areas:
            dic_areas.append({'id': area.id, 'name': area.name})

        if not areas:
            return jsonify({'code': 1013, 'msg': '没数据'})
        return jsonify({'code': 200, 'msg': '返回数据成功', 'areas': dic_areas})
    

@house_blue.route('/add_newhouse/', methods=['POST'])
def add_newhouse():
    if request.method == 'POST':
        house_title = request.form.get('title')
        house_price = int(request.form.get('price'))
        area_id = int(request.form.get('area_id'))
        house_address = request.form.get('address')
        house_room_count = int(request.form.get('room_count'))
        house_acreage = int(request.form.get('acreage'))
        house_unit = request.form.get('unit')
        house_capacity = request.form.get('capacity')
        house_beds = request.form.get('beds')
        house_deposit = request.form.get('deposit')
        house_min_days = int(request.form.get('min_days'))
        house_max_days = int(request.form.get('max_days'))

        user_id = session.get('user_id')

        if not (house_title or house_price or area_id or house_address or
                house_room_count or house_acreage or house_unit or house_max_days or
                house_capacity or house_beds or house_deposit or house_min_days
                ):
            return jsonify({'code': 1014, 'msg': '请将信息填写完整'})
        if house_price <= 0:
            return jsonify({'code': 1015, 'msg': '请输入正确的价格'})
        if house_min_days <= 0 or house_max_days < 0:
            return jsonify({'code': 1017, 'msg': '请输入正确的入住天数'})
        if house_max_days != 0 and house_max_days < house_min_days:
            return jsonify({'code': 1017, 'msg': '请输入正确的入住天数'})

        house = House()
        house.user_id = user_id
        house.title = house_title
        house.price = house_price
        house.area_id = area_id
        house.address = house_address
        house.room_count = house_room_count
        house.acreage = house_acreage
        house.unit = house_unit
        house.capacity = house_capacity
        house.beds = house_beds
        house.deposit = house_deposit
        house.min_days = house_min_days
        house.max_days = house_max_days

        # 保存房屋设施到数据库
        house_facs_min = []
        house_facs = request.form.getlist('facility')
        for house_fac in house_facs:
            house_fac = int(house_fac)
            fac = Facility.query.get(house_fac)
            house_facs_min.append(fac)
        house.facilities = house_facs_min

        house.add_update()
        session['house_id'] = house.id
        house_id = house.id

    return jsonify({'code': 200, 'msg': '请输入正确的床位', 'house_id': house_id})


@house_blue.route('/add_house_image/', methods=['POST'])
def add_house_image():
    if request.method == 'POST':
        house_image = request.files.get('house_image')
        house_image_path = os.path.join(MEDIA_PATH, house_image.filename)
        house_image.save(house_image_path)
        house_id = session.get('house_id')
        house = House.query.get(house_id)
        image_url = '/static/media/' + house_image.filename
        # 主图存进house表
        if not house.index_image_url:
            house.index_image_url = image_url
            house.add_update()
        # 其他图存进house_image表
        houseimage = HouseImage()
        houseimage.house_id = house_id
        houseimage.url = image_url
        houseimage.add_update()
        return jsonify({'code': 200, 'msg': '图片保存成功'})


@house_blue.route('/my_house_list/', methods=['GET'])
def my_house_list():
    if request.method == 'GET':
        user_id = session.get('user_id')
        houses = House.query.filter(House.user_id == user_id).all()
        # 重新组装成字典类的列表
        houses_min = []
        for hou in houses:
            houses_min.append(hou.to_dict())

        if houses:
            return jsonify({'code': 200, 'msg': '返回房屋列表', 'houses': houses_min})
        return jsonify({'code': 1018, 'msg': '你没有发布房源'})


@house_blue.route('/house_detail/<int:id>/', methods=['GET'])
def house_detail(id):
    if request.method == 'GET':
        session['house_id'] = id
        return render_template('detail.html')


@house_blue.route('/detail_info/', methods=['GET'])
def detail_info():
    if request.method == 'GET':
        booking = 0
        house_id = session.get('house_id')
        house = House.query.get(house_id)
        user_id = session.get('user_id')
        if house.user_id == user_id:
            booking = 1
        house.to_full_dict()

        # house_images = HouseImage.query.filter(HouseImage.house_id == house_id).all()
        # imgs = []
        # for hu_im in house_images:
        #     house_pic = 'house_pic_' + str(hu_im.id)
        #     imgs.append({house_pic: hu_im.url})

        return jsonify({'code': 200, 'msg': '返回数据成功', 'house': house.to_full_dict(), 'booking': booking})












