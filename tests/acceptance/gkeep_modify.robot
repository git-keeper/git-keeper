*** Settings ***
Library    gkeeprobot.keywords.ServerSetupKeywords
Library    gkeeprobot.keywords.ServerCheckKeywords
Library    gkeeprobot.keywords.ClientSetupKeywords
Library    gkeeprobot.keywords.ClientCheckKeywords
Resource    resources/setup.robot
Test Setup    Launch Gkeepd With Faculty    washington
Force Tags    gkeep_modify

*** Test Cases ***

Add Student
    [Tags]    happy_path
    Establish Course    washington    cs1    @{cs1_students}
    Add To Class    faculty=washington    class_name=cs1    student=piggy
    Gkeep Modify Succeeds    faculty=washington    class_name=cs1
    User Exists    piggy
    Expect Email    to_user=piggy    contains=Password
    Gkeep Query Contains    washington    students    piggy

Remove Student
    [Tags]    happy_path
    Establish Course    washington    cs1    @{cs1_students}
    Remove From Class    faculty=washington    class_name=cs1    student=gonzo
    Gkeep Modify Succeeds    faculty=washington    class_name=cs1
    Gkeep Query Does Not Contain    washington    students    gonzo

*** Keywords ***

Establish Course
    [Arguments]    ${faculty}    ${class}    @{students}
    Setup Faculty Accounts    ${faculty}
    :FOR     ${student}    IN    @{students}
    \    Add To Class    faculty=${faculty}    class_name=${class}    student=${student}
    Gkeep Add Succeeds    faculty=washington    class_name=cs1

*** Variables ***
@{cs1_students}    kermit    gonzo
