from flask import json, jsonify
from dinhoseller import create_app


app = create_app()

app.run(host='0.0.0.0',debug=True,port=5000)

