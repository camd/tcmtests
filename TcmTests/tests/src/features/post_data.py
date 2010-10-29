'''
######################################################################

                     DATA SUBMISSION HELPER FUNCTIONS

######################################################################
These functions generate data to be submitted in POST operations

Created on Oct 21, 2010
@author: camerondawson
'''
import urllib



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

    return urllib.quote(user)

def get_submit_role(rolename):
    user = """
        {
            "role":{
                "description":"%(rolename)s"
            }
        }
    """ % {'rolename': rolename}
    return urllib.quote(user)
    
def get_submit_permission(permission_name):
    perm = """
        {
            "permission":{
                "description":"%(permission_name)s"
            }
        }
    """ % {'permission_name': permission_name}

    return urllib.quote(perm)

def get_submit_test_case(description):
    tc = """
        {
            "testcase":{
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
                }
            }
        }
    """ % {'description': description}
    return urllib.quote(tc)
