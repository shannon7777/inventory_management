import peeweedbevolve # new; must be imported before models
import os
from flask import Flask, render_template, request, redirect, flash, url_for
from models import db, Store, Warehouse
import peewee as pw

app = Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET_KEY') or os.urandom(24)


@app.before_request
def before_request():
   db.connect()

@app.after_request
def after_request(response):
   db.close()
   return response

@app.cli.command() # new
def migrate(): # new 
   db.evolve(ignore_tables={'base_model'}) # new

@app.route("/")
def index():
   return render_template('index.html')

@app.route("/store", methods=['GET'])
def show():
    stores = Store.select()
    # stores= Store.select(Store, Warehouse, pw.fn.COUNT(Warehouse.id).filter(Warehouse.store_id == Store.id).alias("w_count")).join(Warehouse, join_type="left outer").group_by(Warehouse.id, Store.id).order_by(Store.id)
    return render_template('store.html', stores = stores)

#request.args = from URL
#request.form = from form
#request.files = from a file

@app.route("/store/create", methods=['POST'])
def create():
    store_name = request.form['store_name']
    # store_name = request.form.get('store_name') //this is a 'softcode' version of the code above
    store = Store(name=store_name)
    if store.save():
        flash('Successfully Created Store', "success")
        return redirect(url_for('show'))
    else:
        flash('failed to create store', "danger")
        return redirect(url_for('show'))
    # return render_template('store.html')

@app.route('/store/<id>/edit', methods=['GET'])
def edit(id):
    store = Store.get_by_id(id)
    return render_template('storeupdate.html', store = store)

@app.route('/store/<id>/update', methods=['POST'])
def update(id):
    store = Store.update(name = request.form['store_name']).where(Store.id == id)
    store_id = Store.get_by_id(id)
    if store.execute():
        flash('Succesfully updated store name!', 'success')
        return redirect(url_for('edit', store=store, id=store_id))
    else:
        flash('Failed to update store name :/', 'danger')
        return redirect(url_for('update'))


@app.route("/warehouse", methods=['GET'])
def show_warehouse():
    stores = Store.select()
    return render_template('warehouse.html', stores=stores)

@app.route("/warehouse/create", methods=['POST'])
def create_warehouse():
    location = request.form['location']
    store_id = Store.get(Store.name == request.form['store_name'])
    warehouse = Warehouse(location = location, store_id = store_id)

    if warehouse.save():
        flash('Succesfully created warehouse!', "success")
        return render_template('index.html')
    else:
        flash('Failed to create warehouse',"danger")
        return redirect(url_for('show_warehouse'))

@app.route("/store/<id>/delete", methods=['POST'])
def delete(id):
    store = Store.delete().where(Store.id == id)
    if store.execute():
        flash('Succesfully deleted store', "success")
        return redirect(url_for('show'))
    else:
        flash('Failed to delete store', "danger")
        return render_template('store.html')
    


if __name__ == '__main__':
    app.run()


