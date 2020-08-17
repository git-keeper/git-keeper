# Copyright 2020 Nathan Sommer and Ben Coleman
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
Force Tags    gkeep_status

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1

*** Test Cases ***

Close and Open
    [Tags]    happy_path
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    Gkeep Status Succeeds    faculty1    cs1    closed
    Gkeep Query JSON Produces Results    faculty1   classes   [{"name":"cs1","open":false}]
    Gkeep Status Succeeds    faculty1    cs1    open
    Gkeep Query JSON Produces Results    faculty1   classes   [{"name":"cs1","open":true}]

Opening Open
    [Tags]    error
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    Gkeep Status Fails    faculty1    cs1    open

Closing Closed
    [Tags]    error
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    Gkeep Status Succeeds    faculty1    cs1    closed
    Gkeep Status Fails    faculty1    cs1    closed
