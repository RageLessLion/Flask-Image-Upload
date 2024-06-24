# Flask Image Upload Application

This Flask application allows the users to categorize and view images sorted by categories on the main page. Additionally, it provides an admin page where administrators can add/delete images and categories. The delete functionality for categories is implemented using fetch.

- **Image Upload**: Admin user can upload images to the server.
- **Main Page**: Displays images sorted by categories.
- **Admin Page**: Allows administrators to manage images and categories (add/delete).
- **Delete Categories with Fetch**: Categories can be deleted dynamically using fetch requests.


When it comes to the database , there are 3 tables used . A user table that has a one to many towards the image table and the image table that has a one to many towards the category table (Mysql + SqlAlchemy as ORM were used) 

the credentuials for the the database need to be changed in database.py here :
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/image_gallery'
