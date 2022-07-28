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
Suite Setup     Add Docker Images
Force Tags    default_env

*** Keywords ***

Add Docker Images
    Load Docker Image   gitkeeper/git-keeper-tester:python3.10


*** Test Cases ***

Default Env Is Firejail When Not Defined
    [Tags]  happy_path
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course  faculty1    cs1     student1
    Add Assignment to Client  faculty1  determine_env
    Gkeep Upload Succeeds   faculty1   cs1    determine_env
    Gkeep Test Succeeds    faculty1    cs1    determine_env    determine_env/correct_solution
    Submission Test Results Email Exists    faculty1    cs1    determine_env    firejail

Default Env Is Firejail When Defined
    [Tags]  happy_path
    Launch Gkeepd And Configure Admin Account on Client   files/default_env_firejail_server.cfg
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course  faculty1    cs1     student1
    Add Assignment to Client  faculty1  determine_env
    Gkeep Upload Succeeds   faculty1   cs1    determine_env
    Gkeep Test Succeeds    faculty1    cs1    determine_env    determine_env/correct_solution
    Submission Test Results Email Exists    faculty1    cs1    determine_env    firejail

Default Env Is Host When Defined
    [Tags]  happy_path
    Launch Gkeepd And Configure Admin Account on Client   files/default_env_host_server.cfg
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course  faculty1    cs1     student1
    Add Assignment to Client  faculty1  determine_env
    Gkeep Upload Succeeds   faculty1   cs1    determine_env
    Gkeep Test Succeeds    faculty1    cs1    determine_env    determine_env/correct_solution
    Submission Test Results Email Exists    faculty1    cs1    determine_env    host

Default Env Docker Fails
    [Tags]  error
    Add File To Server    keeper    files/default_env_docker_server.cfg    server.cfg
    Start gkeepd
    Gkeepd Is Not Running
