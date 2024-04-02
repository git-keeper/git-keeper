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
Test Setup    Reset Client And Add Faculty Account
Force Tags    gkeep_test

*** Keywords ***

Reset Client And Add Faculty Account
    Reset Client
    Create Accounts On Client    faculty1


*** Test Cases ***

Local Host Test Succeeds
    [Tags]  happy_path
    Add Assignment To Client    faculty1    good_host
    Gkeep Local Test Output Contains    faculty1    good_host  good_host/correct_solution  On\ Host

Local Firejail Test Succeeds
    [Tags]  happy_path
    Add Assignment To Client    faculty1    good_firejail_host_check
    Gkeep Local Test Output Contains    faculty1    good_firejail_host_check  good_firejail_host_check/correct_solution  On\ Host

Local Docker Test Succeeds
    [Tags]  happy_path
    Add Assignment To Client    faculty1    good_docker
    Gkeep Local Test Output Contains    faculty1    good_docker  good_docker/correct_solution  In\ Docker

Local Test Fails With Bad Action
    [Tags]  error
    Add Assignment To Client    faculty1    bad_action
    Gkeep Local Test Fails    faculty1    bad_action  bad_action/correct_solution
