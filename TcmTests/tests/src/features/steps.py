'''
Created on Oct 7, 2010

@author: camerondawson
'''
from lettuce import *
from nose.tools import *
from numpy.ma.testutils import *
import httplib
import json
import scenario_data
import urllib

conn = "happy"

def get_connection():
    return httplib.HTTPConnection('localhost', 8080)

@before.all
def setup_connection():
    conn = get_connection()
    
#
# DATA SETUP
# This is the function that uploads the expected data to the mock server.
#
# @todo Need to make this only run in DEBUG mode or something
@before.each_scenario
def setup_scenario_data(scenario):
    scenarioData = scenario_data.get_scenario_data(scenario.name)
    headers = { 'content-Type':'text/plain',
            "Content-Length": "%d" % len(scenarioData) }

    conn = get_connection()
    conn.request("POST", "/api/v1/users/mockdata", "", headers)
    conn.send(scenarioData)
    conn.getresponse()

######################################################################

#                     USER STEPS

######################################################################
    
@step(u'user "(.*)" is (.*)registered')
def user_foo_check_registration(step, name, registered):
    names = name.split()
        
    conn = get_connection()
    conn.request("GET", "/api/v1/users?firstName=" + names[0] + "&lastName=" + names[1])
    response = conn.getresponse()
    data = response.read()

    if registered.strip() == "not":
        assert_equal(response.status, 404, "registration status")
    else:
        assert_equal(response.status, 200, "registration status")
        respJson = json.loads(data)
        userJson = respJson.get("user")
        assert_equal(userJson.get("firstname"), names[0], "First Name field didn't match")
        assert_equal(userJson.get("lastname"), names[1], "Last Name field didn't match")


@step(u'submit information for "(.*)"')
def submit_information_for_user_foo(step, name):
    names = name.split()
    
    xml_data = get_submit_user(names[0], names[1])
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(xml_data) }

    conn = get_connection()
    conn.request("POST", "/api/v1/users", "", headers)
    conn.send(xml_data)
    response = conn.getresponse()
    assert_equal(response.status, 200, "Create new user")


@step(u'user "(.*)" has active status "(.*)"')
def user_has_foo__has_active_status_bar(step, name, exp_active):
    names = name.split()
    conn = get_connection()
    conn.request("GET", "/api/v1/users?firstName=" + names[0] + "&lastName=" + names[1])
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    respJson = json.loads(response.read())
    userJson = respJson.get("user")
    assert_equal(userJson.get("active"), exp_active, "active status")

@step(u'user "(.*)" has id of (\d+)')
def user_foo_has_id_of_bar(step, name, id):
    names = name.split()
    conn = get_connection()
    conn.request("GET", "/api/v1/users?firstName=" + names[0] + "&lastName=" + names[1])
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    respJson = json.loads(response.read())
    userJson = respJson.get("user")
    assert_equal(userJson.get("resourceIdentity"), id, "matching resourceIdentity")

@step(u'(activate|deactivate) the user with id (\d+)')
def activate_deactivate_user_foo(step, action, userid):
    conn = get_connection()
    conn.request("PUT", "/api/v1/users/" + userid + "/" + action)
    response = conn.getresponse()
    assert_equal(response.status, 200, action +"ed user")



######################################################################

#                     ROLE STEPS

######################################################################

@step(u'logged in as "(.*)"')
def logged_in_as_user_foo(step, name):
    conn = get_connection()
    conn.request("GET", "/api/v1/users/current")
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    respJson = json.loads(response.read())
    userJson = respJson.get("user")

    names = name.split()
    assert_equal(userJson.get("firstname"), names[0], "First Name field didn't match")
    assert_equal(userJson.get("lastname"), names[1], "Last Name field didn't match")

@step(u'user "(.*)" has the role of (.*)')
def user_foo_has_the_role_of_bar(step, name, role):
    # This takes 2 requests to complete
    #    1: get the id of the user
    #    2: check that user has that role
    names = name.split()
    conn = get_connection()
    
    # fetch the user's resource identity
    conn.request("GET", "/api/v1/users?firstName=" + names[0] + "&lastName=" + names[1])
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    respJson = json.loads(response.read())
    userJson = respJson.get("user")
    assert_not_equal(userJson, None, "should not be empty")
    
    userid = userJson.get("resourceIdentity")

    conn.request("GET", "/api/v1/users/" + userid + "/roles")
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    respJson = json.loads(response.read())
    # walk through all roles for this user to see if it has the requested one
    roleJsonList = respJson.get("role")
    for roleJson in roleJsonList:
        foundRole = False
        if (roleJson.get("description") == role):
            foundRole = True
    assert_equal(foundRole, True, "looking for role of " + role)


@step(u'create a new role of "(.*)"')
def create_a_new_role_of_x(step, new_role):
    
    json_data = get_submit_role(new_role)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(json_data) }

    conn = get_connection()
    conn.request("POST", "/api/v1/roles", "", headers)
    conn.send(json_data)
    response = conn.getresponse()
    assert_equal(response.status, 200, "Create new role")
    

@step(u'add permission of "(.*)" to the role of "(.*)"')
def add_permission_foo_to_role_bar(step, permission, role):
    # this takes 2 requests.  
    #    1: get the id of this role
    #    2: add the permission to the role
    conn = get_connection()
    
    # fetch the user's resource identity
    conn.request("GET", "/api/v1/roles?description=" + role)
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a role")

    respJson = json.loads(response.read())
    
    roleJson = respJson.get("role")
    assert_not_equal(roleJson, None, "should not be empty")
    
    roleid = roleJson.get("resourceIdentity")

    post_payload = get_submit_permission(permission)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    conn.request("POST", "/api/v1/roles/" + roleid + "/permissions", "", headers)
    conn.send(post_payload)
    response = conn.getresponse()
    assert_equal(response.status, 200, "post new permission to role")



@step(u'role of "(.*)" has permission of "(.*)"')
def then_role_foo_has_permission_of_bar(step, role, permission):
    # This takes 2 requests to complete
    #    1: get the id of the role
    #    2: check that role has that permission
    conn = get_connection()
    
    # fetch the user's resource identity
    conn.request("GET", "/api/v1/roles?description=" + role)
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a role")

    respJson = json.loads(response.read())
    roleJson = respJson.get("role")
    assert_not_equal(roleJson, None, "should not be empty")
    
    roleid = roleJson.get("resourceIdentity")

    conn.request("GET", "/api/v1/roles/" + roleid + "/permissions")
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a permission")

    respJson = json.loads(response.read())
    # walk through all roles for this user to see if it has the requested one
    permJsonList = respJson.get("permission")
    for item in permJsonList:
        found = False
        if (item.get("description") == permission):
            found = True
    assert_equal(found, True, "looking for permission of " + permission)


@step(u'The system should have at least these roles:')
def the_system_should_have_at_least_these_roles(step):
    conn = get_connection()
    
    # fetch the user's resource identity
    conn.request("GET", "/api/v1/roles")
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched list of all roles")

    respJson = json.loads(response.read()).get("role")

    # now walk through the expected roles and check the response
    # to see that it is represented
    for exp_role in step.hashes:
        found = False
        for act_role in respJson:
            exp = exp_role.get("description")
            act = act_role.get("description")
            if (exp == act):
                found = True
        assert_equal(found, True, "expected role of: " + exp)


@step(u'"(.*)" role searches list "(.*)" before "(.*)"')
def order_role_searches_list_foor_before_bar(step, order, first, second):
    conn = get_connection()
    
    # fetch the user's resource identity
    conn.request("GET", "/api/v1/roles")
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched list of all roles")

    respJson = json.loads(response.read()).get("role")

    # now walk through the expected roles and check the response
    # to see that it is represented in the right order
    foundFirst = False
    foundSecond = False
    
    for act_role in respJson:
        act = act_role.get("description")
        if (first == act):
            foundFirst = True
            assert_equal(foundSecond, False, "found first, still haven't found second")
        if (second == act):
            foundSecond = True
            assert_equal(foundFirst, True, "found second, after finding first")

    # since it's possible to drop through here without finding one or the other, we have to check that 
    # both were actually found.
    assert_equal(foundFirst, True, "First was found")
    assert_equal(foundSecond, True, "Second was found")
    



######################################################################

#                     TEST CASE STEPS

######################################################################

# not implemented yet








#  Helper function
def get_submit_user(fname, lname):    
    user = """
        {
            "user":{
                "firstname":"%(fname)s",
                "lastname":"%(lname)s",
                "email":"%(fname)s%(lname)s@utest.com",
                "loginname":"%(fname)s%(lname)s",
                "password":"%(fname)s%(lname)s123",
                "companyid":1,
                "communitymember":"false"
            }
        }
    """ % {'fname': fname, 'lname': lname}
    returnStr = ""
    for line in user:
        returnStr += line.strip()
    return returnStr.encode('ascii', 'xmlcharrefreplace')

def get_submit_role(rolename):
    user = """
        {
            "role":{
                "description":"%(rolename)s"
            }
        }
    """ % {'rolename': rolename}
    returnStr = ""
    for line in user:
        returnStr += line.strip()
    return returnStr.encode('ascii', 'xmlcharrefreplace')
    
def get_submit_permission(permission_name):
    perm = """
        {
            "permission":{
                "description":"%(permission_name)s"
            }
        }
    """ % {'permission_name': permission_name}
    returnStr = ""
    for line in perm:
        returnStr += line.strip()
    return urllib.quote(returnStr)


