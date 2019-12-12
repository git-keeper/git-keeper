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
Force Tags    gkeep_passwd

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1   faculty2
    Establish Course    faculty1    cs1   student1
    Establish Course    faculty2    cs2   student2

*** Test Cases ***

Reset Password
    [Tags]    happy_path
    Gkeep Passwd Succeeds    faculty=faculty1    username=student1
    Password Reset Email Exists    username=student1

Nonexistant Student
    [Tags]    error
    Gkeep Passwd Fails    faculty=faculty1    username=student3

Student Not In Faculty Class
    [Tags]    error
    Gkeep Passwd Fails    faculty=faculty1    username=student2
