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
Force Tags    gkeep_upload

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course  faculty1    cs1     student1  student2

*** Test Cases ***
Valid Assignment Upload
    [Tags]  happy_path
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple
    New Assignment Email Exists    faculty1    cs1    good_simple
    Clone Assignment    faculty1  faculty1  cs1  good_simple
    gkeep query contains  faculty1    assignments  U good_simple

Missing Email
    [Tags]  error
    Add Assignment to Client  faculty1  missing_email
    Gkeep Upload Fails   faculty1   cs1    missing_email

Missing Base Code
    [Tags]  error
    Add Assignment to Client  faculty1  missing_base
    Gkeep Upload Fails   faculty1   cs1    missing_base

Missing Base Action_sh
    [Tags]  error
    Add Assignment to Client  faculty1  missing_action
    Gkeep Upload Fails   faculty1   cs1    missing_action

Missing Base Tests
    [Tags]  error
    Add Assignment to Client  faculty1  missing_tests
    Gkeep Upload Fails   faculty1   cs1    missing_tests

Double Assignment Upload
    [Tags]  error
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple
    Gkeep Upload Fails   faculty1   cs1    good_simple

Assignment Named all
    [Tags]  error
    Add Assignment to Client  faculty1  all
    Gkeep Upload Fails  faculty1  cs1  all

Assignment Named tests
    [Tags]  error
    Add Assignment to Client  faculty1  tests
    Gkeep Upload Fails  faculty1  cs1  tests
