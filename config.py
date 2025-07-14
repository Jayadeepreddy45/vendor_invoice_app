class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/invoice_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
