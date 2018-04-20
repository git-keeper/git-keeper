
*** Settings ***
Library    robot_lib/VagrantControl.py
Suite Setup    Start vagrant
#Suite Teardown    Stop vagrant

**** Test Cases ****

New System Setup
    Start gkeepd
    Expect Email    to_user=prof    contains=Password
    Expect Email    to_user=prof2   contains=Password
    User Exists    tester
    Stop gkeepd
    Reset Server


*** Keywords ***

Reset Server
    Remove User    prof
    Remove User    prof2
    #Remove User    student
    #Remove User    student2
    Remove User    tester
    Remove File    keeper    gkeepd.log
    Remove File    keeper    snapshot.json
    Clear Email
