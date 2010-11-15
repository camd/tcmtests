'''
Created on Nov 9, 2010

@author: camerondawson
'''
from lettuce import *
from numpy.ma.testutils import *
from types import ListType
import json
import urllib

'''
######################################################################

                     HELPER FUNCTIONS

######################################################################
'''

def check_existence(step, uri, arg_name, arg_value, obj_name, existence):
    arg_value_enc = urllib.quote(arg_value)
    world.conn.request("GET", "/api/v1/" + uri + "?" + arg_name + "=" + arg_value_enc)
    response = world.conn.getresponse()

    if existence.strip() == "does not exist":
        assert_equal(response.status, 404, uri + " existence")
    else:
        assert_equal(response.status, 200, uri + " existence")

        environmentJson = get_single_item(response, obj_name)
        assert_equal(environmentJson.get(arg_name), arg_value, obj_name + " name match")
    


def get_single_item(response, type):
    '''
        Expect the response to hold an array of 1 and only 1 item.  Throw an error
        if not.  Returns just the first item of that type.
    '''
    respJson = json.loads(response.read())
    # in this case, we only care about the first returned item in this array
    
    arrayJson = respJson.get(type)
    assert_not_equal(arrayJson, None, "response object didn't have our expected type of " + type + ":\n" + json.dumps(respJson))
    if isinstance(arrayJson, ListType):
        assert_equal(len(arrayJson), 1, "should only have 1 item of type: " + type)
        return arrayJson[0]
    else:
        return arrayJson


def get_user_resid(name):
    ''' 
        name: Split into 2 parts at the space.  Only the first two parts are used.  Must have at least 2 parts.
    '''
    names = name.split()
    return get_resource_identity("user", "/api/v1/users?firstName=" + names[0] + "&lastName=" + names[1])

def get_role_resid(role):
    '''
        Get the resourceIdentity of a role, based on the description of the role
    '''
    return get_resource_identity("role", "/api/v1/roles?description=" + role)


def get_resource_identity(type, uri):
    '''
        type: Something like user or role or permission.  The JSON object type
        uri: The URI stub to make the call
        
        Return the id as a string.
        
        @TODO: This presumes an array of objects is returned.  So it ONLY returns the resid for
        the first element of the array.  Will almost certainly need a better solution in the future.
        Like a new method "get_resource_identities" which returns an array of ids or something.  
    '''
    world.conn.request("GET", uri)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Response when asking for " + type)

    respJson = json.loads(response.read())
    objJson = respJson.get(type)
    # we always use this as a string
    return str(objJson[0].get("resourceIdentity"))

def get_json_obj_or_bust(respJson, elementName):
    '''
        If we don't find anything with this element name, then we assert and dump out the json.  Our data
        may be wrong.
    '''
    obj = respJson.get(elementName)
    fail_if_equal(obj, None, "\"" + elementName + "\" element not found in this response: " + str(respJson))
    return obj
    
