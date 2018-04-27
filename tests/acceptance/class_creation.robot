
*** Settings ***
Library    gkeeprobot.keywords.ServerSetupKeywords
Library    gkeeprobot.keywords.ServerCheckKeywords
Library    gkeeprobot.keywords.ClientSetupKeywords
Test Setup    Launch Server
Test Teardown    Run Keywords    Reset Server    Reset Client

*** Test Cases ***

Valid Class
    Create Accounts    washington    kermit    gonzo
    Establish SSH Keys    washington
    Create Gkeep Config File    washington
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Add To Class    faculty=washington    class_name=cs1    student=gonzo
    Run Gkeep Add    faculty=washington    class_name=cs1
    Establish SSH Keys    kermit
    Establish SSH Keys    gonzo
    User Exists    washington
    User Exists    kermit
    User Exists    gonzo
    Expect Email    to_user=kermit    contains=Password
    Expect Email    to_user=gonzo    contains=Password


*** Keywords ***

Launch Server
    Configure Faculty   washington    adams
    Add File    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd

Reset Server
    [Documentation]    All keywords succeed whether or not the user/file is present
    Stop gkeepd
    Remove Faculty
    Remove User    tester
    Remove File    keeper    gkeepd.log
    Remove File    keeper    snapshot.json
    Remove File    keeper    faculty.csv
    Remove File    keeper    server.cfg
    Clear Email

Reset Client
    Remove Students
    Remove Client User    washington