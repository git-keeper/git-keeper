# Copyright 2025 Nathan Sommer and Ben Coleman
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
Force Tags    gkeep_resend

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course    faculty1    cs1   student1    student2
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple

*** Test Cases ***

Resend Published Assignment For All Students
    [Tags]  happy_path
    Gkeep Publish Succeeds   faculty1   cs1    good_simple
    New Assignment Email Exists   student1   cs1   good_simple   1
    New Assignment Email Exists   student2   cs1   good_simple   1
    Gkeep Resend Succeeds    faculty1    cs1    good_simple
    New Assignment Email Exists   student1   cs1   good_simple  2
    New Assignment Email Exists   student2   cs1   good_simple  2

Resend Published Assignment For One Student
    [Tags]  happy_path
    Gkeep Publish Succeeds   faculty1   cs1    good_simple
    New Assignment Email Exists   student1   cs1   good_simple   1
    New Assignment Email Exists   student2   cs1   good_simple   1
    Gkeep Resend Succeeds    faculty1    cs1    good_simple    student1
    New Assignment Email Exists   student1   cs1   good_simple  2
    New Assignment Email Exists   student2   cs1   good_simple  1

Resend Published Assignment For Faculty
    [Tags]  happy_path
    Gkeep Publish Succeeds   faculty1   cs1    good_simple
    New Assignment Email Exists   faculty1   cs1   good_simple   1
    Gkeep Resend Succeeds    faculty1    cs1    good_simple    faculty1
    New Assignment Email Exists   faculty1   cs1   good_simple  2

Resend Unpublished Assignment For Faculty
    [Tags]  happy_path
    New Assignment Email Exists   faculty1   cs1   good_simple   1
    Gkeep Resend Succeeds    faculty1    cs1    good_simple    faculty1
    New Assignment Email Exists   faculty1   cs1   good_simple  2

Resend Unpublished Assignment For All Students
    [Tags]  error
    Gkeep Resend Fails    faculty1    cs1    good_simple

Resend Unpublished Assignment For One Student
    [Tags]  error
    Gkeep Resend Fails    faculty1    cs1    good_simple    student1
