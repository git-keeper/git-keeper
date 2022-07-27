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
Force Tags    gkeepd_launch

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course  faculty1    cs1     student1
    Create Accounts On Client    student1
    Create Git Config    student1

*** Test Cases ***

Student Submits Correct Solution
    [Tags]  happy_path
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple
    Gkeep Publish Succeeds  faculty1    cs1     good_simple
    Clone Assignment  student1  faculty1    cs1     good_simple
    Student Submits    student1    faculty1    cs1    good_simple    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_simple    Done

Student Submit From Other Branch
    [Tags]  error
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple
    Gkeep Publish Succeeds  faculty1    cs1     good_simple
    Clone Assignment  student1  faculty1    cs1     good_simple
    Student Submits    student1    faculty1    cs1     good_simple    correct_solution    branch=other    expect_failure=True
    Submission Test Results Email Does Not Exist    student1    cs1     good_simple     Done

Student Submits Python Action Solution
    [Tags]  happy_path
    Add Assignment to Client  faculty1  good_action_py
    Gkeep Upload Succeeds   faculty1   cs1    good_action_py
    Gkeep Publish Succeeds  faculty1    cs1     good_action_py
    Clone Assignment  student1  faculty1    cs1     good_action_py
    Student Submits    student1    faculty1    cs1    good_action_py    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_action_py    Done

Bad Action.sh
    [Tags]  error
    Add Assignment to Client  faculty1  bad_action
    Gkeep Upload Succeeds   faculty1   cs1    bad_action
    Gkeep Publish Succeeds  faculty1    cs1     bad_action
    Clone Assignment  student1  faculty1    cs1     bad_action
    Student Submits    student1    faculty1    cs1    bad_action    correct_solution
    Email Exists    student1    subject_contains="bad_action: Failed to process submission - contact instructor"    body_contains="instructor"

Duplicate Assignment Name Across Courses Managed
    [Tags]    happy_path
    Establish Course    faculty1   cs2    student1
    Add Assignment to Client  faculty1  good_simple
    # good_simple used in cs1
    Gkeep Upload Succeeds   faculty1   cs1    good_simple
    Gkeep Publish Succeeds  faculty1    cs1     good_simple
    Clone Assignment  student1  faculty1    cs1     good_simple
    Student Submits    student1    faculty1    cs1    good_simple    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_simple    Done
    # good_simple used in cs2
    Gkeep Upload Succeeds   faculty1   cs2    good_simple
    Gkeep Publish Succeeds  faculty1    cs2     good_simple
    Clone Assignment  student1  faculty1    cs2     good_simple
    Student Submits    student1    faculty1    cs2    good_simple    correct_solution
    Submission Test Results Email Exists    student1    cs2    good_simple    Done

Submissions While Gkeepd is Down
    [Tags]    happy_path
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple
    Gkeep Publish Succeeds  faculty1    cs1     good_simple
    Clone Assignment  student1  faculty1    cs1     good_simple
    Stop Gkeepd
    gkeepd is not running
    Student Submits    student1    faculty1    cs1    good_simple    correct_solution
    Submission Test Results Email Does Not Exist    student1    cs1    good_simple    Done
    Start gkeepd
    Submission Test Results Email Exists    student1    cs1    good_simple    Done

Global Timeout Catches Infinite Loop
    [Tags]    happy_path
    Add Assignment to Client  faculty1  run_py
    Gkeep Upload Succeeds   faculty1   cs1    run_py
    Gkeep Publish Succeeds  faculty1    cs1     run_py
    Clone Assignment  student1  faculty1    cs1     run_py
    Student Submits    student1    faculty1    cs1    run_py    infinite_loop_submission
    Submission Test Results Email Exists    student1   cs1   run_py   "Tests timed out"
