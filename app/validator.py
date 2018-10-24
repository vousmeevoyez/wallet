from flask_inputs       import Inputs

from wtforms            import StringField
from wtforms.validators import DataRequired

class HeaderValidation(Inputs):
    headers = {
        'Authorization': [ DataRequired() ] 
    }
