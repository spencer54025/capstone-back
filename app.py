from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
# import os

app = Flask(__name__)
CORS(app)

# basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jjirsyzkowwrcx:a89361f80f7352158f85fd8841fa8f5dc35c7594bb93a49102efdbcf9d1e3d0d@ec2-3-228-235-79.compute-1.amazonaws.com:5432/daiabcc4gkelqr'


db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    user_type = db.Column(db.String)
    # cart = db.relationship('Cart', backref='user', cascade='all, delete, delete-orphan')

    def __init__(self, username, password, email, user_type):
        self.username = username
        self.password = password
        self.email = email
        self.user_type = user_type

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password', 'email', 'user_type')

user_schema = UserSchema()
multi_user_schema = UserSchema(many=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    summary = db.Column(db.String)
    author = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String)
    img = db.Column(db.String, nullable=False)

    def __init__(self, title, summary, author, price, genre, img):
        self.title = title
        self.summary = summary
        self.author = author
        self.price = price
        self.genre = genre
        self.img = img

class BookSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'summary', 'author', 'price', 'genre', 'img')

book_schema = BookSchema()
multi_book_schema = BookSchema(many=True)

# class Cart(db.Model):
#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     items = db.Column(db.PickleType)
#     user_id = db.relationship(db.Integer, db.ForeignKey('user.id'), nullable=False)

#     def __init__(self, items, user_id):
#         self.items = items
#         self.user_id = user_id

# class CartSchema(ma.Schema):
#     class Meta:
#         fields = ('id', 'items', 'user_id')

# cart_schema = CartSchema()



# user routes
@app.route('/users/get', methods=["GET"])
def get_users():
    users = db.session.query(User).all()
    return jsonify(multi_user_schema.dump(users))


@app.route('/signup', methods=["POST"])
def add_user():
    if request.content_type != 'application/json':
        return jsonify('data must be json')

    
    user_data = request.get_json()

    username = user_data.get('username')
    password = user_data.get('password')
    email = user_data.get('email')
    user_type = user_data.get('user_type')

    existing_user_check = db.session.query(User).filter(User.username == username).first()
    existing_email_check = db.session.query(User).filter(User.email == email).first()
    if existing_user_check is not None:
        return('please pick a different username')
    elif existing_email_check is not None:
        return('please choose a different email')

    new_user = User(username, password, email, user_type)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(user_schema.dump(new_user))

@app.route('/delete/user/<id>', methods=["DELETE"])
def delete_user(id):
    user = db.session.query(User).filter(User.id == id).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify('that user has vanished')

@app.route('/user/update/<username>/<email>', methods=["PUT"])
def update_user(username, email):
    if request.content_type != 'application/json':
        return jsonify('data must be json')

    user = db.session.query(User).filter(User.username == username).filter(User.email == email).first()

    if user != None:
        updated_data = request.get_json()
        password = updated_data.get('password')

        user_to_update = db.session.query(User).filter(User.username == username).first()

        if password != None:
            user_to_update.password = password

        db.session.commit()
        return jsonify(book_schema.dump(user_to_update), 'user was updated')
    else:
        return jsonify('user was not found')

@app.route('/user/verify', methods=["POST"])
def verification():
    if request.content_type != 'application/json':
        return jsonify('send it as json')
    
    post_data = request.get_json()
    username = post_data.get('username')
    password = post_data.get('password')

    user = db.session.query(User).filter(User.username == username).first()

    if user == None:
        return jsonify('user was not verified')

    elif username == user.username and password == user.password:
        return jsonify('user was verified', user.id, user.user_type, user.username)
    else:
        return jsonify('user was not verified')

# books routes

@app.route('/book/add', methods=["POST"])
def add_book():
    if request.content_type != 'application/json':
        return jsonify('content must be json')
    
    book_data = request.get_json()

    title = book_data.get('title')
    summary = book_data.get('summary')
    author = book_data.get('author')
    price = book_data.get('price')
    genre = book_data.get('genre')
    img = book_data.get('img')

    new_book = Book(title, summary, author, price, genre, img)
    db.session.add(new_book)
    db.session.commit()

    return jsonify(book_schema.dump(new_book))


@app.route('/books/add', methods=["POST"])
def add_books():
    if request.content_type != 'application/json':
        return jsonify('content must be json')
    post_data = request.get_json()
    books = post_data.get("books")

    new_records = []

    for book in books:
        title = book.get('title')
        summary = book.get('summary')
        author = book.get('author')
        price = book.get('price')
        genre = book.get('genre')
        img = book.get('img')

        new_record = Book(title, summary, author, price, genre, img)
        db.session.add(new_record)
        db.session.commit()
        new_records.append(new_record)

    return jsonify(multi_book_schema.dump(new_records))

@app.route('/books/get', methods=["GET"])
def get_books():
    books = db.session.query(Book).all()
    return jsonify(multi_book_schema.dump(books))

@app.route('/book/get/<id>', methods=["GET"])
def get_book(id):
    book = db.session.query(Book).filter(Book.id == id).first()
    return jsonify(book_schema.dump(book))

@app.route('/book/delete/<id>', methods=["DELETE"])
def delete_book(id):
    book = db.session.query(Book).filter(Book.id == id).first()
    db.session.delete(book)
    db.session.commit()
    return jsonify('that book has vanished')

@app.route('/update/book/<id>', methods=["PUT"])
def update_book(id):
    if request.content_type != 'application/json':
        return jsonify('data must be json')

    updated_data = request.get_json()
    title = updated_data.get('title')
    summary = updated_data.get('summary')
    author = updated_data.get('author')
    price = updated_data.get('price')
    genre = updated_data.get('genre')
    img = updated_data.get('img')

    book_to_update = db.session.query(Book).filter(Book.id == id).first()

    if title != None:
        book_to_update.title = title
    if summary != None:
        book_to_update.summary = summary
    if author != None:
        book_to_update.author = author
    if price != None:
        book_to_update.price = price
    if genre != None:
        book_to_update.genre = genre
    if img != None:
        book_to_update.img = img


    db.session.commit()
    return jsonify(book_schema.dump(book_to_update))


# cart endpoints

# @app.route('/cart/create', methods=["POST"])
# def create_cart():
#     if request.content_type != 'application/json':
#         return jsonify('data must be json')
#     post_data = request.get_json()

#     items = {}
#     user_id = post_data.get('user_id')

#     new_user = User(items, user_id)
#     db.session.add(new_user)
#     db.session.commit()

#     return jsonify(cart_schema.dump(new_user))

# @app.route('/cart/add-item/<user_id>', methods=["PUT"])
# def add_item_cart(user_id):
#     cart = db.session.query(Cart).filter(Cart.user_id == user_id).first()
#     items_in_cart = db.session.query(Cart).filter(Cart.user_id == user_id).filter(Cart.items).first()
#     return jsonify(items_in_cart.append(item))

# @app.route('/cart/remove-item/<user_id>/<item>')
# def remove_item(user_id, item):




if __name__ == '__main__':
    app.run(debug=True)