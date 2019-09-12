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
    Student Submits Correct Solution    student1    faculty1    cs1    good_simple
    Email Exists    student1    "[cs1] good_simple submission test results"

Bad Action.sh
    [Tags]  error
    Add Assignment to Client  faculty1  bad_action
    Gkeep Upload Succeeds   faculty1   cs1    bad_action
    Gkeep Publish Succeeds  faculty1    cs1     bad_action
    Clone Assignment  student1  faculty1    cs1     bad_action
    Student Submits Correct Solution    student1    faculty1    cs1    bad_action
    Email Exists    student1    "bad_action: Failed to process submission - contact instructor"


