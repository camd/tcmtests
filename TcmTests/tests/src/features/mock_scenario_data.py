'''
############################################################################

                           MOCK DATA GENERATOR

############################################################################
This library is used to generate the data that is sent to the mock servlet so it
can return it.  Each array item is returned for every call made.  Sometimes more than one
call is made per step, so watch out for that.  This is often a preliminary call to get
the resourceIdentity for a user, role, permission, etc.

Created on Oct 18, 2010

@author: camerondawson
'''

import urllib

def get_scenario_data(scenarioName):
    '''
        Get scenario data, keyed off the scenarioName passed in.  If the text of the scenario changes,
        then it won't find anything, so be careful. 
        
        I added a "comment" field to each element to help me keep track of what each call response was expected to respond to.
        I don't use it in the mock servlet at all.  It's purely for documentation here.  But since the objects are in block
        quotes, this was the best I could come up with.  Perhaps I'll use it.  Optional for now, really.
        
        TODO: There may be a better way to do this, but this is the best I could come up with.  Perhaps it's genius.
        It's simple, anyway.  I'm just concerned with how well it will scale.  
    '''
    
    data = ""
    if scenarioName == "Register a new user":
        data = """
            [
                {"status": "404","response": "No response expected", "comment": "User does not exist"},
                {"status": "200","response": "POST, w/o response",   "comment": "Posting the user data"},
                {"status": "200","response": "%(activeFalse)s",      "comment": "Check user exists, but not active"},
                {"status": "200","response": "%(activeFalse)s",      "comment": "request it to be activated"},
                {"status": "200","response": "%(activeTrue)s",       "comment": "expect it's now active"}
            ]
        """ % { 'activeFalse': get_returned_user("Jedi", "Jones", "false"),
                'activeTrue': get_returned_user("Jedi", "Jones", "true")}
        
    elif scenarioName == "Activate a Non Active user":
        data = """
            [
                {"status": "200","response": "%(activeFalse)s"},
                {"status": "200","response": "%(activeFalse)s"},
                {"status": "200","response": "%(activeFalse)s"},
                {"status": "200","response": "POST, no return"},
                {"status": "200","response": "%(activeTrue)s"}
            ]
        """ % { 'activeFalse': get_returned_user("Jedi", "NotActive", "false"),
                'activeTrue': get_returned_user("Jedi", "NotActive", "true")}
    
    elif scenarioName == "Deactivate an Active user":
        data = """
            [
                {"status": "200","response": "%(activeTrue)s"},
                {"status": "200","response": "%(activeTrue)s"},
                {"status": "200","response": "%(activeTrue)s"},
                {"status": "200","response": "POST, w/o response"},
                {"status": "200","response": "%(activeFalse)s"}
            ]
        """ % { 'activeFalse': get_returned_user("Jedi", "Active", "false"),
                'activeTrue': get_returned_user("Jedi", "Active", "true")}
        
    elif scenarioName == "Create a new Role and add Permission":
        data = """
            [
                {"status": "200","response": "%(ourAdminUser)s",   "comment": "logged in as user"},
                {"status": "200","response": "%(ourAdminUser)s",   "comment": "get id of user"},
                {"status": "200","response": "%(users_roles)s",    "comment": "check users roles"},
                {"status": "200","response": "POST, w/o response", "comment": "create a new role"},
                {"status": "200","response": "%(new_role)s",       "comment": "get id of role"},
                {"status": "200","response": "POST, w/o response", "comment": "add permission to role"},
                {"status": "200","response": "%(new_role)s",       "comment": "get id of role"},
                {"status": "200","response": "%(permissions)s",    "comment": "get permissions for new role"}
            ]
        """ % { 'ourAdminUser': get_returned_user("Jedi", "Admin", "true"),
                'users_roles': get_returned_roles(["ADMINISTRATOR"]), 
                'new_role': get_returned_role("Creationator"),
                'permissions': get_returned_permissions(["Spammer"])}
        
    elif scenarioName == "Get list of roles":
        data = """
            [
                {"status": "200","response": "%(roles)s",       "comment": "get list of roles"},
                {"status": "200","response": "%(asc_roles)s",   "comment": "get list of ASC roles"},
                {"status": "200","response": "%(desc_roles)s",  "comment": "get list of DESC roles"}
            ]
        """ % { 'roles': get_returned_roles(["Apple", "Zipper", "Frame"]),
                'asc_roles': get_returned_roles(["Apple", "Frame", "Zipper"]),
                'desc_roles': get_returned_roles(["Zipper", "Frame", "Apple"])}
        
    
    return data


'''
############################################################################

                           RETURN TYPES

############################################################################
'''



def get_returned_user(fname, lname, active, resid="007"):    
    user = """
        {
            "user":{
                "firstname":"%(fname)s",
                "lastname":"%(lname)s",
                "email":"%(fname)s%(lname)s@utest.com",
                "loginname":"%(fname)s%(lname)s",
                "password":"%(fname)s%(lname)s123",
                "companyid":1,
                "communitymember":"false",
                "active":"%(active)s",
                "resourceIdentity":"%(resid)s",
                "timeline":"..."
            }
        }
    """ % {'fname': fname, 'lname': lname, 'active': active, 'resid': resid}
    returnStr = ""
    for line in user:
        returnStr += line.strip()
    return urllib.quote(returnStr)

def get_returned_roles(role_names):
    roles = "{\"role\":["
    for role_name in role_names:
        roles += """
            {
                "description": "%(role_name)s",
                "resourceIdentity": "24",
                "timeline": "wha?"
            },""" % {'role_name': role_name}
        
    # we will have an extra comma at the end of the last item, so just clip it.    
    roles = roles[:-1]
    roles += "]}"
    
    returnStr = ""
    for line in roles:
        returnStr += line.strip()
    return urllib.quote(returnStr)

def get_returned_role(role_name):
    role = """
        {
            "role": {
                "description": "%(role_name)s",
                "resourceIdentity": "24",
                "timeline": "wha?"
            }
        }
    """ % {'role_name': role_name}
    returnStr = ""
    for line in role:
        returnStr += line.strip()
    return urllib.quote(returnStr)

def get_returned_permissions(permission_names):
    perms = "{\"permission\":["
    for perm_name in permission_names:
        perms += """
            {
                "description": "%(perm_name)s",
                "resourceIdentity": "24"
            },""" % {'perm_name': perm_name}
        
    # we will have an extra comma at the end of the last item, so just clip it.    
    perms = perms[:-1]
    perms += "]}"
    
    returnStr = ""
    for line in perms:
        returnStr += line.strip()
    return urllib.quote(returnStr)
