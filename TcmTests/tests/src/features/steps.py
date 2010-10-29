'''
Created on Oct 7, 2010

@author: camerondawson
'''
from lettuce import *
from nose.tools import *
from numpy.ma.testutils import *
import httplib
import json
import mock_scenario_data
import post_data
import urllib
import urllib2

host = "http://localhost:8080"

def get_connection():
    return httplib.HTTPConnection('localhost', 8080)

#
# DATA SETUP
# This is the function that uploads the expected data to the mock server.
#
# @todo Need to make this only run in DEBUG mode or something
@before.each_scenario
def setup_scenario_data(scenario):
    scenarioData = mock_scenario_data.get_scenario_data(scenario.name).strip()
#    print scenarioData
#    scenarioData = scenarioData.zfill(8000)

    headers = { 'content-Type':'text/plain',
            "Content-Length": "%d" % len(scenarioData) }
#    headers = { 'content-Type':'application/x-www-form-urlencoded',
#            "Content-Length": "%d" % len(scenarioData) }


    conn = get_connection()
    conn.request("POST", "/api/v1/mockdata?scenario=" + urllib.quote(scenario.name), "", headers)

#    conn.send(urllib.urlencode({"data": scenarioData}))
    conn.send(scenarioData)
    conn.getresponse()

'''
######################################################################

                     USER STEPS

######################################################################
'''
    
@step(u'user "(.*)" is (.*)registered')
def user_foo_check_registration(step, name, registered):
    names = name.split()
        
    conn = get_connection()
    conn.request("GET", "/api/v1/users?firstName=" + names[0] + "&lastName=" + names[1])
    response = conn.getresponse()

    if registered.strip() == "not":
        assert_equal(response.status, 404, "registration status")
    else:
        assert_equal(response.status, 200, "registration status")

        userJson = get_single_item(response, "user")
        assert_equal(userJson.get("firstname"), names[0], "First Name field didn't match")
        assert_equal(userJson.get("lastname"), names[1], "Last Name field didn't match")


@step(u'submit information for "(.*)"')
def submit_information_for_user_foo(step, name):
    names = name.split()
    
    xml_data = post_data.get_submit_user(names[0], names[1])
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

    userJson = get_single_item(response, "user")
    assert_equal(userJson.get("active"), exp_active, "active status")

# @TODO This function may not be useful.  Possibly dead code
@step(u'user "(.*)" has id of (\d+)')
def user_foo_has_id_of_bar(step, name, exp_id):
    act_id = get_user_resid(name)

    assert_equal(act_id, exp_id, "matching resourceIdentity")

@step(u'(activate|deactivate) user "(.*)"')
def activate_deactivate_user_foo(step, action, name):
    conn = get_connection()
    user_id = get_user_resid(name)
    
    conn.request("PUT", "/api/v1/users/" + user_id + "/" + action)
    response = conn.getresponse()
    assert_equal(response.status, 200, action +"ed user")

@step(u'"(.*)" has these roles:')
def foo_has_these_roles(step, name):
    user_id = get_user_resid(name)
    conn = get_connection()
    conn.request("GET", "/api/v1/users/" + user_id + "/roles")
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    # walk through all roles for this user to see if it has the requested one
    respJson = json.loads(response.read()).get("role")

    # now walk through the expected roles and check the response
    # to see that it is represented
    roles = step.hashes
    for exp_role in roles:
        found = False
        for act_role in respJson:
            exp = exp_role.get("description")
            act = act_role.get("description")
            if (exp == act):
                found = True
        assert_equal(found, True, "expected role of: " + exp)

@step(u'"(.*)" has these assignments:')
def foo_has_these_assignments(step, name):
    user_id = get_user_resid(name)
    conn = get_connection()
    conn.request("GET", "/api/v1/users/" + user_id + "/assignments")
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    # walk through all roles for this user to see if it has the requested one
    respJson = json.loads(response.read()).get("testcase")

    # now walk through the expected roles and check the response
    # to see that it is represented
    exp_list = step.hashes
    for exp_item in exp_list:
        found = False
        for act_item in respJson:
            exp = exp_item.get("description")
            act = act_item.get("description")
            if (exp == act):
                found = True
        assert_equal(found, True, "expected assignment of: " + exp)


'''
######################################################################

                     ROLE STEPS

######################################################################
'''


@step(u'logged in as "(.*)"')
def logged_in_as_user_foo(step, name):
    conn = get_connection()
    conn.request("GET", "/api/v1/users/current")
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    thisUser = get_single_item(response, "user")

    names = name.split()
    assert_equal(thisUser.get("firstname"), names[0], "First Name field didn't match")
    assert_equal(thisUser.get("lastname"), names[1], "Last Name field didn't match")

@step(u'"(.*)" has the role of "(.*)"')
def user_foo_has_the_role_of_bar(step, name, role):
    user_role_check(name, role, True, "should have role of " + role)

@step(u'"(.*)" does not already have the role of "(.*)"')
def foo_does_not_already_have_the_role_of_bar(step, name, role):
    user_role_check(name, role, False, "should not have role of " + role)

def user_role_check(name, role, expected_tf, assert_text):
    # This takes 2 requests to complete
    #    1: get the id of the user
    #    2: check that user has that role
    conn = get_connection()
    
    # fetch the user's resource identity
    user_id = get_user_resid(name)
    conn.request("GET", "/api/v1/users/" + user_id + "/roles")
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    respJson = json.loads(response.read())
    # walk through all roles for this user to see if it has the requested one
    roleJsonList = respJson.get("role")

    foundRole = False
    for roleJson in roleJsonList:
        if (roleJson.get("description") == role):
            foundRole = True
    assert_equal(foundRole, expected_tf, assert_text)

@step(u'add role of "(.*)" to user "(.*)"')
def add_role_of_foo_to_user_bar(step, role, name):
    '''
    # this takes 2 requests.  
    #    1: get the id of this user
    #    2: add the role to the user
    '''
    conn = get_connection()
    
    # fetch the role's resource identity
    user_id = get_user_resid(name)
    
    post_payload = post_data.get_submit_role(role)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    conn.request("POST", "/api/v1/users/" + user_id + "/roles", "", headers)
    conn.send(post_payload)
    response = conn.getresponse()
    assert_equal(response.status, 200, "post new role to user")

@step(u'create a new role of "(.*)"')
def create_a_new_role_of_x(step, new_role):
    
    json_data = post_data.get_submit_role(new_role)
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
    
    # fetch the role's resource identity
    role_id = get_role_resid(role)
    
    post_payload = post_data.get_submit_permission(permission)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    conn.request("POST", "/api/v1/roles/" + role_id + "/permissions", "", headers)
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
    role_id = get_role_resid(role)

    conn.request("GET", "/api/v1/roles/" + role_id + "/permissions")
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

@step(u'role of "(.*)" exists')
def role_of_foo_exists(step, role):
    check_role_existence([{"description": role}])
    

@step(u'at least these roles exist:')
def at_least_these_roles_exist(step):
    check_role_existence(step.hashes)
    
def check_role_existence(roles):
    conn = get_connection()
    
    # fetch the user's resource identity
    conn.request("GET", "/api/v1/roles")
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched list of all roles")

    respJson = json.loads(response.read()).get("role")

    # now walk through the expected roles and check the response
    # to see that it is represented
    for exp_role in roles:
        found = False
        for act_role in respJson:
            exp = exp_role.get("description")
            act = act_role.get("description")
            if (exp == act):
                found = True
        assert_equal(found, True, "expected role of: " + exp)


@step(u'"(.*)" role searches list "(.*)" before "(.*)"')
def order_role_searches_list_foo_before_bar(step, order, first, second):
    conn = get_connection()
    
    # fetch the user's resource identity
    conn.request("GET", "/api/v1/roles?sortDirection=" + order)
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
    

'''
######################################################################

                     TEST CASE STEPS

######################################################################
'''

@step(u'submit a new test case with description "(.*)"')
def submit_a_new_test_case_with_description_foo(step, description):
    conn = get_connection()
    post_payload = post_data.get_submit_test_case(description)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    conn.request("POST", "/api/v1/testcases", "", headers)
    conn.send(post_payload)
    response = conn.getresponse()
    assert_equal(response.status, 200, "create new testcase")

@step(u'test case exists with description "(.*)"')
def test_case_exists_with_description_foo(step, description):
    conn = get_connection()
    
    conn.request("GET", "/api/v1/testcases?description=" + urllib.quote(description))
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched testcase")

    respJson = json.loads(response.read())
    # walk through all the testcases for this user to see if it has the requested one
    roleJsonList = respJson.get("testcase")

    found = False
    for item in roleJsonList:
        if (item.get("description") == description):
            found = True
    assert_equal(found, True, "looking for testcase desc of " + description)





'''
######################################################################

                     HELPER FUNCTIONS

######################################################################
'''

def get_single_item(response, type):
    '''
        Expect the response to hold an array of 1 and only 1 item.  Throw an error
        if not.  Returns just the first item of that type.
    '''
    respJson = json.loads(response.read())
    # in this case, we only care about the first returned item in this array
    arrayJson = respJson.get(type)
    assert_equal(len(arrayJson), 1, "should only have 1 item of type: " + type)
    return arrayJson[0]


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
        
        @TODO: This presumes an array of objects is returned.  So it ONLY returns the resid for
        the first element of the array.  Will almost certainly need a better solution in the future.
        Like a new method "get_resource_identities" which returns an array of ids or something.  
    '''
    conn = get_connection()
    conn.request("GET", uri)
    response = conn.getresponse()
    assert_equal(response.status, 200, "Response when asking for " + type)

    respJson = json.loads(response.read())
    objJson = respJson.get(type)
    return objJson[0].get("resourceIdentity")


