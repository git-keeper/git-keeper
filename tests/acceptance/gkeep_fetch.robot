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
Force Tags    gkeep_fetch

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1    faculty2
    Establish Course  faculty1    cs1     student1    student2
    Create Accounts On Client    student1    student2
    Create Git Config    student1
    Create Git Config    student2
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple
    Gkeep Publish Succeeds  faculty1    cs1     good_simple
    Clone Assignment  student1  faculty1    cs1     good_simple
    Student Submits    student1    faculty1    cs1    good_simple    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_simple    Done


*** Test Cases ***

Fetch After Student Submission
    [Tags]  happy_path
    Fetch Assignment    faculty1    cs1    good_simple    fetched_assignments
    Verify Submission Count   faculty1    fetched_assignments    cs1    good_simple    student1    1
    Verify Submission Count   faculty1    fetched_assignments    cs1    good_simple    student2    0

Second Fetch Updates Submissions
    [Tags]  happy_path
    Fetch Assignment    faculty1    cs1    good_simple    fetched_assignments
    Verify Submission Count   faculty1    fetched_assignments    cs1    good_simple    student1    1
    Verify Submission Count   faculty1    fetched_assignments    cs1    good_simple    student2    0
    # Student 2 submits and then re-fetch
    Clone Assignment  student2  faculty1    cs1     good_simple
    Student Submits    student2    faculty1    cs1    good_simple    correct_solution
    Submission Test Results Email Exists    student2    cs1    good_simple    Done
    Fetch Assignment    faculty1    cs1    good_simple    fetched_assignments
    Verify Submission Count   faculty1    fetched_assignments    cs1    good_simple    student1    1
    Verify Submission Count   faculty1    fetched_assignments    cs1    good_simple    student2    1

Fetch to Submissions Folder
    [Tags]  happy_path
    Add Submissions Folder to Config    faculty1    ~/submissions
    Fetch Assignment    faculty1    cs1    good_simple
    Verify Submission Count   faculty1    submissions    cs1    good_simple    student1    1
    Verify Submission Count   faculty1    submissions    cs1    good_simple    student2    0



