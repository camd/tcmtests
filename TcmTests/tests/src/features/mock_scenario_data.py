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
import json

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
                {"status": "404", "request": "/api/v1/users?firstName=Jedi&lastName=Jones", "response": "No response expected", "comment": "User does not exist"},
                {"status": "200", "request": "/api/v1/users",                               "response": "POST, w/o response",   "comment": "Posting the user data"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Jones", "response": "%(activeFalse)s",      "comment": "Check user exists, but not active"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Jones", "response": "%(activeFalse)s",      "comment": "request it to be activated"},
                {"status": "200","response": "%(activeTrue)s",       "comment": "expect it's now active"}
            ]
        """ % { 'activeFalse': get_returned_user(["Jedi Jones"], "false"),
                'activeTrue': get_returned_user(["Jedi Jones"], "true")}
        
    elif scenarioName == "Activate a Non Active user":
        data = """
            [
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=NotActive","response": "%(activeFalse)s"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=NotActive","response": "%(activeFalse)s"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=NotActive","response": "%(activeFalse)s"},
                {"status": "200", "request": "/api/v1/users/8/activate","response": "POST, no return"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=NotActive","response": "%(activeTrue)s"}
            ]
        """ % { 'activeFalse': get_returned_user(["Jedi NotActive"], "false"),
                'activeTrue': get_returned_user(["Jedi NotActive"], "true")}
    
    elif scenarioName == "Deactivate an Active user":
        data = """
            [
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Active","response": "%(activeTrue)s"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Active","response": "%(activeTrue)s"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Active","response": "%(activeTrue)s"},
                {"status": "200", "request": "/api/v1/users/8/activate",                    "response": "POST, w/o response"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Active","response": "%(activeFalse)s"}
            ]
        """ % { 'activeFalse': get_returned_user(["Jedi Active"], "false"),
                'activeTrue': get_returned_user(["Jedi Active"], "true")}
        
    elif scenarioName == "Create a new Role and add Permission":
        data = """
            [
                {"status": "200", "request": "/api/v1/users/current",                       "response": "%(ourAdminUser)s",   "comment": "logged in as user"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Admin", "response": "%(ourAdminUser)s",   "comment": "get id of user"},
                {"status": "200", "request": "/api/v1/users/8/roles",                       "response": "%(users_roles)s",    "comment": "check users roles"},
                {"status": "200", "request": "/api/v1/roles",                               "response": "POST, w/o response", "comment": "create a new role"},
                {"status": "200", "request": "/api/v1/roles?description=Creationator",      "response": "%(new_role)s",       "comment": "get id of role"},
                {"status": "200", "request": "/api/v1/roles/24/permissions",                "response": "POST, w/o response", "comment": "add permission to role"},
                {"status": "200", "request": "/api/v1/roles?description=Creationator",      "response": "%(new_role)s",       "comment": "get id of role"},
                {"status": "200", "request": "/api/v1/roles/24/permissions",                "response": "%(permissions)s",    "comment": "get permissions for new role"}
            ]
        """ % { 'ourAdminUser': get_returned_user(["Jedi Admin"], "true"),
                'users_roles': get_returned_roles(["ADMINISTRATOR"]), 
                'new_role': get_returned_roles(["Creationator"]),
                'permissions': get_returned_permissions(["Spammer"])}
        
    elif scenarioName == "Get list of roles":
        data = """
            [
                {"status": "200", "request": "/api/v1/roles"                   ,"response": "%(roles)s",       "comment": "get list of roles"},
                {"status": "200", "request": "/api/v1/roles?sortDirection=ASC" ,"response": "%(asc_roles)s",   "comment": "get list of ASC roles"},
                {"status": "200", "request": "/api/v1/roles?sortDirection=DESC","response": "%(desc_roles)s",  "comment": "get list of DESC roles"}
            ]
        """ % { 'roles': get_returned_roles(["Apple", "Zipper", "Frame"]),
                'asc_roles': get_returned_roles(["Apple", "Frame", "Zipper"]),
                'desc_roles': get_returned_roles(["Zipper", "Frame", "Apple"])}
    
    elif scenarioName == "Create a new Test Case":
        data = """
            [
                {"status": "200", "request": "/api/v1/users/current",                         "response": "%(our_user)s",       "comment": "logged in as user"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Creator", "response": "%(our_user)s",       "comment": "get id of user"},
                {"status": "200", "request": "/api/v1/users/8/roles",                         "response": "%(users_roles)s",    "comment": "check users roles"},
                {"status": "200", "request": "/api/v1/testcases",                             "response": "POST, w/o response", "comment": "create a new test case"},
                {"status": "200", "request": "/api/v1/testcases?description=Testing%%20mic%%20%%231.%%20%%20Isn%%27t%%20this%%20a%%20lot%%20of%%20fun.", "response": "%(new_test_case)s",  "comment": "get new test case data"}
            ]
        """ % { 'our_user': get_returned_user(["Jedi Creator"], "true"),
                'users_roles': get_returned_roles(["TEST_CREATOR"]),
                'new_test_case': get_returned_test_case(["Testing mic #1.  Isn't this a lot of fun."]) 
              }

    elif scenarioName == "Assign a Role to a User":
        data = """
            [
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Roller","response": "%(our_user)s",       "comment": "Given user Jedi Roller has active status true"},
                {"status": "200", "request": "/api/v1/roles",                               "response": "%(roles)s",          "comment": "And the role of CHIPPER exists"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Roller","response": "%(our_user)s",       "comment": "get id of user"},
                {"status": "200", "request": "/api/v1/users/8/roles"                       ,"response": "%(old_roles)s",      "comment": "And Jedi Roller does not already have the role of CHIPPER"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Roller","response": "%(our_user)s",       "comment": "get id of user"},
                {"status": "200", "request": "/api/v1/users/8/roles"                       ,"response": "POST, w/o response", "comment": "When I add role of CHIPPER to user Jedi Roller"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Roller","response": "%(our_user)s",       "comment": "get id of user"},
                {"status": "200", "request": "/api/v1/users/8/roles"                       ,"response": "%(new_roles)s",      "comment": "Then Jedi Roller has the role of CHIPPER"}
            ]
        """ % { 'our_user': get_returned_user(["Jedi Roller"], "true"),
                'roles': get_returned_roles(["CHIPPER"]), 
                'old_roles': get_returned_roles(["MASHER", "SMASHER"]), 
                'new_roles': get_returned_roles(["MASHER", "SMASHER", "CHIPPER"]) 
            }

    elif scenarioName == "Check Roles of a User":
        data = """
            [
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Roller","response": "%(our_user)s",       "comment": "Given user Jedi Roller has active status true"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Roller","response": "%(our_user)s",       "comment": "get id of user"},
                {"status": "200", "request": "/api/v1/users/8/roles"                       ,"response": "%(roles)s",          "comment": "Then Jedi Roller has the role of MASHER and SMASHER"}
            ]
        """ % { 'our_user': get_returned_user(["Jedi Roller"], "true"),
                'roles': get_returned_roles(["MASHER", "SMASHER"])
              }
               
    elif scenarioName == "Check the Assignments of a User":
        data = """
            [
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Assigned","response": "%(our_user)s",       "comment": "Given user has active status true"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Assigned","response": "%(our_user)s",       "comment": "get id of user"},
                {"status": "200", "request": "/api/v1/users/8/assignments"                   ,"response": "%(assignments)s",    "comment": "Then the user has the listed assignments"}
            ]
        """ % { 'our_user': get_returned_user(["Jedi Assigned"], "true"),
                'assignments': get_returned_assignments(["What the cat dragged in", "Where I put the keys"])
              }
        
    elif scenarioName == "Create a new Company":
        data = """
            [
                {"status": "200", "request": "/api/v1/users/current",                         "response": "%(our_user)s",       "comment": "logged in as user"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Creator", "response": "%(our_user)s",       "comment": "get id of user"},
                {"status": "200", "request": "/api/v1/users/8/roles",                         "response": "%(users_roles)s",    "comment": "check users roles"},
                {"status": "404", "request": "/api/v1/companies?name=Massive%%20Dynamic",     "response": "%(no_companies)s",   "comment": "check company does not exist"},
                {"status": "200", "request": "/api/v1/companies",                             "response": "POST, w/o response", "comment": "create a new company"},
                {"status": "200", "request": "/api/v1/companies?name=Massive%%20Dynamic",     "response": "%(exist_companies)s","comment": "check now company exists"}
            ]
        """ % { 'our_user': get_returned_user(["Jedi Creator"], "true"),
                'users_roles': get_returned_roles(["COMPANY_CREATOR"]),
                'no_companies': get_returned_companies([]),
                'exist_companies': get_returned_companies(["Massive Dynamic"]) 
              }
        
    elif scenarioName == "Create a new Environment":
        data = """
            [
                {"status": "200", "request": "/api/v1/users/current",                         "response": "%(our_user)s",       "comment": "logged in as user"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Creator", "response": "%(our_user)s",       "comment": "get id of user"},
                {"status": "200", "request": "/api/v1/users/8/roles",                         "response": "%(users_roles)s",    "comment": "check users roles"},
                {"status": "404", "request": "/api/v1/companies?name=Walter%%27s%%20Lab",     "response": "%(no_envs)s",        "comment": "check environment does not exist"},
                {"status": "200", "request": "/api/v1/companies",                             "response": "POST, w/o response", "comment": "create a new environment"},
                {"status": "200", "request": "/api/v1/companies?name=Walter%%27s%%20Lab",     "response": "%(exist_envs)s",     "comment": "check now environment exists"}
            ]
        """ % { 'our_user': get_returned_user(["Jedi Creator"], "true"),
                'users_roles': get_returned_roles(["ENVIRONMENT_CREATOR"]),
                'no_envs': get_returned_environments([]),
                'exist_envs': get_returned_environments(["Walter's Lab"]) 
              }

    elif scenarioName == "Create a new Environment Type":
        data = """
            [
                {"status": "200", "request": "/api/v1/users/current",                         "response": "%(our_user)s",       "comment": "logged in as user"},
                {"status": "200", "request": "/api/v1/users?firstName=Jedi&lastName=Creator", "response": "%(our_user)s",       "comment": "get id of user"},
                {"status": "200", "request": "/api/v1/users/8/roles",                         "response": "%(users_roles)s",    "comment": "check users roles"},
                {"status": "404", "request": "/api/v1/companies?name=Laboratory",             "response": "%(no_companies)s",   "comment": "check environment type does not exist"},
                {"status": "200", "request": "/api/v1/companies",                             "response": "POST, w/o response", "comment": "create a new environment type"},
                {"status": "200", "request": "/api/v1/companies?name=Laboratory",             "response": "%(exist_companies)s","comment": "check now environment type exists"}
            ]
        """ % { 'our_user': get_returned_user(["Jedi Creator"], "true"),
                'users_roles': get_returned_roles(["ENVIRONMENT_CREATOR"]),
                'no_companies': get_returned_environment_type([]),
                'exist_companies': get_returned_environment_type(["Laboratory"]) 
              }


    return data


'''
############################################################################

                           RETURN TYPES

############################################################################

ASSUMPTION: I wasn't sure here.  So I'm making an assumption that when you request an object type, you'll get
            an array in return.  You may only get one element in that array, but it'll be a JSON array.  So I'm
            going to return an array, even when it only has 1 item.  These methods will be passed an array of
            whatever item type, and I'll return an array of JSON types for it, even if there's only 1 item in
            that array.

'''

def get_returned_user(names, active, resid=7):  
    '''
        Return an array of users.  It increments the resid for each one.  They're all the same
        value of "active" for now.  May need to change that in the future.
    '''  

    users = "{\"user\":["
    for name in names:
        name_parts = name.split()
        fname = name_parts[0]
        lname = name_parts[1]
        resid = resid + 1
        
        users += """
            {
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
            },""" % {'fname': fname, 'lname': lname, 'active': active, 'resid': resid}

    # we will have an extra comma at the end of the last item, so just clip it.    
    if len(names) > 0:
        users = users[:-1]
    users += "]}"

    return urllib.quote(users)

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
    if len(role_names) > 0:
        roles = roles[:-1]
    roles += "]}"
    
    return urllib.quote(roles)


def get_returned_assignments(assignment_names):
    return get_returned_test_case(assignment_names)


def get_returned_permissions(permission_names):
    perms = "{\"permission\":["
    for perm_name in permission_names:
        perms += """
            {
                "description": "%(perm_name)s",
                "resourceIdentity": "24"
            },""" % {'perm_name': perm_name}
        
    # we will have an extra comma at the end of the last item, so just clip it.    
    if len(permission_names) > 0:
        perms = perms[:-1]
    perms += "]}"
    
    return urllib.quote(perms)

def get_returned_test_case(tc_descriptions):
    testcases = "{\"testcase\":["
    for tc_desc in tc_descriptions:
        testcases += """
            {
                "productid":"1",
                "maxattachmentsizeinmbytes":"10",
                "maxnumberofattachments":"5",
                "name":"Application login",
                "description":"%(description)s",
                "testcasesteps":{
                    "testcasestep":{
                        "stepnumber":"1",
                        "name":"login name missing ",
                        "instruction":"don't provide login name",
                        "expectedresult":"validation message should appear",
                        "estimatedtimeinmin":"1"
                    }
                },
                "testcasestatusid":"2",
                "majorversion":"1",
                "minorversion":"1",
                "latestversion":"true",
                "resourceidentity":"...",
                "timeline":"..."
            },""" % {'description': tc_desc}
    if len(tc_descriptions) > 0:
        testcases = testcases[:-1]
        
    testcases += "]}"
    return urllib.quote(testcases)

def get_returned_companies(company_names):
    companies = "{\"company\":"
    
    # make it an array, if there's more than one
    if len(company_names) > 1:
        companies += "["
        
    for co_name in company_names:
        companies += """
            {
                "name": "%(co_name)s",
                "phone": "617-417-0593",
                "address": "31 lakeside drive",
                "city": "Boston",
                "zip": "01721",
                "companyUrl": "http//www.utest.com",
                "resourceIdentity": "5",
                "timeline": "bleh"
            },""" % {'co_name': co_name}
    if len(company_names) > 0:
        companies = companies[:-1]
        
    # make it an array, if there's more than one
    if len(company_names) > 1:
        companies += "]"

    companies += "}"
    return urllib.quote(companies)

def get_returned_environments(env_names):
    '''
        Takes an array of env names
    '''
    envs = []
    for env_name in env_names:
        obj = {"name": env_name, \
               "localeCode": "en_US", \
               "sortOrder": 0, \
               "environementTypeId": 1, \
               "resourceIdentity": 007, \
               "timeline": "whenever"}
        envs.append(obj)

    environments = {"environment": envs}
        
    return urllib.quote(json.dumps(environments))


def get_returned_environment_type(envtype_names):
    '''
        Takes an array of env type names
    '''
    env_types = []
    for env_name in envtype_names:
        obj = {"name": env_name, \
               "localeCode": "en_US", \
               "sortOrder": 0, \
               "resourceIdentity": 007, \
               "timeline": "whenever"}
        env_types.append(obj)

    environment_types = {"environmentType": env_types}
        
    return urllib.quote(json.dumps(environment_types))
