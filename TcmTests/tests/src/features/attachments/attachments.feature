Feature: Attachments
    In order to attach files to test cases
    As Users
    We will implement attachment management

    Scenario: Create a new Attachment
        Given I am logged in as user "Peter Bishop"
        And user "Peter Bishop" has the role of "ATTACHER"
        And test case "transmute" exists
        when I add a new attachment with name "Electron Microscope"
        and attach "Electron Microscope" to test case "transmute"
        Then test case "transmute" has attachment "Electron Microscope"
        
