
*** Settings ***
Library    gkeeprobot.keywords.VagrantKeywords
Library    gkeeprobot.keywords.ServerKeywords
Suite Setup    Vagrant Setup
Suite Teardown    Vagrant Teardown

**** Test Cases ****

New System Setup
    Set Faculty    prof    prof2
    Add File    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Expect Email    to_user=prof    contains=Password
    Expect Email    to_user=prof2   contains=Password
    User Exists    tester
    Stop gkeepd
    Reset Server


*** Keywords ***

Vagrant Setup
    Make Boxes if Missing
    Start Vagrant   ${ROBOT_CONTROLS_VAGRANT}

Vagrant Teardown
    Stop Vagrant    ${ROBOT_CONTROLS_VAGRANT}

Reset Server
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


*** Variables ***
${ROBOT_CONTROLS_VAGRANT}    No
