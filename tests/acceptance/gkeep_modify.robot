*** Settings ***
Library    gkeeprobot.keywords.ServerSetupKeywords
Library    gkeeprobot.keywords.ServerCheckKeywords
Library    gkeeprobot.keywords.ClientSetupKeywords
Library    gkeeprobot.keywords.ClientCheckKeywords
Resource    resources/setup.robot
Test Setup    Launch Gkeepd With Faculty    washington
Force Tags    gkeep_modify

*** Test Cases ***

Add Student To Course
    [Tags]    happy_path
    Setup Faculty Accounts    washington
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Add To Class    faculty=washington    class_name=cs1    student=gonzo
    Gkeep Add Succeeds    faculty=washington    class_name=cs1

    Add To Class    faculty=washington    class_name=cs1    student=piggy
    Gkeep Modify Succeeds    faculty=washington    class_name=cs1
    User Exists    piggy
    Expect Email    to_user=piggy    contains=Password
    Gkeep Query Contains    washington    students    piggy



