from models import (Base, session, engine, Product)
import csv
import datetime
import time


def menu():
    while True:
        print('''
            \nSTORE INVENTORY
            \rV) View product
            \rA) Add product to database
            \rB) Back up database
            \rE) Exit app
        ''')
        choice = input("What do you want to do? ").lower()
        if choice in ['v', 'a', 'b', 'e']:
            return choice
        else:
            input('''
                \nPlease choose 'V', 'A', 'B' or 'E'
                \rPress enter to continue...  ''')

def view_product():
    id_list = []
    print('View product by Id')
    for product in session.query(Product):
        id_list.append(product.product_id)
    id_error = True
    while id_error:
        product_choice = input(f'''
            \nId Options: {id_list}
            \rProduct id:  ''')
        product_choice = clean_id(product_choice, id_list)
        if type(product_choice) == int:
            id_error = False
    product_to_show = session.query(Product).filter(Product.product_id==product_choice).first()
    input(f'''
        \nProduct: {product_to_show.product_name}
        \rPrice: ${product_to_show.product_price / 100}
        \rQuantity: {product_to_show.product_quantity}
        \rLast updated: {product_to_show.date_updated}
        \rPress any key to continue... ''')

def add_product():
    
    name = input('Product name: ')
    price_error = True
    while price_error:
        price = input('Price (ex: $x.xx): ')
        price = clean_price(price)
        if type(price) == int:
            price_error = False
    quantity_error = True
    while quantity_error:
        quantity = input('Quantity: ')
        quantity = clean_quantity(quantity)
        if type(quantity) == int:
            quantity_error = False
    date_error = True
    while date_error:
        date = input('Date Updated (ex: month/day/year): ')
        date = clean_date(date)
        if type(date) == datetime.date:
            date_error = False
    products = session.query(Product)
    product = session.query(Product).filter(Product.product_name==name).one_or_none()
    for i in products:
        if product == None:
            product_name = name
            product_price = price
            product_quantity = quantity
            date_updated = date
            new_product = Product(product_name=product_name, product_price=product_price, product_quantity=product_quantity, date_updated=date_updated)
            session.add(new_product)
            time.sleep(1.5)
            print('Product successfully added!')
            break
        elif product and product.date_updated <= date:
            product.date_updated = date
            product.product_price = price
            product.product_quantity = quantity
            print("Product updated!")
            backup_csv()
            break
        else:
            break
    session.commit()


def backup_csv():
    header = ['product_name', 'product_price', 'product_quantity', 'date_updated']
    data = session.query(Product.product_name, Product.product_price, Product.product_quantity, Product.date_updated).all()
    with open('backup.csv', 'w', newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(data)
    print('Database successfully backed up!')
    time.sleep(1.5)

def clean_date(date_str):
    try:
        date_list = date_str.split('/')
        month = int(date_list[0])
        day = int(date_list[1])
        year = int(date_list[2])
    except (IndexError, ValueError):
        input('''
            \nInvalid Date!
            \rPlease enter a valid date!
            \rUse month/day/year format. Ex: MM/DD/YYYY
            \rPress any key to continue... ''')
        return
    else:
        return datetime.date(year, month, day)

def clean_price(price_str):
    try:
        price_list = price_str.split('$')
        price_float = float(price_list[1])
    except (ValueError, IndexError, OverflowError):
        input('''
            \n*Invalid Price!
            \rPlease enter a valid price!
            \rUse $1.99 format. Ex: $1.11
            \rPress any key to continue...  ''')
        return
    else:
        return int(price_float * 100)

def clean_quantity(quantity):
    try:
        quantity = int(quantity)
    except (ValueError, OverflowError):
        input('''
            \nInvalid Quantity!
            \rPlease enter an whole number.
            \rEx: 10
            \rPress any key to continue...  ''')
        return
    else:
        return int(quantity)

def clean_id(id_str, id_options):
    try:
        product_id = int(id_str)
    except (ValueError, OverflowError):
        input('''
            \nInvalid ID!
            \rInvalid entry please enter an integer (whole number)
            \rPress any key to try again...
            \r*******************''')
        return
    else:
        if product_id in id_options:
            return product_id
        else:
            input(f'''
                \nInvalid ID!
                \rPlease enter a valid optiion {id_options}.
                \rPress any key to continue...  ''')
            return

def check_product(name_str):
    name_list = []
    products = session.query(Product)
    for product in products:
        name_list.append(product.product_name)
    if name_str in name_list:
        return True
    else:
        return False

def add_csv():
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        next(csvfile)
        for row in data:
            product_in_db = session.query(Product).filter(Product.product_name==row[0]).one_or_none()
            if product_in_db == None:
                product_name = row[0]
                product_price = clean_price(row[1])
                product_quantity = clean_quantity(row[2])
                date_updated = clean_date(row[3])
                new_product = Product(product_name=product_name, product_price=product_price, product_quantity=product_quantity, date_updated=date_updated)
                session.add(new_product)
            elif product_in_db and product_in_db.date_updated <= clean_date(row[3]):
                product_in_db.date_updated = clean_date(row[3])
                product_in_db.product_price = clean_price(row[1])
                product_in_db.product_quantity = clean_quantity(row[2])
        session.commit()

def app():
    app_running = True
    while app_running:
        choice = menu()
        if choice == 'v':
            view_product()
        elif choice == 'a':
            add_product()
        elif choice == 'b':
            backup_csv()
        else:
            print("See Ya Later!")
            app_running = False

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_csv()
    app()