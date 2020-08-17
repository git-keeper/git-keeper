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
Force Tags    gkeep_test

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course  faculty1    cs1     student1    student2
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple


*** Test Cases ***


Test Produces Email to Faculty
    [Tags]  happy_path
    Gkeep Test Succeeds    faculty1    cs1    good_simple    good_simple/correct_solution
    Submission Test Results Email Exists    faculty1    cs1    good_simple    Done

Test Fails on Bad Course Name
    [Tags]  error
    Gkeep Test Fails    faculty1    bad_course    good_simple    good_simple/correct_solution

Test Fails on Bad Assignment Name
    [Tags]  error
    Gkeep Test Fails    faculty1    cs1    bad_name    good_simple/correct_solution

Test Fails on Bad Solution Path
    [Tags]  error
    Gkeep Test Fails    faculty1    cs1    good_simple    missing/path
