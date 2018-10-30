from app import create_app, db
from app.models import ApiKey, Wallet, VirtualAccount, Transaction, ExternalLog

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db' : db, 'ApiKey' : ApiKey, 'Wallet' : Wallet, 'VirtualAccount' : VirtualAccount, 'Transaction' : Transaction, 'ExternalLog' : ExternalLog}

