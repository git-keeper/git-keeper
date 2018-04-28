
*** Settings ***
Library    gkeeprobot.keywords.ServerSetupKeywords
Library    gkeeprobot.keywords.ServerCheckKeywords
Test Setup    Reset Server

*** Test Cases ***

Valid Setup
    Configure Faculty   prof    prof2
    Add File    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Expect Email    to_user=prof    contains=Password
    Expect Email    to_user=prof2   contains=Password
    User Exists    prof
    User Exists    prof2
    User Exists    tester
    Server Running

Faculty Exists
    Add Account On Server    prof
    Configure Faculty    prof
    Add File    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Expect No Email    prof

Missing server cfg
    Configure Faculty    prof
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
    Configure Faculty    prof    prof2
    Add File    keeper    files/malformed_server.cfg    server.cfg
    Start gkeepd
    Server Not Running
    User Does Not Exist    prof
    User Does Not Exist    prof2


