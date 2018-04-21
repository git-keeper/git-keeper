
*** Settings ***
Library    robot_lib/VagrantControl.py
Suite Setup    Vagrant Setup
Suite Teardown    Vagrant Teardown

**** Test Cases ****

New System Setup
    Start gkeepd
    Expect Email    to_user=prof    contains=Password
    Expect Email    to_user=prof2   contains=Password
    User Exists    tester
    Stop gkeepd
    Reset Server


*** Keywords ***

Vagrant Setup
    Make Boxes if Missing
    Start vagrant   ${VAGRANT_START_FLAG}

Vagrant Teardown
    Stop Vagrant    ${VAGRANT_STOP_FLAG}

Reset Server
    Remove User    prof
    Remove User    prof2
    #Remove User    student
    #Remove User    student2
    Remove User    tester
    Remove File    keeper    gkeepd.log
    Remove File    keeper    snapshot.json
    Clear Email


*** Variables ***
# use --variable VAGRANT_START_FLAG:False to change behavior
${VAGRANT_START_FLAG}    ${True}
${VAGRANT_STOP_FLAG}    ${True}