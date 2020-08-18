from flask import Flask, render_template, request, redirect, url_for, session, Response, make_response, send_file
from news_api import getheadlines
#session is a special kind of dictionary that is accessible anywhere in the program
#even in the jinja without passing it explicitly
from model import save_user, user_exists, product_exists, add_product, products_list, remove_from_db, add_to_cart, cart_info, remove_from_cart, save_profile_image, fetch_profile_image
import base64, io

app = Flask(__name__)
app.secret_key = 'hello'


@app.route('/')
def home():
	return render_template('home.html', title = "Home")

@app.route('/about')
def about():
	return render_template('about.html', title = "About")

@app.route('/contact')
def contact():
	return render_template('contact.html', title = "Contact")

@app.route('/login', methods=['GET', 'POST'])
def login():
	
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		
		result = user_exists(username)

		if result:
				if result['password'] != password:
					return render_template('access_denied.html', error_msg = "Password doesn't match. Go back and re-renter the password")

				session['username'] = username
				session['c_type'] = result['c_type']
				return render_template('home.html')
		return render_template('access_denied.html', error_msg = "Username doesn't exist")
	return redirect('home.html')


@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		user_info = {}
		user_info['username'] = request.form['username']
		
		user_info['password'] = request.form['password1']
		password2 = request.form['password2']
		user_info['c_type'] = request.form['type']


		user_profile_image = {}
		user_profile_image['username'] = user_info['username']
		if 'profile_image' in request.files: 
					# The image will be stored in the request.files and not in request.form
			profile_image = base64.b64encode(request.files['profile_image'].read())
			user_profile_image['image'] = request.files['profile_image'].filename
			user_profile_image['data'] = profile_image
		
		user_info['profile_image'] = user_profile_image['image']

		if user_info['c_type'] == 'buyer':
			user_info['cart'] = []
			
		if user_exists(user_info['username']):
			return render_template('access_denied.html', error_msg = "Username already exist")

		if user_info['password'] != password2:
			return render_template('access_denied.html', error_msg = "Password doesn't match. Go back and re-renter the password")

		save_profile_image(user_profile_image)
		save_user(user_info)

	return redirect(url_for('home'))


@app.route("/add_product", methods=['GET', 'POST'])
def add():
	return render_template("add_product.html")

@app.route('/products', methods=['GET', 'POST'])
def products():
	if request.method == 'POST':
		product_info = {}
		product_info['name'] = request.form['name']
		product_info['price'] = int(request.form['price'])
		product_info['description'] = request.form['description']
		product_info['seller'] = session['username']

		if product_exists(product_info['name']):
			return "Product exists"

		add_product(product_info)
		return (redirect(url_for('products')))
	products = products_list()
	return render_template('products.html', products = products)



@app.route("/profile_image")
def retrieve_profile_image():
    image_binary = fetch_profile_image(session['username'])
    #response = make_response(image_binary)
    #response.headers.set('Content-Type', 'image/jpeg')
	#response.headers.set('Content-Disposition', 'attachment', filename='%s.jpg' % session['profile_image'])
    return send_file(
    io.BytesIO(image_binary),
    mimetype='image/jpeg',
    as_attachment=True,
    attachment_filename='%s.jpg' % session['profile_image'])

	

@app.route("/remove_products", methods=['GET', 'POST'])
def remove_products():
	if request.method == 'POST':
		name = request.form['name']
		remove_from_db(name)
		return redirect(url_for('products'))
	return redirect(url_for('products'))

@app.route("/cart", methods=['GET', 'POST'])
def cart():
	if request.method == 'POST':
		name = request.form['name']
		add_to_cart(name)
		return redirect(url_for('cart'))
	info = cart_info()
	return render_template('cart.html', products=info)
	

@app.route("/remove_from_cart", methods=['GET', 'POST'])
def remove_cart():
	if request.method == 'POST':
		name = request.form['name']
		remove_from_cart(name)
		return redirect(url_for('cart'))
	return redirect(url_for('cart'))


@app.route("/headline")
def get_news():
	headlines = getheadlines()
	
	if(headlines != None):
		return render_template('headlines.html', title = "News Headlines", headlines = headlines, totalheadlines = len(headlines))
	return render_template('headlines.html', title = "News Headlines", headlines = ["Cannot retrieve the news, Internet Not Connected"], totalheadlines = 1)

app.run(debug = True, port = 9999)