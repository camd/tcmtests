############################################################################
'''

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
    
    steps = ""
    if scenarioName == "Register a new user":
        steps = \
            [
               {"comment": "User does not exist", 
                "request": "/api/v1/users?firstName=Jedi&lastName=Jones", 
                "response": "No response expected", 
                "status": "404"
                },
               {"comment": "Posting the user data", 
                "request": "/api/v1/users",                               
                "response": "POST, w/o response",   
                "status": "200"
                },
               {"comment": "Check user exists, but not active", 
                "request": "/api/v1/users?firstName=Jedi&lastName=Jones", 
                "response": get_returned_user(["Jedi Jones"], "false"),      
                "status": "200"
                },
               {"comment": "request it to be activated", 
                "request": "/api/v1/users?firstName=Jedi&lastName=Jones", 
                "response": get_returned_user(["Jedi Jones"], "false"),      
                "status": "200"
                },
               {"comment": "expect it's now active",
                "request": "/api/v1/users?firstName=Jedi&lastName=Jones", 
                "response": get_returned_user(["Jedi Jones"], "true"),
                "status": "200"       
                }
            ]
        
    elif scenarioName == "Activate a Non Active user":
        steps = \
            [
                {"comment": "check user registered", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=NotActive",
                 "response": get_returned_user(["Jedi NotActive"], "false"),
                 "status": "200"
                 },
                {"comment": "get user id", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=NotActive",
                 "response": get_returned_user(["Jedi NotActive"], "false"),
                 "status": "200"
                 },
                {"comment": "check user active status false", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=NotActive",
                 "response": get_returned_user(["Jedi NotActive"], "false"),
                 "status": "200"
                 },
                {"comment": "set user active", 
                 "request": "/api/v1/users/8/activate",
                 "response": "POST, no return",
                 "status": "200"
                 },
                {"comment": "check user active status true", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=NotActive",
                 "response": get_returned_user(["Jedi NotActive"], "true"),
                 "status": "200"
                 }
            ]
    
    elif scenarioName == "Deactivate an Active user":
        steps = \
            [
                {"comment": "check user registered", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Active",
                 "response": get_returned_user(["Jedi Active"], "true"),
                 "status": "200"
                 },
                {"comment": "get user id", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Active",
                 "response": get_returned_user(["Jedi Active"], "true"),
                 "status": "200"
                 },
                {"comment": "check user active status true", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Active",
                 "response": get_returned_user(["Jedi Active"], "true"),
                 "status": "200"
                 },
                {"comment": "set user deactivated", 
                 "request": "/api/v1/users/8/activate",                    
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "check user active status false", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Active",
                 "response": get_returned_user(["Jedi Active"], "false"),
                 "status": "200"
                 }
            ]
        
    elif scenarioName == "Create a new Role and add Permission":
        steps = \
            [
                {"comment": "logged in as user", 
                 "request": "/api/v1/users/current",                       
                 "response": get_returned_user(["Jedi Admin"], "true"),   
                 "status": "200"
                 },
                {"comment": "get id of user", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Admin", 
                 "response": get_returned_user(["Jedi Admin"], "true"),   
                 "status": "200"
                 },
                {"comment": "check users roles", 
                 "request": "/api/v1/users/8/roles",                       
                 "response": get_returned_roles(["ADMINISTRATOR"]),    
                 "status": "200"
                 },
                {"comment": "create a new role", 
                 "request": "/api/v1/roles",                               
                 "response": "POST, w/o response", 
                 "status": "200"
                 },
                {"comment": "get id of role", 
                 "request": "/api/v1/roles?description=Creationator",      
                 "response": get_returned_roles(["Creationator"]),       
                 "status": "200"
                 },
                {"comment": "add permission to role", 
                 "request": "/api/v1/roles/24/permissions",                
                 "response": "POST, w/o response", 
                 "status": "200"
                 },
                {"comment": "get id of role", 
                 "request": "/api/v1/roles?description=Creationator",      
                 "response": get_returned_roles(["Creationator"]),       
                 "status": "200"
                 },
                {"comment": "get permissions for new role", 
                 "request": "/api/v1/roles/24/permissions",                
                 "response": get_returned_permissions(["Spammer"]),    
                 "status": "200"
                 }
            ]
        
    elif scenarioName == "Get list of roles":
        steps = \
            [
                {"comment": "get list of roles", 
                 "request": "/api/v1/roles"                   ,
                 "response": get_returned_roles(["Apple", "Zipper", "Frame"]),       
                 "status": "200"
                 },
                {"comment": "get list of ASC roles", 
                 "request": "/api/v1/roles?sortDirection=ASC" ,
                 "response": get_returned_roles(["Apple", "Frame", "Zipper"]),   
                 "status": "200"
                 },
                {"comment": "get list of DESC roles", 
                 "request": "/api/v1/roles?sortDirection=DESC",
                 "response": get_returned_roles(["Zipper", "Frame", "Apple"]),  
                 "status": "200"
                 }
            ]

    elif scenarioName == "Create a new Test Case":
        steps = \
            [
                {"comment": "logged in as user", 
                 "request": "/api/v1/users/current",                         
                 "response": get_returned_user(["Jedi Creator"], "true"),       
                 "status": "200"
                 },
                {"comment": "get id of user", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Creator", 
                 "response": get_returned_user(["Jedi Creator"], "true"),       
                 "status": "200"
                 },
                {"comment": "check users roles", 
                 "request": "/api/v1/users/8/roles",                         
                 "response": get_returned_roles(["TEST_CREATOR"]),    
                 "status": "200"
                 },
                {"comment": "create a new test case", 
                 "request": "/api/v1/testcases",                             
                 "response": "POST, w/o response", 
                 "status": "200"
                 },
                {"comment": "get new test case data", 
                 "request": "/api/v1/testcases?description=Testing%20mic%20%231.%20%20Isn%27t%20this%20a%20lot%20of%20fun.", 
                 "response": get_returned_test_case(["Testing mic #1.  Isn't this a lot of fun."]),  
                 "status": "200"
                 }
            ]

    elif scenarioName == "Assign a Role to a User":
        steps = \
            [
                {"comment": "Given user Jedi Roller has active status true", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Roller",
                 "response": get_returned_user(["Jedi Roller"], "true"), 
                 "status": "200"
                 },
                {"comment": "And the role of CHIPPER exists", 
                 "request": "/api/v1/roles",                               
                 "response": get_returned_roles(["CHIPPER"]), 
                 "status": "200"
                 },
                {"comment": "get id of user", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Roller",
                 "response": get_returned_user(["Jedi Roller"], "true"), 
                 "status": "200"
                 },
                {"comment": "And Jedi Roller does not already have the role of CHIPPER", 
                 "request": "/api/v1/users/8/roles"                       ,
                 "response": get_returned_roles(["MASHER", "SMASHER"]), 
                 "status": "200"     
                 },
                {"comment": "get id of user", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Roller",
                 "response": get_returned_user(["Jedi Roller"], "true"), 
                 "status": "200"      
                 },
                {"comment": "When I add role of CHIPPER to user Jedi Roller", 
                 "request": "/api/v1/users/8/roles"                       ,
                 "response": "POST, w/o response", 
                 "status": "200"
                 },
                {"comment": "get id of user", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Roller",
                 "response": get_returned_user(["Jedi Roller"], "true"), 
                 "status": "200"      
                 },
                {"comment": "Then Jedi Roller has the role of CHIPPER", 
                 "request": "/api/v1/users/8/roles"                       ,
                 "response": get_returned_roles(["MASHER", "SMASHER", "CHIPPER"]), 
                 "status": "200"     
                 }
            ]

    elif scenarioName == "Check Roles of a User":
        steps = \
            [
                {"comment": "Given user Jedi Roller has active status true", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Roller",
                 "response": get_returned_user(["Jedi Roller"], "true"), 
                 "status": "200"      
                 },
                {"comment": "get id of user", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Roller",
                 "response": get_returned_user(["Jedi Roller"], "true"), 
                 "status": "200"      
                 },
                {"comment": "Then Jedi Roller has the role of MASHER and SMASHER", 
                 "request": "/api/v1/users/8/roles",
                 "response": get_returned_roles(["MASHER", "SMASHER"]), 
                 "status": "200"         
                 }
            ]
               
    elif scenarioName == "Check the Assignments of a User":
        steps = \
            [
                {"comment": "Given user has active status true",
                 "request": "/api/v1/users?firstName=Jedi&lastName=Assigned",
                 "response": get_returned_user(["Jedi Assigned"], "true"), 
                 "status": "200"
                 },
                {"comment": "get id of user",
                 "request": "/api/v1/users?firstName=Jedi&lastName=Assigned",
                 "response": get_returned_user(["Jedi Assigned"], "true"), 
                 "status": "200"
                 },
                {"comment": "Then the user has the listed assignments",
                 "request": "/api/v1/users/8/assignments",
                 "response": get_returned_assignments(["What the cat dragged in", "Where I put the keys"]), 
                 "status": "200" 
                 }
            ]
        
    elif scenarioName == "Create a new Company":
        steps = \
            [
                {"comment": "logged in as user",
                 "request": "/api/v1/users/current",                          
                 "response": get_returned_user(["Jedi Creator"], "true"), 
                 "status": "200"       
                 },
                {"comment": "get id of user",
                 "request": "/api/v1/users?firstName=Jedi&lastName=Creator",  
                 "response": get_returned_user(["Jedi Creator"], "true"), 
                 "status": "200"       
                 },
                {"comment": "check users roles",
                 "request": "/api/v1/users/8/roles",                          
                 "response": get_returned_roles(["COMPANY_CREATOR"]), 
                 "status": "200"    
                 },
                {"comment": "check company does not exist",
                 "request": "/api/v1/companies?name=Massive%20Dynamic",     
                 "response": get_returned_companies([]), 
                 "status": "404"   
                 },
                {"comment": "create a new company",
                 "request": "/api/v1/companies",                             
                 "response": "POST, w/o response",
                 "status": "200" 
                 },
                {"comment": "check now company exists", 
                 "request": "/api/v1/companies?name=Massive%20Dynamic",     
                 "response": get_returned_companies(["Massive Dynamic"]), 
                 "status": "200"
                 }
            ]

        
    elif scenarioName == "Create a new Environment":
        steps = \
            [
                {"comment": "logged in as user", 
                 "request": "/api/v1/users/current",                         
                 "response": get_returned_user(["Jedi Creator"], "true"), 
                 "status": "200"      
                 },
                {"comment": "get id of user", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Creator", 
                 "response": get_returned_user(["Jedi Creator"], "true"), 
                 "status": "200"      
                 },
                {"comment": "check users roles", 
                 "request": "/api/v1/users/8/roles",                         
                 "response": get_returned_roles(["ENVIRONMENT_CREATOR"]),  
                 "status": "200"  
                 },
                {"comment": "check environment does not exist", 
                 "request": "/api/v1/companies?name=Walter%%27s%%20Lab",     
                 "response": get_returned_environments([]), 
                 "status": "404"        
                 },
                {"comment": "create a new environment", 
                 "request": "/api/v1/companies",                             
                 "response": "POST, w/o response", 
                 "status": "200"
                 },
                {"comment": "check now environment exists", 
                 "request": "/api/v1/companies?name=Walter%%27s%%20Lab",     
                 "response": get_returned_environments(["Walter's Lab"]),  
                 "status": "200"   
                 }
            ]

    elif scenarioName == "Create a new Environment Type":
        steps = \
            [
                {"comment": "logged in as user", 
                 "request": "/api/v1/users/current",                         
                 "response": get_returned_user(["Jedi Creator"], "true"),  
                 "status": "200"     
                 },
                {"comment": "get id of user", 
                 "request": "/api/v1/users?firstName=Jedi&lastName=Creator", 
                 "response": get_returned_user(["Jedi Creator"], "true"),  
                 "status": "200"     
                 },
                {"comment": "check users roles", 
                 "request": "/api/v1/users/8/roles",                         
                 "response": get_returned_roles(["ENVIRONMENT_CREATOR"]),  
                 "status": "200"  
                 },
                {"comment": "check environment type does not exist", 
                 "request": "/api/v1/companies?name=Laboratory",             
                 "response": get_returned_environment_type([]),  
                 "status": "404" 
                 },
                {"comment": "create a new environment type", 
                 "request": "/api/v1/companies",                             
                 "response": "POST, w/o response", 
                 "status": "200"
                 },
                {"comment": "check now environment type exists", 
                 "request": "/api/v1/companies?name=Laboratory",             
                 "response": get_returned_environment_type(["Laboratory"]),
                 "status": "200"
                 }
            ]

    data = json.dumps(steps)
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

    user_array = []
    for name in names:
        name_parts = name.split()
        fname = name_parts[0]
        lname = name_parts[1]
        resid = resid + 1
        
        obj = {
                "firstname":fname,
                "lastname":lname,
                "email":fname + lname + "@utest.com",
                "loginname":fname + lname,
                "password":fname + lname + "123",
                "companyid":1,
                "communitymember":"false",
                "active":active,
                "resourceIdentity":resid,
                "timeline":"..."
        }
        user_array.append(obj)
    
    users = {"user": user_array}
    return urllib.quote(json.dumps(users))


def get_returned_roles(role_names):
    role_array = []
    for role_name in role_names:
        obj = {
                "description": role_name,
                "resourceIdentity": "24",
                "timeline": "wha?"
        }
        role_array.append(obj)
    roles = {"role": role_array}
    return urllib.quote(json.dumps(roles))


def get_returned_assignments(assignment_names):
    return get_returned_test_case(assignment_names)


def get_returned_permissions(permission_names):
    perm_array = []
    for perm_name in permission_names:
        obj = {
                "description": perm_name,
                "resourceIdentity": "24"
        }
        perm_array.append(obj)
    
    permissions = {"permission": perm_array}
    return urllib.quote(json.dumps(permissions))

def get_returned_test_case(tc_descriptions):
    tc_array = []
    for tc_desc in tc_descriptions:
        obj = {
                "productid":"1",
                "maxattachmentsizeinmbytes":"10",
                "maxnumberofattachments":"5",
                "name":"Application login",
                "description":tc_desc,
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
        }
        tc_array.append(obj)

    testcases = {"testcase": tc_array}
    return urllib.quote(json.dumps(testcases))

def get_returned_companies(company_names):
    '''
        Takes an array of company names
    '''
    cos_array = []    
    for co_name in company_names:
        obj = {
                "name": co_name,
                "phone": "617-417-0593",
                "address": "31 lakeside drive",
                "city": "Boston",
                "zip": "01721",
                "companyUrl": "http//www.utest.com",
                "resourceIdentity": "5",
                "timeline": "bleh"
        }
        cos_array.append(obj)
    companies = {"company": cos_array}

    return urllib.quote(json.dumps(companies))

def get_returned_environments(env_names):
    '''
        Takes an array of env names
    '''
    envs = []
    for env_name in env_names:
        obj = {"name": env_name, 
               "localeCode": "en_US", 
               "sortOrder": 0, 
               "environementTypeId": 1, 
               "resourceIdentity": 007, 
               "timeline": "whenever"
        }
        envs.append(obj)

    environments = {"environment": envs}
        
    return urllib.quote(json.dumps(environments))


def get_returned_environment_type(envtype_names):
    '''
        Takes an array of env type names
    '''
    env_types = []
    for env_name in envtype_names:
        obj = {"name": env_name, 
               "localeCode": "en_US", 
               "sortOrder": 0, 
               "resourceIdentity": 007, 
               "timeline": "whenever"
        }
        env_types.append(obj)

    environment_types = {"environmentType": env_types}
        
    return urllib.quote(json.dumps(environment_types))

def get_returned_attachments(att_names):
    '''
        Takes an array of attachment filenames
    '''
    att_array = []
    for att in att_names:
        obj = {"fileName": att,
            "fileType": "DOC",
            "fileSizeInMB": "1",
            "storageURL": "//home/docs/specs.doc",
            "entityId": "1",
            "entityTypeId": "1",
            "resourceIdentity": "...",
            "timeline": "..."
        }
        att_array.append(obj)
    attachments = {"attachments": att_array}
    return urllib.quote(json.dumps(attachments))











    