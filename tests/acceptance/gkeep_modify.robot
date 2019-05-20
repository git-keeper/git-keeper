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
Resource    resources/setup.robot
Test Setup    Setup Server and Client Accounts
Force Tags    gkeep_modify

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    washington
    Establish Course    washington    cs1   kermit    gonzo

*** Test Cases ***

Add Student
    [Tags]    happy_path
    Add To Class    faculty=washington    class_name=cs1    student=piggy
    Gkeep Modify Succeeds    faculty=washington    class_name=cs1
    User Exists On Server    piggy
    Email Exists    to_user=piggy    contains=Password
    Gkeep Query Contains    washington    students    piggy

Remove Student
    [Tags]    happy_path
    Remove From Class    faculty=washington    class_name=cs1    student=gonzo
    Gkeep Modify Succeeds    faculty=washington    class_name=cs1
    Gkeep Query Does Not Contain    washington    students    gonzo

Add Student Twice
    [Tags]    error
    Add To Class    faculty=washington  class_name=cs1  student=kermit
    Gkeep Modify Fails   faculty=washington    class_name=cs1

Malformed CSV
    [Tags]    error
    Add File To Client    washington    files/malformed_cs1.csv    cs1.csv
    Gkeep Modify Fails    faculty=washington    class_name=cs1


