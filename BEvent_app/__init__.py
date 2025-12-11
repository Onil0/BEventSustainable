from bson import ObjectId
from flask import Flask, request  # Aggiunto 'request' qui, serviva per add_header
from flask_login import LoginManager
# --- GREEN CODING: Import Minify ---
from flask_minify import Minify

from BEvent_app.Routes import home
from .InterfacciaPersistenza.Fornitore import Fornitore
from .InterfacciaPersistenza.Organizzatore import Organizzatore
from .InterfacciaPersistenza.Utente import Utente
from .Routes import views
from .db import get_db
from .Autenticazione.AutenticazioneController import aut
from .GestioneEvento.GestioneEventoController import ge
from .Fornitori.FornitoriController import Fornitori
from .RicercaEvento.RicercaEventoController import re
from .FeedBack.FeedBackController import fb


def create_app():
    app = Flask(__name__)

    app.secret_key = 'BEvent'
    app.config['SECRET_KEY'] = "BEVENT"

    # --- GREEN CODING: Attivazione Minificazione Automatica ---
    # Questo middleware comprime HTML, CSS e JS al volo prima di inviarli al browser.
    # html=True: Rimuove spazi e commenti dalle pagine
    # js=True: Minifica script inline e file statici
    # cssless=True: Minifica fogli di stile
    Minify(app=app, html=True, js=True, cssless=True)

    datab = get_db()
    login_manager = LoginManager(app)
    login_manager.login_view = 'views.home'

    app.register_blueprint(Fornitori, url_prefix="/")
    app.register_blueprint(fb, url_prefix="/")
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(aut, url_prefix='/')
    app.register_blueprint(ge, url_prefix='/')
    app.register_blueprint(re, url_prefix='/')

    def get_user_by_id(user_id):
        user_data = datab.Utente.find_one({'_id': ObjectId(user_id)})
        if user_data:
            if user_data['Ruolo'] == '2':
                return Organizzatore(user_data, user_data)
            elif user_data['Ruolo'] == '3':
                return Fornitore(user_data, user_data)
        return None

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    @app.route('/')
    def index():
        return home()

    # --- GREEN CODING: Cache Control Optimization ---
    @app.after_request
    def add_header(response):
        """
        Aggiunge header di caching per ridurre il traffico di rete ripetuto.
        Impatto: Riduce i download ridondanti (minore consumo server e client).
        """
        # Applica cache solo ai file statici (css, js, immagini)
        if request.path.startswith('/static'):
            response.headers['Cache-Control'] = 'public, max-age=3600'
        return response

    return app