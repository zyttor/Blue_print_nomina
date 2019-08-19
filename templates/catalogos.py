
import functools
from ast import dump

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('catalogos', __name__)


@bp.route('/c_nivel_estudio')
def c_nivel_estudio():
    from app import mysql
    cur = mysql.get_db().cursor()
    cur.execute("""Select * from nivel_estudios """)
    data = cur.fetchall()
    print(data)
    return render_template('catalogos/niveles_estudio.html', niveles=data)

