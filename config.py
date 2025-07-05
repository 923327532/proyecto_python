import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        user="postgres",
        password="ailynmedina",
        dbname="banco_db"
    )

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'roberto.lopez@tecsup.edu.pe'
MAIL_PASSWORD = 'lhdr owxq xtns idcv'
