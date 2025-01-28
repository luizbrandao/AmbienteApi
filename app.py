import os
from flask_cors import cross_origin
import psycopg2
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host=os.environ['DB_HOST'],
                            database=os.environ['DB_DATABASE'],
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn

@app.route('/json-example', methods=['POST'])
def json_example():
    request_data = request.get_json()
    temperatura = request_data['temperatura']
    umidade = request_data['umidade']
    pressao = request_data['pressao']
    luminosidade = request_data['luminosidade']    
    data = request_data['data']
    interno = request_data['interno']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO "Registro" (temperatura, umidade, pressao, luminosidade, "data", interno) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;',
                    (temperatura, umidade, pressao, luminosidade, data, interno))
    returned_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({ "id" : returned_id})

@app.route('/dados',methods=['GET'])
@cross_origin()
def get_dados():
    conn = get_db_connection()
    cur = conn.cursor()
    
    data_limite = datetime.now() - timedelta(hours=24)
    
    cur.execute('SELECT * FROM "Registro" WHERE data > %s', (data_limite,))
    
    resultados = cur.fetchall()
    
    dados_formatados = [{'id':row[0], 'data': row[5], 'temperatura': row[1], 'umidade': row[2], 'pressao':row[3], 'luminosidade':row[4]} for row in resultados]
    
    cur.close()
    conn.close()
    
    return jsonify(dados_formatados), 200

@app.route('/ultima-leitura',methods=['GET'])
@cross_origin()
def get_ultima_leitura():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM public."Registro" order by "data" desc fetch first 1 rows with ties')
    
    resultados = cur.fetchall()
    
    dados_formatados = [{'id':row[0],'data': row[5], 'temperatura': row[1], 'umidade': row[2], 'pressao':row[3], 'luminosidade':row[4], 'interno':row[6]} for row in resultados]
    
    cur.close()
    conn.close()
    
    return jsonify(dados_formatados), 200

@app.route('/dia_especifico', methods=['GET'])
def get_dia_especifico():
    
    # Obtém o parâmetro da requisição
    dia_str = request.args.get('dia')
    if not dia_str:
        return jsonify({"error": "O parâmetro 'dia' é obrigatório."}), 400

    # Converte a string em um objeto datetime
    try:
        dia = datetime.strptime(dia_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "O formato da data deve ser 'YYYY-MM-DD'."}), 400

    # Define o intervalo do dia
    inicio_do_dia = dia
    fim_do_dia = dia + timedelta(days=1)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM public."Registro" r where r."data" between %s and %s order by r."data" desc', (inicio_do_dia, fim_do_dia))
    
    resultados = cur.fetchall()
    
    dados_formatados = [{'id':row[0],'data': row[5], 'temperatura': row[1], 'umidade': row[2], 'pressao':row[3], 'luminosidade':row[4], 'interno':row[6]} for row in resultados]
    
    cur.close()
    conn.close()
    
    return jsonify(dados_formatados), 200


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=1234, host='0.0.0.0')  