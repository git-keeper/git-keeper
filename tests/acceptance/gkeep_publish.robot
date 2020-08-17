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
Force Tags    gkeep_publish

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course  faculty1    cs1     student1  student2
    Create Accounts On Client   student1    student2
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple

*** Test Cases ***
Valid Assignment Publish
    [Tags]  happy_path
    Gkeep Publish Succeeds  faculty1    cs1     good_simple
    New Assignment Email Exists    student1    cs1    good_simple
    New Assignment Email Exists    student2    cs1    good_simple
    Clone Assignment  student1  faculty1    cs1     good_simple
    Clone Assignment  student2  faculty1    cs1     good_simple

Bad Assignment Name In Publish
    [Tags]  error
    Gkeep Publish Fails     faculty1    cs1     unknown_name

Bad Course Name In Publish
    Gkeep Publish Fails     faculty1    unknown_course      good_simple

Publish Twice
    [Tags]  error
    Gkeep Publish Succeeds  faculty1    cs1     good_simple
    Gkeep Publish Fails     faculty1    cs1     good_simple

Double Upload Then Double Publish
    [Tags]  happy_path
    Add Assignment To Client  faculty1  good_simple2
    Gkeep Upload Succeeds   faculty1   cs1    good_simple2
    # Publish 1st assignment
    Gkeep Publish Succeeds  faculty1    cs1     good_simple
    New Assignment Email Exists    student1    cs1    good_simple
    New Assignment Email Exists    student2    cs1    good_simple
    Clone Assignment  student1  faculty1    cs1     good_simple
    Clone Assignment  student2  faculty1    cs1     good_simple
    # Publish 2nd assignment
    Gkeep Publish Succeeds  faculty1    cs1     good_simple2
    New Assignment Email Exists    student1    cs1    good_simple2
    New Assignment Email Exists    student2    cs1    good_simple2
    Clone Assignment  student1  faculty1    cs1     good_simple2
    Clone Assignment  student2  faculty1    cs1     good_simple2

Interleave Upload and Publish
    [Tags]  happy_path
    Add Assignment To Client  faculty1  good_simple2
    Gkeep Upload Succeeds   faculty1   cs1    good_simple2
    # Publish 2nd assignment
    Gkeep Publish Succeeds  faculty1    cs1     good_simple2
    New Assignment Email Exists    student1    cs1    good_simple2
    New Assignment Email Exists    student2    cs1    good_simple2
    Clone Assignment  student1  faculty1    cs1     good_simple2
    Clone Assignment  student2  faculty1    cs1     good_simple2
    # Publish 1st assignment
    Gkeep Publish Succeeds  faculty1    cs1     good_simple
    New Assignment Email Exists    student1    cs1    good_simple
    New Assignment Email Exists    student2    cs1    good_simple
    Clone Assignment  student1  faculty1    cs1     good_simple
    Clone Assignment  student2  faculty1    cs1     good_simple
