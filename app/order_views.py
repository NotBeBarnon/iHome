import random

from flask import Blueprint, request, render_template, session, jsonify

from app.models import House, Order

order_blue = Blueprint('order', __name__)


@order_blue.route('/booking/<int:id>', methods=['GET'])
def booking(id):
    if request.method == 'GET':
        session['house_id'] = id
        return render_template('booking.html')


@order_blue.route('/booking_info/', methods=['GET'])
def booking_info():
    if request.method == 'GET':
        house_id = session.get('house_id')
        house = House.query.get(house_id)
        house_title = house.title
        house_price = house.price
        house_img = house.index_image_url
        return jsonify({'code': 200, 'msg': '返回数据成功', 'house_title': house_title, 'house_price': house_price, 'house_img': house_img})


@order_blue.route('/orders/', methods=['GET'])
def orders():
    if request.method == 'GET':
        return render_template('orders.html')


@order_blue.route('/orders_info/', methods=['GET', 'POST'])
def orders_info():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        # order_amount = request.form.get('order_amount')
        days_amount = request.form.get('days_amount')

        house_id = session.get('house_id')
        user_id = session.get('user_id')
        house = House.query.get(house_id)

        order = Order()
        order.user_id = user_id
        order.house_id = house_id
        order.begin_date = start_date
        order.end_date = end_date
        days = int(float(days_amount)/house.price)
        # 判断days是否大于规定的
        if days > house.max_days or days < house.min_days:
            return jsonify({'code': 1111, 'msg': '日期有误，请重新选择！'})

        order.days = days
        order.house_price = house.price
        order.amount = days_amount
        order.add_update()
        session['order_id'] = order.id
        return jsonify({'code': 200, 'msg': '接收数据成功'})

    if request.method == 'GET':
        # 生成订单号
        seed = "1234567890abcdefghijklmnopqrstuvwxyz"
        sa = []
        for i in range(11):
            sa.append(random.choice(seed))
        order_num = ''.join(sa)
        order_id = session.get('order_id')
        order = Order.query.get(order_id)
        return jsonify({'code': 200, 'msg': '接收数据成功', 'order': order.to_dict(), 'order_num': order_num})


@order_blue.route('/orders_comment/', methods=['POST'])
def orders_comment():
    if request.method == 'POST':
        # 保存评论
        comment = request.form.get('comment')
        order_id = session.get('order_id')
        order = Order.query.get(order_id)
        order.comment = comment
        order.add_update()
        return jsonify({'code': 200, 'msg': '接收数据成功'})


