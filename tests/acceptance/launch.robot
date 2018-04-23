
*** Settings ***
Library    gkeeprobot.keywords.ServerSetupKeywords
Library    gkeeprobot.keywords.ServerCheckKeywords
Test Teardown    Reset Server

**** Test Cases ****

Valid Setup
    Set Faculty CSV   prof    prof2
    Add File    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Expect Email    to_user=prof    contains=Password
    Expect Email    to_user=prof2   contains=Password
    User Exists    tester
    Server Running
    Stop gkeepd

Missing server cfg
    Set Faculty CSV    prof
    Start gkeepd
    Server Not Running
    User Does Not Exist    prof

Missing faculty csv
    Add File    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Server Not Running

Malformed faculty csv
    Add File    keeper    files/valid_server.cfg    server.cfg
    Add File    keeper    files/malformed_faculty.csv    faculty.csv
    Start gkeepd
    Server Not Running
    User Does Not Exist    prof
    User Does Not Exist    prof2

Malformed server cfg
    Set Faculty CSV    prof    prof2
    Add File    keeper    files/malformed_server.cfg    server.cfg
    Start gkeepd
    Server Not Running
    User Does Not Exist    prof
    User Does Not Exist    prof2


*** Keywords ***

Reset Server
    [Documentation]    All keywords succeed whether or not the user/file is present
    Remove User    prof
    Remove User    prof2
    Remove User    student
    Remove User    student2
    Remove User    tester
    Remove File    keeper    gkeepd.log
    Remove File    keeper    snapshot.json
    Remove File    keeper    faculty.csv
    Remove File    keeper    server.cfg
    Clear Email


