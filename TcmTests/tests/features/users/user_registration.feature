Feature: New Users
    In order to have a user base
    As a User
    I want to be able to register

    Scenario: Register a new user
        Given user "Jedi Jones" is not registered
        When I submit information for "Jedi Jones"
        Then user "Jedi Jones" is registered
        And user "Jedi Jones" has active status "false"
        
    Scenario: Activate a Non Active user
        Given user "Jedi NotActive" is registered
        And user "Jedi NotActive" has active status "false"
        And user "Jedi NotActive" has id of 23
        When I activate the user with id 23
        Then user "Jedi NotActive" has active status "true"
    
    Scenario: Deactivate an Active user
        Given user "Jedi Active" is registered
        And user "Jedi Active" has active status "true"
        And user "Jedi Active" has id of 24
        When I deactivate the user with id 24
        Then user "Jedi Active" has active status "false"
    