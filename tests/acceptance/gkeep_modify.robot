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
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course    faculty1    cs1   student1    student2

*** Test Cases ***

Add Student
    [Tags]    happy_path
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student3
    Gkeep Modify Succeeds    faculty=faculty1    class_name=cs1
    User Exists On Server    student3
    New Account Email Exists    student3
    Class Contains Student    faculty1    cs1    student3

Remove Student
    [Tags]    happy_path
    Remove From Class    faculty=faculty1    class_name=cs1    student=student2
    Gkeep Modify Succeeds    faculty=faculty1    class_name=cs1
    Class Does Not Contain Student    faculty1    cs1    student2

Add Student Twice
    [Tags]    error
    Add To Class CSV    faculty=faculty1  class_name=cs1  username=student1
    Gkeep Modify Fails   faculty=faculty1    class_name=cs1

Malformed CSV
    [Tags]    error
    Add File To Client    faculty1    files/malformed_cs1.csv    cs1.csv
    Gkeep Modify Fails    faculty=faculty1    class_name=cs1

Remove Then Add Student
    [Tags]    happy_path
    Remove From Class    faculty=faculty1    class_name=cs1    student=student2
    Gkeep Modify Succeeds    faculty=faculty1    class_name=cs1
    Class Does Not Contain Student    faculty1    cs1    student2
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student2
    Gkeep Modify Succeeds    faculty=faculty1    class_name=cs1
    Class Contains Student    faculty1    cs1    student2

Change Student Name
    [Tags]    happy_path
    Add File To Client    faculty1    files/cs1_change_name.csv    cs1.csv
    Gkeep Modify Succeeds    faculty=faculty1    class_name=cs1
    Gkeep Query JSON Produces Results    faculty1   students   {"cs1":[{"first_name":"NewFirst","last_name":"NewLast","username":"student1","email_address":"student1@school.edu"},{"first_name":"First","last_name":"Last","username":"student2","email_address":"student2@school.edu"}]}
