Feature: Users Test Cases
    In order to work with test cases
    As Users
    We'll implement Test Case management

    Scenario: Create a new Test Case
        Given I am logged in as a user
        and I have the role of TestCreator
        When I request a new test case
        and enter the required fields
        Then a test case is created
