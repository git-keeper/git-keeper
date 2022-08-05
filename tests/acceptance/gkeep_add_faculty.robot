# Copyright 2018 Nathan Sommer and Ben Coleman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


*** Settings ***
Library    gkeeprobot.keywords.ServerSetupKeywords
Library    gkeeprobot.keywords.ServerCheckKeywords
Library    gkeeprobot.keywords.ServerWaitKeywords
Library    gkeeprobot.keywords.ClientSetupKeywords
Library    gkeeprobot.keywords.ClientCheckKeywords
Resource    resources/setup.robot
Test Setup    Launch Gkeepd And Configure Admin Account on Client
Force Tags    gkeep_add_faculty

*** Test Cases ***

Add One Faculty
    [Tags]    happy_path
    Gkeep Add Faculty Succeeds    admin_prof    faculty1
    New Account Email Exists    faculty1
    User Exists On Server    faculty1

Duplicate Faculty
    [Tags]    error
    Gkeep Add Faculty Succeeds    admin_prof    faculty1
    Wait For Email      to_user=faculty1    subject_contains="New git-keeper account"    body_contains=Password
    Gkeep Add Faculty Fails    admin_prof    faculty1
    Gkeepd Is Running

Add Faculty As Non Admin
    [Tags]    error
    Gkeep Add Faculty Succeeds    admin_prof    faculty1
    Wait For Email      to_user=faculty1    subject_contains="New git-keeper account"    body_contains=Password
    Create Accounts On Client    faculty1
    Gkeep Add Faculty Fails    faculty1    prof3
    Gkeepd Is Running

Different Case Email
    [Tags]    error
    Gkeep Add Faculty Succeeds    admin_prof    faculty1
    Gkeep Add Faculty Fails    admin_prof    FaCuLtY1
    Gkeep Add Faculty Fails    admin_prof    faculty1    email_domain='ScHoOl.EdU'

Uppercase Email
    [Tags]    happy_path
    Gkeep Add Faculty Succeeds    admin_prof    FACULTY1    email_domain='SCHOOL.EDU'
    New Account Email Exists    faculty1
    User Exists On Server    faculty1

Admin Promote And Demote
    [Tags]    happy_path
    Gkeep Add Faculty Succeeds    admin_prof    faculty1
    Create Accounts On Client    faculty1
    Gkeep Add Faculty Fails    faculty1    faculty2
    Gkeep Admin Promote Succeeds    admin_prof    faculty1
    Gkeep Admin Promote Fails    admin_prof    faculty1
    Gkeep Add Faculty Succeeds    faculty1    faculty2
    Gkeep Admin Demote Succeeds    faculty1    admin_prof
    Gkeep Admin Demote Fails    faculty1    admin_prof
    Gkeep Add Faculty Fails    admin_prof    faculty3
    Create Accounts On Client    faculty2
    Gkeep Add Faculty Fails    faculty2    faculty3
    Gkeep Admin Promote Succeeds    faculty1    faculty2
    Gkeep Admin Demote Succeeds    faculty2    faculty1
    Gkeep Add Faculty Fails    faculty1    faculty3
    Gkeepd Is Running

Add Faculty With Same Email Username
    [Tags]    happy_path
    Gkeep Add Faculty Succeeds    admin_prof    faculty1
    Gkeep Add Faculty Succeeds    admin_prof    faculty1     email_domain='gitkeeper.edu'

Faculty Named Faculty
    [Tags]    happy_path
    Gkeep Add Faculty Succeeds     admin_prof    faculty
    User Exists On Server    faculty1
    New Account Email Exists    faculty1

Faculty Named Keeper
    [Tags]    happy_path
    Gkeep Add Faculty Succeeds     admin_prof    keeper
    User Exists On Server    keeper1
    New Account Email Exists    keeper1
