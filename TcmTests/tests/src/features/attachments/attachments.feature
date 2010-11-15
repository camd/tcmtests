Feature: Attachments
    In order to attach files to test cases
    As Users
    We will implement attachment management

    Scenario: Upload a new Attachment to a test case
        Given I am logged in as user "Olivia Dunham"
        And I have the role of "ATTACHER"
        And test case with description "Trans-Universe Communication" exists
        when I upload attachment "Selectric251.txt" to test case "Trans-Universe Communication"
        Then test case "Trans-Universe Communication" has attachment "Selectric251.txt"
        
