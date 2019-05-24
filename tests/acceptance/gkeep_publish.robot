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
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple

*** Test Cases ***
Valid Assignment Publish
    [Tags]  happy_path
    Gkeep Publish Succeeds  faculty1    cs1     good_simple

Bad Assignment Name In Publish
    [Tags]  error
    Gkeep Publish Fails     faculty1    cs1     unknown_name

Bad Course Name In Publish
    [Setup]     NONE
    Add Assignment to Client  faculty1  good_simple
    gkeep publish fails     faculty1    unknown_course      good_simple