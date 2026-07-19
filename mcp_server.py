from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/launch', methods=['POST'])
def launch_token():
    return jsonify({'message': 'Token launched successfully!'})

@app.route('/trust', methods=['POST'])
def deploy_trust():
    return jsonify({'message': 'Trust deployed successfully!'})

@app.route('/reserves', methods=['GET'])
def get_reserves():
    return jsonify({'message': 'Gold: 100, Silver: 200'})

if __name__ == '__main__':
    app.run(debug=True)
