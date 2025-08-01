from dinhoseller import create_app


app = create_app()

@app.route('/', methods=['GET'])
def index():
    return "Welcome to DinhoSeller API"

app.run(host='127.0.0.1',debug=True,port=8000)
# app.run(host='127.0.0.1',debug=True,port=5000)

