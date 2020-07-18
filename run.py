from getirwapp import app, db
from getirwapp.models import User, Product, Promotion

if __name__ == '__main__':
    print(User.query.all())
    print(Product.query.all())
    app.run(debug=True)