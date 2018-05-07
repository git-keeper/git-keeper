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
Test Setup    Launch Gkeepd With Faculty    washington
Force Tags    gkeep_modify

*** Test Cases ***

Add Student
    [Tags]    happy_path
    Establish Course    washington    cs1    @{cs1_students}
    Add To Class    faculty=washington    class_name=cs1    student=piggy
    Gkeep Modify Succeeds    faculty=washington    class_name=cs1
    User Exists    piggy
    Email Exists    to_user=piggy    contains=Password
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
