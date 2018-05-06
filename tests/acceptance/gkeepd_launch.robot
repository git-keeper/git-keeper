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
Library    gkeeprobot.keywords.ServerSetupKeywords
Library    gkeeprobot.keywords.ServerCheckKeywords
Test Setup    Reset Server
Force Tags    gkeepd_launch

*** Test Cases ***

One Faculty
    [Tags]    happy_path
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Expect Email    to_user=prof    contains=Password
    Server Running

Valid Setup
    [Tags]    happy_path
    Configure Faculty   prof    prof2
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Expect Email    to_user=prof    contains=Password
    Expect Email    to_user=prof2   contains=Password
    User Exists    prof
    User Exists    prof2
    User Exists    tester
    Server Running

Faculty Exists
    [Tags]    error
    Add Account On Server    prof
    Configure Faculty    prof
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Expect No Email    prof

Duplicate Faculty
    [Tags]    error
    Configure Faculty    prof
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Server Not Running
    User Does Not Exist    prof
    Expect No Email    prof

Faculty Named Faculty
    [Tags]    error
    Configure Faculty    faculty
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Server Not Running
    User Does Not Exist    faculty
    Expect No Email    faculty

Missing server cfg
    [Tags]    error
    Configure Faculty    prof
    Start gkeepd
    Server Not Running
    User Does Not Exist    prof

Missing faculty csv
    [Tags]    error
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Server Not Running

Malformed faculty csv
    [Tags]    error
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Add File To Server    keeper    files/malformed_faculty.csv    faculty.csv
    Start gkeepd
    Server Not Running
    User Does Not Exist    prof
    User Does Not Exist    prof2

Malformed server cfg
    [Tags]    error
    Configure Faculty    prof    prof2
    Add File To Server    keeper    files/malformed_server.cfg    server.cfg
    Start gkeepd
    Server Not Running
    User Does Not Exist    prof
    User Does Not Exist    prof2


