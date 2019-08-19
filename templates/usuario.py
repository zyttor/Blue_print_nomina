from flask import (
    Blueprint, render_template
)

bp = Blueprint('usuario', __name__)



@bp.route('/index')
def index():
    from app import mysql
    cur = mysql.get_db().cursor()
    cur.execute("""Select * from empresas """)
    data = cur.fetchall()
    print(data)
    return render_template('index.html')