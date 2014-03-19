from flask import Flask, request
app = Flask(__name__)
import json

@app.route("/request_broker", methods=['GET'])
def request_broker():
    a = request.args.get('broker_param', 0, type=str)
    #request_parameters = request.args
    response = {"broker_address" : "ws://localhost:9000"}
    response_json = json.dumps(response)
    return response_json

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')