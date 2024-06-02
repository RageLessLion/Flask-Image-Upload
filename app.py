import os

from flask import Flask, render_template, url_for, flash, redirect, request, current_app, abort, make_response
from flask import session
from wtforms.fields.choices import SelectField

from forms import LoginForm, RegistrationForm, UploadForm, photos
from database import User, app, db, Image, Category
from middleware import AdminRequired
from flask import jsonify
from flask_wtf.csrf import generate_csrf


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.password == form.password.data:
                session['username'] = form.username.data
                if user.is_admin == 1:
                    return redirect(url_for('access_gallery'))
                else:
                    return redirect('/')
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        else:
            flash('Account does not exist.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/access_gallery", methods=['GET'])
@AdminRequired
def access_gallery():
    form = UploadForm()
    images = Image.query.all()
    categories = Category.query.all()
    csrf_token = generate_csrf()
    session['csrf_token'] = csrf_token
    return render_template('access_gallery.html', form=form, images=images, categories=categories,
                           csrf_token=csrf_token)


@app.route("/", methods=['GET'])
def view_gallery():
    images = Image.query.all()
    categories = Category.query.all()
    username = session.get('username')  # Use get method to avoid KeyError
    user = User.query.filter_by(username=username).first()
    logged_in = 1 if user else 0  # Check if user exists
    is_admin = user.is_admin if user else 0  # Check if user is admin
    return render_template("view_gallery.html", images=images, categories=categories, is_admin=is_admin,
                           logged_in=logged_in)


@app.route("/delete_image/<int:image_id>", methods=['POST'])
@AdminRequired
def delete_image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        flash('Image not found', 'error')
        return redirect(url_for('access_gallery'))
    db.session.delete(image)
    db.session.commit()
    flash('Image successfully deleted', 'success')
    try:
        os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], image.filename))
        flash('Image successfully deleted', 'success')
    except OSError:
        flash('Error while deleting image file', 'error')
    return redirect(url_for('access_gallery'))


@app.route("/upload", methods=['GET', 'POST'])
@AdminRequired
def upload_image():
    form = UploadForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]  # Populate category choices

    if request.method == 'POST' and form.validate_on_submit():
        file = form.photo.data
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
            user = User.query.filter_by(username=session['username'], is_admin=True).first()
            if user:
                existing_image = Image.query.filter_by(filename=filename, user_id=user.id).first()
                if existing_image is None:
                    try:
                        file.save(file_path)
                        category_id = form.category.data
                        name = form.name.data
                        new_image = Image(filename=filename, user_id=user.id, category_id=category_id, name=name)
                        db.session.add(new_image)
                        db.session.commit()
                        flash("Photo saved and added to database", "success")
                        return redirect(url_for('access_gallery'))
                    except Exception as e:
                        db.session.rollback()
                        flash(f"An error occurred while saving the image: {str(e)}", "danger")
                        return redirect(url_for('access_gallery'))
                else:
                    flash("Image path already exists in the database", "warning")
                    return redirect(url_for('access_gallery'))
            else:
                flash("Unauthorized user", "danger")
                abort(401)
        else:
            flash("No file uploaded", "warning")
            return redirect(url_for('access_gallery'))
    else:
        if request.method == 'POST':
            flash("Form validation failed", "warning")

    return render_template('access_gallery.html', form=form)


@app.route("/delete_category", methods=['POST'])
@AdminRequired
def delete_category():
    category_id = request.args.get('id')

    category = Category.query.get(category_id)
    print(category.name)
    if category is None:
        flash('Category not found', 'error')
        return redirect(url_for('access_gallery'))

    db.session.delete(category)
    db.session.commit()
    flash('Category successfully deleted', 'success')
    return redirect(url_for('access_gallery'))


@app.route("/add_category", methods=['POST'])
@AdminRequired
def add_category():
    category_name = request.form.get('new_category')
    if category_name is None:
        flash('No category name provided', 'error')
        return redirect(url_for('access_gallery'))

    existing_category = Category.query.filter_by(name=category_name).first()
    if existing_category is not None:
        flash('Category already exists', 'error')
        return redirect(url_for('access_gallery'))

    new_category = Category(name=category_name)
    db.session.add(new_category)
    db.session.commit()
    flash('Category successfully added', 'success')
    return redirect(url_for('access_gallery'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
