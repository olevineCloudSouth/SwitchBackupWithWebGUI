from flask import Flask
from flask_cors import CORS


from flask_endpoints.check_config import web_switch_check
from flask_endpoints.get_config import web_get_config
from flask_endpoints.track_ip import track_ip
from flask_endpoints.switch_list import switch_list
from flask_endpoints.get_ip_arp import web_get_arps
from flask_endpoints.get_int_status import web_get_int
from flask_endpoints.get_mac import web_get_mac

app = Flask(__name__)
CORS(app)

app.register_blueprint(track_ip)
app.register_blueprint(web_switch_check)
app.register_blueprint(web_get_config)
app.register_blueprint(switch_list)
app.register_blueprint(web_get_arps)
app.register_blueprint(web_get_int)
app.register_blueprint(web_get_mac)



if __name__ == '__main__':
    app.run()
