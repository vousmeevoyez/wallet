"""
    HTTP Response
    __________
    This module to handle HTTP Success & Error code
"""
def no_content():
    """ Function to return 204 HTTP success message """
    return ('', 204)
#end def

def ok(data=None, message=None):
    """ Function to return 200 HTTP success message """
    response = {
        "data" : data
    }

    if message is not None:
        response["message"] = message
    # end if
    return (response, 200)
#end def

def created(data=None, message=None):
    """ Function to return 201 HTTP success message """
    response = {}

    if data is not None:
        response["data"] = data
    # end if
    if message is not None:
        response["message"] = message
    # end if
    return (response, 201)
#end def

def accepted(data=None, message=None):
    """ Function to return 202 HTTP success message """
    response = {}

    if data is not None:
        response["data"] = data
    # end if
    if message is not None:
        response["message"] = message
    # end if
    return (response, 202)
#end def
