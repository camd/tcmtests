Feature: User Administration
    In order to update an existing user
    As an Administrator
    I want to be able to change user values

    Scenario: Activate an unactivated user
        Given I am logged in as an administrator
        And User Fligoogigoogee exists, but is not activated
        When I activate Fligugigugee
        Then Fligugigugee is activated
        
    Scenario: Deactivate an Activated User
    Scenario: Assign a role to a User
    Scenario: Delete a role from a User
    Scenario: Check roles for a User
    Scenario: Check the assignments of a User
    Scenario: Update User information
    Scenario: Change User's password
    Scenario: Get specific User by id
    Scenario: Search for Users
    
    