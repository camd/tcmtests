'''
Created on Oct 7, 2010

@author: camerondawson
'''
from lettuce import *
import json
import httplib
import urllib
from numpy.ma.testutils import assert_equal

def get_connection():
    return httplib.HTTPConnection('localhost', 8080)

@before.each_scenario
def setup_scenario_data(scenario):
    conn = get_connection()
    scenarioData = get_scenario_data(scenario.name)
    headers = { 'content-Type':'text/plain',
            "Content-Length": "%d" % len(scenarioData) }

    conn.request("POST", "/api/v1/users/mockdata", "", headers)
    conn.send(scenarioData)
    conn.getresponse()
    
@step(u'user "(.*)" is (.*)registered')
def user_x_check_registration(step, name, registered):
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
def submit_information_for_username(step, name):
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
def user_has_active_status_x(step, name, exp_active):
    names = name.split()
    conn = get_connection()
    conn.request("GET", "/api/v1/users?firstName=" + names[0] + "&lastName=" + names[1])
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    respJson = json.loads(response.read())
    userJson = respJson.get("user")
    assert_equal(userJson.get("active"), exp_active, "active status")

@step(u'user "(.*)" has id of (\d+)')
def user_x_has_id_of_y(step, name, id):
    names = name.split()
    conn = get_connection()
    conn.request("GET", "/api/v1/users?firstName=" + names[0] + "&lastName=" + names[1])
    response = conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    respJson = json.loads(response.read())
    userJson = respJson.get("user")
    assert_equal(userJson.get("resourceidentity"), id, "matching resourceidentity")

@step(u'(activate|deactivate) the user with id (\d+)')
def activate_deactivate_user_x(step, action, userid):
    conn = get_connection()
    conn.request("PUT", "/api/v1/users/" + userid + "/" + action)
    response = conn.getresponse()
    assert_equal(response.status, 200, action +"ed user")











# Scenario Data
def get_scenario_data(scenarioName):
    data = ""
    if scenarioName == "Register a new user":
        data = """
            [
                {"status": "404","response": "User does not exist"},
                {"status": "200","response": "wazzon chokey"},
                {"status": "200","response": "%(activeFalse)s"},
                {"status": "200","response": "%(activeFalse)s"},
                {"status": "200","response": "%(activeTrue)s"}
            ]
        """ % \
        { 'activeFalse': get_returned_user("Jedi", "Jones", "false"),
          'activeTrue': get_returned_user("Jedi", "Jones", "true")}
    elif scenarioName == "Activate a Non Active user":
        data = """
            [
                {"status": "200","response": "%(activeFalse)s"},
                {"status": "200","response": "%(activeFalse)s"},
                {"status": "200","response": "%(activeFalse)s"},
                {"status": "200","response": "Activating user"},
                {"status": "200","response": "%(activeTrue)s"}
            ]
        """ % \
        { 'activeFalse': get_returned_user("Jedi", "NotActive", "false", "23"),
          'activeTrue': get_returned_user("Jedi", "NotActive", "true", "23")}
    elif scenarioName == "Deactivate an Active user":
        data = """
            [
                {"status": "200","response": "%(activeTrue)s"},
                {"status": "200","response": "%(activeTrue)s"},
                {"status": "200","response": "%(activeTrue)s"},
                {"status": "200","response": "Activating user"},
                {"status": "200","response": "%(activeFalse)s"}
            ]
        """ % \
        { 'activeFalse': get_returned_user("Jedi", "Active", "false", "24"),
          'activeTrue': get_returned_user("Jedi", "Active", "true", "24")}
    
    return data


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

#  Helper function
#         <?xml version="1.0" encoding="UTF-8" ?> 
def get_returned_user(fname, lname, active, resid="00"):    
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
                "resourceidentity":"%(resid)s",
                "timeline":"..."
            }
        }
    """ % {'fname': fname, 'lname': lname, 'active': active, 'resid': resid}
    returnStr = ""
    for line in user:
        returnStr += line.strip()
    return urllib.quote(returnStr)









