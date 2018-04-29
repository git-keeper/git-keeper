
*** Settings ***
Library    gkeeprobot.keywords.ServerSetupKeywords
Library    gkeeprobot.keywords.ServerCheckKeywords
Library    gkeeprobot.keywords.ClientSetupKeywords
Library    gkeeprobot.keywords.ClientCheckKeywords
Test Setup    Launch Server

*** Test Cases ***

Valid Class
    Setup Faculty Account    washington
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Add To Class    faculty=washington    class_name=cs1    student=gonzo
    Gkeep Add Succeeds    faculty=washington    class_name=cs1
    User Exists    kermit
    User Exists    gonzo
    Expect Email    to_user=kermit    contains=Password
    Expect Email    to_user=gonzo    contains=Password

Missing CSV
    Setup Faculty Account    washington
    Gkeep Add Fails    faculty=washington    class_name=cs1

Existing Student
    Setup Faculty Account    washington
    Add Account on Server    gonzo
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Add To Class    faculty=washington    class_name=cs1    student=gonzo
    Gkeep Add Succeeds    faculty=washington    class_name=cs1
    User Exists    kermit
    User Exists    gonzo
    Expect Email    to_user=kermit    contains=Password
    Expect No Email    to_user=gonzo

Call Add Twice
    Setup Faculty Account    washington
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Gkeep Add Succeeds    faculty=washington    class_name=cs1
    Gkeep Add Fails    faculty=washington    class_name=cs1

Duplicate Student
    Setup Faculty Account    washington
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Gkeep Add Fails    faculty=washington    class_name=cs1

Malformed CSV
    Setup Faculty Account    washington
    Add File To Client    washington    files/malformed_cs1.csv    cs1.csv
    Gkeep Add Fails    faculty=washington    class_name=cs1

Student Named Student
    Setup Faculty Account    washington
    Add To Class    faculty=washington    class_name=cs1    student=student
    Gkeep Add Fails    faculty=washington    class_name=cs1

Duplicate Class Name
    Setup Faculty Account    washington
    Setup Faculty Account    adams
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Gkeep Add Succeeds    faculty=washington    class_name=cs1
    Add To Class    faculty=adams    class_name=cs1    student=kermit
    Gkeep Add Fails    faculty=adams    class_name=cs1

Empty CSV
    Setup Faculty Account    washington
    Make Empty File    washington    cs1.csv
    Gkeep Add Fails    faculty=washington    class_name=cs1

*** Keywords ***

Launch Server
    Reset Server
    Reset Client
    Configure Faculty   washington    adams
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd

Setup Faculty Account
    [Arguments]    ${username}
    Create Accounts    ${username}
    Establish SSH Keys    ${username}
    Create Gkeep Config File    ${username}
