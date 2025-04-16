from flask import json, jsonify
from dinhoseller import create_app


app = create_app()


@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "good job"})

@app.route('/isSuperAdminConfigured', methods=['GET'])
def is_super_admin_configured():
    try:
        with open('dinhoseller/app_settings.json', 'r') as file:
            settings = json.load(file)
            is_super_admin_configured = settings.get('isSuperAdminConfigured', False)
            return jsonify({'isSuperAdminConfigured': is_super_admin_configured})
    except FileNotFoundError:
        return jsonify({'error': 'app_settings.json not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding JSON'}), 500


app.run(host='0.0.0.0',port=5000)

