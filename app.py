import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='127.0.0.1',
                            database='ApiClimatica',
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
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO "Registros" (temperatura, umidade, pressao, luminosidade, "dataHora") VALUES (%s, %s, %s, %s, %s) RETURNING id;',
                    (temperatura, umidade, pressao, luminosidade, data))
    returned_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({ "id" : returned_id})

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=1234, host='0.0.0.0')  