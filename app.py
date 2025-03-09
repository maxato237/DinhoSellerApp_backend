from flask import jsonify
from dinhoseller import create_app


app = create_app()


@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "good job"})
app.run(host='0.0.0.0',debug=True,port=5000)