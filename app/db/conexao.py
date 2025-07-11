import psycopg2
from flask import current_app, flash

def conectar():
    try:
        conn = psycopg2.connect(
            dbname=current_app.config['DB_NAME'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT']
        )
        return conn
    except psycopg2.Error as e:
        flash(f"Erro ao conectar ao banco: {e}", "danger")
        return None
