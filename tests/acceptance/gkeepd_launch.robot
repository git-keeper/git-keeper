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
Test Setup    Reset Server
Force Tags    gkeepd_launch

*** Test Cases ***

Valid Setup
    [Tags]    happy_path
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    New Account Email Exists    admin_prof
    User Exists On Server    admin_prof
    User Exists On Server   tester
    Gkeepd Is Running

Admin Account Already Exists
    [Tags]    happy_path
    Add Account On Server    admin_prof
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    New Account Email Does Not Exist    admin_prof
    Gkeepd Is Running

Admin Named Faculty
    [Tags]    error
    Add File To Server    keeper    files/admin_named_faculty_server.cfg    server.cfg
    Start gkeepd
    Gkeepd Is Not Running
    User Does Not Exist On Server    faculty
    New Account Email Does Not Exist    faculty

Missing server cfg
    [Tags]    error
    Start gkeepd
    Gkeepd Is Not Running
    User Does Not Exist On Server    admin_prof

Malformed server cfg
    [Tags]    error
    Add File To Server    keeper    files/malformed_server.cfg    server.cfg
    Start gkeepd
    Gkeepd Is Not Running
    User Does Not Exist On Server    admin_prof

Multiple instances not allowed
    [Tags]    error
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Gkeepd Is Running
    Gkeepd fails
