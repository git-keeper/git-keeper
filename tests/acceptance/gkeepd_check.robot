# Copyright 2022 Nathan Sommer and Ben Coleman
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
Force Tags    gkeepd_check

*** Test Cases ***

Check Valid Setup
    [Tags]    happy_path
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Gkeepd Check Succeeds
    Gkeepd Check Email Exists    admin_prof
    Gkeepd Is Not Running
    User Does Not Exist On Server    admin_prof

Check Valid Setup While Gkeepd Is Running
    [Tags]    happy_path
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Gkeepd Check Succeeds
    Gkeepd Check Email Exists    admin_prof
    Gkeepd Is Running

Check Missing Server cfg
    [Tags]    error
    Gkeepd Check Fails

Check Malformed Server cfg
    [Tags]    error
    Add File To Server    keeper    files/malformed_server.cfg    server.cfg
    Gkeepd Check Fails
