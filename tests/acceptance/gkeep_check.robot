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
Test Setup      Setup Server and Client Accounts
Force Tags    gkeep_check

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1

*** Test Cases ***

Valid Configuration Server Running
    [Tags]    happy_path
    Gkeep Check Succeeds    faculty1

Valid Configuration Server Stopped
    [Tags]    error
    Stop Gkeepd
    Gkeep Check Fails    faculty1

Invalid Configuration Server Running
    [Tags]    error
    Add File To Client    faculty1    files/malformed_client.cfg    .config/git-keeper/client.cfg
    Gkeep Check Fails    faculty1
