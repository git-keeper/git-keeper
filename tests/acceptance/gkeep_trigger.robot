# Copyright 2019 Nathan Sommer and Ben Coleman
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
Force Tags    gkeep_trigger

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course    faculty1    cs1   student1    student2
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple

*** Test Cases ***

Published Assignment For All Students
    [Tags]  happy_path
    Gkeep Publish Succeeds   faculty1   cs1    good_simple
    Gkeep Trigger Succeeds   faculty1   cs1    good_simple
    Submission Test Results Email Exists   student1   cs1   good_simple   Unpushed
    Submission Test Results Email Exists   student2   cs1   good_simple   Unpushed
    Submission Test Results Email Does Not Exist  faculty1   cs1    good_simple  Unpushed

Published Assignment For One Student
    [Tags]  happy_path
    Gkeep Publish Succeeds   faculty1   cs1    good_simple
    Gkeep Trigger Succeeds   faculty1   cs1    good_simple    student1
    Submission Test Results Email Exists    student1    cs1    good_simple    Unpushed
    Submission Test Results Email Does Not Exist  student2   cs1    good_simple    Unpushed
    Submission Test Results Email Does Not Exist  faculty1   cs1    good_simple    Unpushed

Published Assignment For Faculty
    [Tags]  happy_path
    Gkeep Publish Succeeds   faculty1   cs1    good_simple
    Gkeep Trigger Succeeds   faculty1   cs1    good_simple    faculty1
    Submission Test Results Email Exists    faculty1    cs1    good_simple    Unpushed
    Submission Test Results Email Does Not Exist  student1   cs1    good_simple    Unpushed
    Submission Test Results Email Does Not Exist  student2   cs1    good_simple    Unpushed

Unpublished Assignment For Faculty
    [Tags]  happy_path
    Gkeep Trigger Succeeds   faculty1   cs1    good_simple    faculty1
    Submission Test Results Email Exists    faculty1    cs1    good_simple    Unpushed
    Submission Test Results Email Does Not Exist  student1   cs1    good_simple    Unpushed
    Submission Test Results Email Does Not Exist  student2   cs1    good_simple    Unpushed

Unpublished Assignment For All Students
    [Tags]  error
    Gkeep Trigger Fails   faculty1   cs1    good_simple

Unpublished Assignment For One Student
    [Tags]  error
    Gkeep Trigger Fails   faculty1   cs1    good_simple    student1
