from flask_mysqldb import MySQL

mysql = MySQL()

def init_db(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root' 
    app.config['MYSQL_PASSWORD'] = ''  
    app.config['MYSQL_DB'] = 'secure_api'  
    mysql.init_app(app)


if __name__ == "__main__":
    from flask import Flask  
    
    app = Flask(__name__)  
    init_db(app)  

    with app.app_context():
        try:
            conn = mysql.connection
            print("✅ Database connection successful!")
        except Exception as e:
            print("❌ Database connection failed:", str(e))