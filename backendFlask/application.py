from flask import Flask

from flask_endpoints.check_config import web_switch_check

app = Flask(__name__)

app.register_blueprint(web_switch_check)

if __name__ == '__main__':
    app.run()