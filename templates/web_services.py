import decimal
import functools
import json
from ast import dump
from datetime import datetime, timedelta
import statistics


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    jsonify)
from flask_cors import CORS, cross_origin

from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('ws', __name__)

@bp.route('/ws_nivel')
@cross_origin(origin='*')
def get_Nivel_estudio():

    from app import mysql
    cur = mysql.get_db().cursor()
    cur.execute(""" call get_empresas()""" )
    data = cur.fetchall()

    cur_area = mysql.get_db().cursor()
    cur_area.execute("""call get_areas();""")
    areas = cur_area.fetchall()

    cur_tipo_nomino = mysql.get_db().cursor()
    cur_tipo_nomino.execute(""" call get_nominas(); """)
    nominas = cur_tipo_nomino.fetchall()

    return jsonify({'empresas': data,
                    'areas': areas,
                    'nominas': nominas})


@bp.route('/puestos_por_area',methods=['POST'])
@cross_origin(origin='*')
def get_puestos_area():

    data =None
    status = 'error'
    if request.method == 'POST':
        id = request.form['id_area']
        from app import mysql
        cur = mysql.get_db().cursor()
        cur.execute("""call get_puestos_by_area_empresa(%s)""", (id,))
        data = cur.fetchall()
        if len( data):
            status = 'exito'
        print('Estoy en POST')


    return jsonify({'resp': status,
                    'puestos': data})



@bp.route('/pedidos_por_articulo')
@cross_origin(origin='*')
def pedidos():
    fecha_ = datetime.now()
    fecha_.year
    from app import mysql
    cur = mysql.get_db().cursor()
    cur.execute("""call get_ventas_por_pedido ();""")
    data = cur.fetchall()
    c_data= []

    for i in data:
        c_data.append( [ i[0], i[1], str(i[2]) ])

    for i in c_data:
        print(type(i[1]))
    return jsonify({'productos': c_data} )


@bp.route('/porcentaje_articulo_por_pedido')
@cross_origin(origin='*')
def porcecntaje_pedidos():

    from app import mysql
    cur = mysql.get_db().cursor()
    cur.execute("""call get_porcentaje_ventas_por_articulo()""")
    data = cur.fetchall()
    c_data= []

    for i in data:
        c_data.append( [ i[0], i[1], str(i[2]) ])

    for i in c_data:
        print(type(i[1]))
    return jsonify({'productos': c_data} )


class DecimalEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)


@bp.route('/historico')
@cross_origin(origin='*')
def historial_por_anio():

    fecha_ = datetime.now()

    str_fecha_ini = str(fecha_.year) + '/01/01'
    str_fecha_fin = str(fecha_.year) + '/12/31'
    fecha_ini = datetime.strptime(str_fecha_ini, '%Y/%m/%d').date()
    fecha_fin = datetime.strptime(str_fecha_fin, '%Y/%m/%d').date()
    print(fecha_)

    print(fecha_ini)
    print(fecha_fin)

    from app import mysql
    cur = mysql.get_db().cursor()
    cur.execute("""call get_ventas_por_fechas(%s ,%s ) ;""" , (fecha_ini, fecha_fin))
    data = cur.fetchall()
    list = []
    for i in data:
        list.append(i[2])
    val_max = max(list)
    val_min = min(list)

    c_data = []

    for i in data:
        is_max=0
        is_min=0
        if i[2]==val_max:
            is_max=1
        if i[2]==val_min:
            is_min=1
        c_data.append([i[0], i[1], str(i[2]), is_max, is_min])



    return jsonify ( {'ventas': c_data,
                      'promedio': str(statistics.mean(list)),
                      'anio': fecha_.year} )


@bp.route('/ventas_anio_actual')
@cross_origin(origin='*')
def ventas_anio_actual():


    fecha_ = datetime.now()
    fecha_ini =  str(fecha_.year) +'/01/01'
    fecha_fin =  str(fecha_.year) +'/12/31'
    from app import mysql
    cur = mysql.get_db().cursor()
    cur.execute(""" call get_ventas_por_fechas(%s ,%s ) ; """, (fecha_ini, fecha_fin,)  )
    data = cur.fetchall()
    list = []
    for i in data:
        list.append(i[2])
    val_max = max(list)
    val_min = min(list)

    c_data = []

    for i in data:
        is_max = 0
        is_min = 0
        if i[2] == val_max:
            is_max = 1
        if i[2] == val_min:
            is_min = 1
        c_data.append([i[0], i[1], str(i[2]), is_max, is_min])


    return jsonify ( {'historico': c_data,'anio': fecha_.year} )



@bp.route('/ventas_fechas/<fecha_ini>/<fecha_fin>')
@cross_origin(origin='*')
def ventas_fechas(fecha_ini,fecha_fin):
    print('inicia')
    from app import mysql
    cur = mysql.get_db().cursor()
    cur.execute(""" call get_ventas_por_fechas(%s ,%s ) ; """, (fecha_ini, fecha_fin,))
    data = cur.fetchall()
    list = []
    for i in data:
        list.append(i[2])
    val_max = max(list)
    val_min = min(list)

    c_data = []

    for i in data:
        is_max = 0
        is_min = 0
        if i[2] == val_max:
            is_max = 1
        if i[2] == val_min:
            is_min = 1
        c_data.append([i[0], i[1], str(i[2]), is_max, is_min])


    print(fecha_ini)
    print(fecha_fin)

    return jsonify ( {'ventas':c_data,
                      'Fecha_ini': fecha_ini,
                      'Fecha_fin': fecha_fin} )


@bp.route('/historico_mes')
@cross_origin(origin='*')
def ventas_x_mes():

    fecha_ = datetime.now()
    list = []

    datetime_str = '2000/01/01 00:00:00'

    fecha_ = datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')

    list.append([str(fecha_.year) + '/01/01' , str(fecha_.year) + '/01/31' ]) #ene
    list.append([str(fecha_.year) + '/02/01', str(fecha_.year) + '/02/28'])#feb
    list.append([str(fecha_.year) + '/03/01', str(fecha_.year) + '/03/31'])#mar
    """
         list.append([str(fecha_.year) + '/04/01', str(fecha_.year) + '/04/30'])#abrl
    list.append([str(fecha_.year) + '/05/01', str(fecha_.year) + '/05/31'])#mayo
    list.append([str(fecha_.year) + '/06/01', str(fecha_.year) + '/06/30'])#juni
    list.append([str(fecha_.year) + '/07/01', str(fecha_.year) + '/07/31'])#jul
    list.append([str(fecha_.year) + '/08/01', str(fecha_.year) + '/08/31'])#ago
    list.append([str(fecha_.year) + '/09/01', str(fecha_.year) + '/09/30'])#sep
    list.append([str(fecha_.year) + '/10/01', str(fecha_.year) + '/10/31'])#oct
    list.append([str(fecha_.year) + '/11/01', str(fecha_.year) + '/11/30'])#nov
    list.append([str(fecha_.year) + '/12/01', str(fecha_.year) + '/12/31'])#dic
    """


    #call get_all_empresas()

    from app import mysql
    cur_sucursales = mysql.get_db().cursor()
    cur_sucursales.execute ("""call get_all_empresas()""")
    sucursales  = cur_sucursales.fetchall()

    list_historial=[]
    for sucursal in sucursales:
        his_suc=[]
        for i in list:
            db = mysql.get_db()
            cur_venta = db.cursor()
            cur_venta.execute(""" call get_ventas_por_fechas_y_sucursal(%s,%s,%s) ; """, (i[0], i[1], sucursal[0],))
            data = cur_venta.fetchall()
            c_data = []
            for j in data:


                c_data.append([sucursal[0],sucursal[1], j[0], j[1],j[2], str(j[3]),j[4]])

            his_suc.append(c_data)
            print(i)
            print(c_data )
        list_historial.append(his_suc)

    print('exit')
    return jsonify ( {'historico': list_historial,'ini':list[0][0], 'fin':list[2][1] } )



@bp.route('/hist_suc_fechas/<suc>/<fecha_ini>/<fecha_fin>')
@cross_origin(origin='*')
def hist_suc_fechas(suc,fecha_ini,fecha_fin):
    print('inicia')
    id= -1;
    error=[]
    from app import mysql

    cur = mysql.get_db().cursor()
    cur.execute("""select id_sucursal,nombre from sucursales where nombre =  %s;""" , (suc))
    id= cur.fetchall()[0][0]


    cur_empleados = mysql.get_db().cursor()
    cur_empleados.execute(""" select id_empleado from empleados where id_sucursal = %s """ , (id,))
    #cur_empleados.execute(""" select id_empleado from empleados where id_empleado  in (1,2)""")

    data_empleados = cur_empleados.fetchall()
    print(data_empleados)

    if id==-1:
        error.append("ID")
    print(id)

    list = []

    datetime_str = '2001/01/01 00:00:00'

    fecha_ = datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')

    list.append([str(fecha_.year) + '/01/01', str(fecha_.year) + '/01/31'])  # ene
    list.append([str(fecha_.year) + '/02/01', str(fecha_.year) + '/02/28'])  # feb
    list.append([str(fecha_.year) + '/03/01', str(fecha_.year) + '/03/31'])  # mar

    list.append([str(fecha_.year) + '/04/01', str(fecha_.year) + '/04/30'])#abrl
    list.append([str(fecha_.year) + '/05/01', str(fecha_.year) + '/05/31'])#mayo
    list.append([str(fecha_.year) + '/06/01', str(fecha_.year) + '/06/30'])#juni
    list.append([str(fecha_.year) + '/07/01', str(fecha_.year) + '/07/31'])#jul
    list.append([str(fecha_.year) + '/08/01', str(fecha_.year) + '/08/31'])#ago
    list.append([str(fecha_.year) + '/09/01', str(fecha_.year) + '/09/30'])#sep
    list.append([str(fecha_.year) + '/10/01', str(fecha_.year) + '/10/31'])#oct
    list.append([str(fecha_.year) + '/11/01', str(fecha_.year) + '/11/30'])#nov
    list.append([str(fecha_.year) + '/12/01', str(fecha_.year) + '/12/31'])#dic



    historico = []
    for id_empleado in data_empleados:
        historico_empleado =[]
        for i in list:
            #print((id_empleado[0] , i[0], ))
            cur_historico = mysql.get_db().cursor()
            cur_historico.execute("""call get_historial_empleados_suc_fecha(%s,%s , %s ); """,
                                  (id_empleado[0], i[0], i[1] , ))
            data= cur_historico.fetchall()
            c_data =[]

            for i in data:
                c_data.append([i[1],i[2],i[3],str(i[4])])
            historico_empleado.append(c_data)
        historico.append(historico_empleado)

    return jsonify ( {'ventas':historico,
                      'Fecha_ini': fecha_ini,
                      'Fecha_fin': fecha_fin,
                      'ID': id,
                      'suc':suc,
                      'error': error} )



@bp.route('/hist_suc_periodos/<fecha_ini>/<fecha_fin>/<dias>')
@cross_origin(origin='*')
def hist_suc_periodos_fechas(fecha_ini,fecha_fin,dias):
    print('inicia')
    print(type(dias))
    fecha_inicio = datetime.strptime(fecha_ini, '%Y-%m-%d')
    fecha_final = datetime.strptime(fecha_fin, '%Y-%m-%d')
    fecha_anterior = fecha_inicio
    print([fecha_inicio, fecha_final, dias])
    list_periodos = []
    print('---------------------')
    while(fecha_anterior < fecha_final ):
        list_periodos.append([fecha_anterior, fecha_anterior+timedelta(days=int(dias))])
        fecha_anterior =  fecha_anterior+timedelta(days=int(dias)+1)

    #for i in list_periodos:
    #    print(i)

    from app import mysql
    cur_sucursales = mysql.get_db().cursor()
    cur_sucursales.execute("""call get_all_empresas();""")
    data_empresas = cur_sucursales.fetchall()

    list_historial =[]
    for empresa in data_empresas:
        print(empresa)
        list_historial_empresa=[]
        for periodo in list_periodos:
            cur_periodo  = mysql.get_db().cursor()
            cur_periodo.execute("""call get_ventas_por_fechas_y_sucursal( %s , %s,%s);""", (periodo[0], periodo[1],
                                                                                            empresa[0],))
            data_periodos = cur_periodo.fetchall()
            list_temp =[]
            for dp in data_periodos:
                list_temp.append([dp[2], str(dp[3])])
            list_historial_empresa.append(list_temp)
        list_historial.append([empresa[0],empresa[1], list_historial_empresa])
    return jsonify ( {'ventas':list_historial,
                      'Fecha_ini': fecha_ini,
                      'Fecha_fin': fecha_fin} )

"""
nuevos filtross
"""

@bp.route('/historico_inicio')
@cross_origin(origin='*')
def ventas_inicio():

    fecha_ = datetime.now()
    list = []

    datetime_str = '2000/01/01 00:00:00'

    fecha_ = datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')

    list.append([str(fecha_.year) + '/01/01' , str(fecha_.year) + '/01/31' ]) #ene
    list.append([str(fecha_.year) + '/02/01', str(fecha_.year) + '/02/28'])#feb
    list.append([str(fecha_.year) + '/03/01', str(fecha_.year) + '/03/31'])#mar

    list.append([str(fecha_.year) + '/04/01', str(fecha_.year) + '/04/30'])#abrl
    list.append([str(fecha_.year) + '/05/01', str(fecha_.year) + '/05/31'])#mayo
    list.append([str(fecha_.year) + '/06/01', str(fecha_.year) + '/06/30'])#juni
    list.append([str(fecha_.year) + '/07/01', str(fecha_.year) + '/07/31'])#jul
    list.append([str(fecha_.year) + '/08/01', str(fecha_.year) + '/08/31'])#ago
    list.append([str(fecha_.year) + '/09/01', str(fecha_.year) + '/09/30'])#sep
    list.append([str(fecha_.year) + '/10/01', str(fecha_.year) + '/10/31'])#oct
    list.append([str(fecha_.year) + '/11/01', str(fecha_.year) + '/11/30'])#nov
    list.append([str(fecha_.year) + '/12/01', str(fecha_.year) + '/12/31'])#dic



    #call get_all_empresas()

    from app import mysql
    cur_sucursales = mysql.get_db().cursor()
    cur_sucursales.execute ("""call get_all_empresas()""")
    data_sucursales  = cur_sucursales.fetchall()

    list_empreas =[]

    for  i  in data_sucursales:
        list_empreas.append(i)

    list_historico =[]
    for i in list:
        cur_his  = mysql.get_db().cursor()
        cur_his.execute("""call get_ventas_por_fechas( %s , %s );""", (i[0],i[1]))
        data = cur_his.fetchall()
        for j in data:

            for empresa in range(0,len(list_empreas)):
                if list_empreas[ empresa] [0] == j[0]:
                    list_historico.append([i[0],i[1],[j[0], j[1], str(j[2])]])



    list_json = []
    for i in list_empreas:
        historial_empresa = []
        for j in list_historico:
            if i[0]== j[2][0]:
                historial_empresa.append([j[2][0],j[2][1], [j[2][2],j[0],j[1]] ])

        list_json.append(historial_empresa)
    print('exit')
    print(list_historico[0])
    print(list_json[0])
    return jsonify ( {'historico': list_json,
                      'ini': list[0][0],
                      'fin':list[11][1]} )

"""
#call _get_venta_suc_by_fecha(3,'2000-01-01' , '2000-12-31')
"""

@bp.route('/historico_hist_suc_name/<nombre>')
@cross_origin(origin='*')
def historico_suc_name(nombre):

    fecha_ = datetime.now()
    list = []

    datetime_str = '2000/01/01 00:00:00'

    fecha_ = datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')

    list.append([str(fecha_.year) + '/01/01' , str(fecha_.year) + '/01/31' ]) #ene
    list.append([str(fecha_.year) + '/02/01', str(fecha_.year) + '/02/28'])#feb
    list.append([str(fecha_.year) + '/03/01', str(fecha_.year) + '/03/31'])#mar

    list.append([str(fecha_.year) + '/04/01', str(fecha_.year) + '/04/30'])#abrl
    list.append([str(fecha_.year) + '/05/01', str(fecha_.year) + '/05/31'])#mayo
    list.append([str(fecha_.year) + '/06/01', str(fecha_.year) + '/06/30'])#juni
    list.append([str(fecha_.year) + '/07/01', str(fecha_.year) + '/07/31'])#jul
    list.append([str(fecha_.year) + '/08/01', str(fecha_.year) + '/08/31'])#ago
    list.append([str(fecha_.year) + '/09/01', str(fecha_.year) + '/09/30'])#sep
    list.append([str(fecha_.year) + '/10/01', str(fecha_.year) + '/10/31'])#oct
    list.append([str(fecha_.year) + '/11/01', str(fecha_.year) + '/11/30'])#nov
    list.append([str(fecha_.year) + '/12/01', str(fecha_.year) + '/12/31'])#dic



    #call _get_sucursal_by_name ('Tampico Centro')

    from app import mysql
    cur_sucursales = mysql.get_db().cursor()
    cur_sucursales.execute ("""call _get_sucursal_by_name (%s)""",(nombre,))
    data_sucursales  = cur_sucursales.fetchall()[0]

    list_historico=[]
    for  i in list:
        cur_venta = mysql.get_db().cursor()
        cur_venta.execute("""call  _get_venta_suc_by_fecha (%s,%s,%s) """ , (data_sucursales[0], i[0],i[1],))
        list_historico.append(cur_venta.fetchall()[0])
    print(list_historico)

    val_max=list_historico[0][2]
    val_min=list_historico[0][2]

    for i in list_historico:
        if i[2]> val_max:
            val_max = i[2]
        if i[2]< val_min:
            val_min = i[2]

    print([val_max, val_min])

    list_json = []
    for i in list_historico:
        estado  = 0
        if i[2] == val_max:
            estado =1
        if i[2] == val_min:
            estado =-1
        list_json.append([i[0],i[1], str(i[2]), estado])

    return jsonify ( {'historico': list_json,
                      'ini': list[0][0],
                      'fin':list[11][1],
                        'ID': data_sucursales[0],
                      'nombre': nombre} )



@bp.route('/hist_suc_venta_art_fechas/<suc>/<fecha_ini>/<fecha_fin>/<n>')
@cross_origin(origin='*')
def hist_suc_venta_fechas(suc,fecha_ini,fecha_fin,n):


    from app import mysql
    cur_sucursales = mysql.get_db().cursor()
    cur_sucursales.execute("""call _get_sucursal_by_name (%s)""", (suc,))
    data_sucursales = cur_sucursales.fetchall()[0]

    cur_venta = mysql.get_db().cursor()
    cur_venta.execute(""" call _get_venta_articulos_por_fechas(%s, %s , %s,%s)""", (data_sucursales[0],
                                                                                    fecha_ini,
                                                                                    fecha_fin,10))
    data  =  cur_venta.fetchall()
    data_json =[]

    for i in data:
        data_json.append([i[0], i[1],i[2], str(i[3])])

    print(data_json)
    return jsonify ( {'ventas': data_json ,
                      'n':n ,
                      'sucursal':data_sucursales[1],
                     'fecha_ini': fecha_ini,
                     'fecha_fin': fecha_fin })



@bp.route('/hist_succursales_rango_periodo/<fecha_ini>/<fecha_fin>/<periodo>')
@cross_origin(origin='*')
def historico_sucursles_por_fechas_periodo(fecha_ini,fecha_fin,periodo):


    d_fecha_ini = datetime.strptime(fecha_ini, '%Y-%m-%d').date()
    d_fecha_fin =  datetime.strptime(fecha_fin, '%Y-%m-%d').date()

    fecha_actual = d_fecha_ini

    fechas_ini = []
    """"
        while fecha_actual < d_fecha_fin:
    
            fecha_temp = fecha_actual+ timedelta(days=int(periodo))
            fechas.append([fecha_actual , fecha_temp])
            fecha_actual = fecha_temp+ timedelta(days=1)
    """
    for result in perdelta(d_fecha_ini,d_fecha_fin, timedelta(days=int(periodo))):
        fechas_ini.append(result)


    fechas=[]

    for i in range(len(fechas_ini)-1):
        fechas.append([fechas_ini[i]+timedelta(days=1), fechas_ini[i+1]])

    for i in fechas:
        print (i)


    from app import mysql
    cur_sucursales =  mysql.get_db().cursor()
    cur_sucursales.execute("call get_all_empresas(); ")
    data = cur_sucursales.fetchall()

    list_sucursales = []
    for i in data:
        list_sucursales.append([i , []])

    for i in fechas:
        cur_historial = mysql.get_db().cursor()
        cur_historial.execute("""call get_ventas_por_fechas(%s ,%s );""" , (i[0],i[1],))
        data_hist = cur_historial.fetchall()
        #print(data_hist)# data_his almaceda los puntos obtenidos en las graficas
        for it_data in data_hist:
            for it_suc in list_sucursales:
                if it_data[0] == it_suc[0][0]:
                    it_suc[1].append([ str(it_data[2]), i[1]])

    return jsonify({'ventas': list_sucursales,
                    'fecha_ini':fecha_ini,
                    'fecha_fin':fecha_fin})




@bp.route('/historico_hist_suc_name_rango_fechas_periodo/<nombre>/<fecha_ini>/<fecha_fin>/<periodo>')
@cross_origin(origin='*')
def historico_suc_name_rango_fechas_periodo(nombre,fecha_ini,fecha_fin,periodo):

    d_fecha_ini = datetime.strptime(fecha_ini, '%Y-%m-%d').date()
    d_fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

    fecha_actual = d_fecha_ini

    fechas_ini = []


    for result in perdelta(d_fecha_ini, d_fecha_fin, timedelta(days=int(periodo))):
        fechas_ini.append(result)

    fechas = []

    for i in range(len(fechas_ini) - 1):
        fechas.append([fechas_ini[i] + timedelta(days=1), fechas_ini[i + 1]])

    for i in fechas:
        print(i)

    from app import mysql
    cur_sucursales = mysql.get_db().cursor()
    cur_sucursales.execute ("""call _get_sucursal_by_name (%s)""",(nombre,))
    data_sucursales  = cur_sucursales.fetchall()[0]

    list_historico=[]
    for  i in fechas:
        cur_venta = mysql.get_db().cursor()
        cur_venta.execute("""call  _get_venta_suc_by_fecha (%s,%s,%s) """ , (data_sucursales[0], i[0],i[1],))
        list_historico.append(cur_venta.fetchall()[0])
    print(list_historico)

    val_max=list_historico[0][2]
    val_min=list_historico[0][2]

    for i in list_historico:
        if i[2]> val_max:
            val_max = i[2]
        if i[2]< val_min:
            val_min = i[2]

    print([val_max, val_min])

    list_json = []
    for i in list_historico:
        estado  = 0
        if i[2] == val_max:
            estado =1
        if i[2] == val_min:
            estado =-1
        list_json.append([i[0],i[1], str(i[2]), estado])

    return jsonify ( {'historico': list_json,
                      'ini':fecha_ini,
                      'fin':fecha_fin,
                        'ID': data_sucursales[0],
                      'nombre': nombre} )


@bp.route('/hist_suc_emp_fechas_periodo/<suc>/<fecha_ini>/<fecha_fin>/<periodo>')
@cross_origin(origin='*')
def hist_suc_fechas_periodo(suc,fecha_ini,fecha_fin, periodo):
    print('inicia')
    id= -1;
    error=[]
    from app import mysql

    cur = mysql.get_db().cursor()
    cur.execute("""select id_sucursal,nombre from sucursales where nombre =  %s;""" , (suc))
    id= cur.fetchall()[0][0]


    cur_empleados = mysql.get_db().cursor()
    cur_empleados.execute(""" select id_empleado from empleados where id_sucursal = %s """ , (id,))
    #cur_empleados.execute(""" select id_empleado from empleados where id_empleado  in (1,2)""")

    data_empleados = cur_empleados.fetchall()
    print(data_empleados)

    if id==-1:
        error.append("ID")
    print(id)

    list = []

    d_fecha_ini = datetime.strptime(fecha_ini, '%Y-%m-%d').date()
    d_fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

    fecha_actual = d_fecha_ini

    fechas_ini = []

    for result in perdelta(d_fecha_ini, d_fecha_fin, timedelta(days=int(periodo))):
        fechas_ini.append(result)

    for i in range(len(fechas_ini) - 1):
        list.append([fechas_ini[i] + timedelta(days=1), fechas_ini[i + 1]])

    for i in list:
        print(i)


    historico = []
    for id_empleado in data_empleados:
        historico_empleado =[]
        for i in list:
            #print((id_empleado[0] , i[0], ))
            cur_historico = mysql.get_db().cursor()
            cur_historico.execute("""call get_historial_empleados_suc_fecha(%s,%s , %s ); """,
                                  (id_empleado[0], i[0], i[1] , ))
            data= cur_historico.fetchall()
            c_data =[]

            for i in data:
                c_data.append([i[1],i[2],i[3],str(i[4])])
            historico_empleado.append(c_data)
        historico.append(historico_empleado)

    return jsonify ( {'ventas':historico,
                      'Fecha_ini': fecha_ini,
                      'Fecha_fin': fecha_fin,
                      'ID': id,
                      'suc':suc,
                      'error': error} )


#ayuda para manejo de fechas
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta