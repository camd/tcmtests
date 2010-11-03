Feature: Environment Administration
    In order to support multiple environments
    As an Administrator
    I want to be able to administer environment entries
    
    Scenario: Create a new Environment
        Given I am logged in as user "Jedi Creator"
        And user "Jedi Creator" has the role of "ENVIRONMENT_CREATOR"
        And environment "Walter's Lab" does not exist
        when I add a new environment with name "Walter's Lab"
        Then environment "Walter's Lab" exists

    Scenario: Create a new Environment Type
        Given I am logged in as user "Jedi Creator"
        And user "Jedi Creator" has the role of "ENVIRONMENT_CREATOR"
        And environment type "Laboratory" does not exist
        when I add a new environment type with name "Laboratory"
        Then environment type "Laboratory" exists
        