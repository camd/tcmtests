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

