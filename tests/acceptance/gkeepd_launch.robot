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
    Email Exists    to_user=admin_prof    contains=Password
    User Exists    admin_prof
    User Exists    tester
    Gkeepd Is Running

Admin Account Already Exists
    [Tags]    error
    Add Account On Server    admin_prof
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Email Does Not Exist    admin_prof

Admin Named Faculty
    [Tags]    error
    Add File To Server    keeper    files/admin_named_faculty_server.cfg    server.cfg
    Start gkeepd
    Gkeepd Is Not Running
    User Does Not Exist    faculty
    Email Does Not Exist    faculty

Missing server cfg
    [Tags]    error
    Start gkeepd
    Gkeepd Is Not Running
    User Does Not Exist    admin_prof

Malformed server cfg
    [Tags]    error
    Add File To Server    keeper    files/malformed_server.cfg    server.cfg
    Start gkeepd
    Gkeepd Is Not Running
    User Does Not Exist    admin_prof
