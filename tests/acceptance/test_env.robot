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
Test Setup    Setup Server and Client Accounts
Suite Setup     Add Docker Images
Force Tags    test_env

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course  faculty1    cs1     student1
    Create Accounts On Client    student1
    Create Git Config    student1

Add Upload and Publish Assignment
    [Arguments]    ${faculty}    ${class}    ${assignment}
    Add Assignment To Client    ${faculty}    ${assignment}
    Gkeep Upload Succeeds    ${faculty}    ${class}    ${assignment}
    Gkeep Publish Succeeds    ${faculty}    ${class}    ${assignment}

Add Docker Images
    Load Docker Image   gitkeeper/git-keeper-tester:python3.10


*** Test Cases ***

Student Submits to Firejail Assignment
    [Tags]    happy_path
    Add Upload and Publish Assignment  faculty1  cs1  good_firejail
    Clone Assignment  student1  faculty1    cs1     good_firejail
    Student Submits    student1    faculty1    cs1    good_firejail    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_firejail    "|/home/tester/tests|"

Student Submits to Firejail Append Args Assignment
    [Tags]    happy_path
    Add Upload and Publish Assignment  faculty1  cs1  good_firejail_append_args
    Clone Assignment  student1  faculty1    cs1     good_firejail_append_args
    Student Submits    student1    faculty1    cs1    good_firejail_append_args    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_firejail_append_args    "|/home/tester/tests|"

Firejail Prevents Writing Large File
    [Tags]    happy_path
    Add Upload and Publish Assignment  faculty1  cs1  good_firejail_large_file
    Clone Assignment  student1  faculty1    cs1     good_firejail_large_file
    Student Submits    student1    faculty1    cs1    good_firejail_large_file    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_firejail_large_file    "File too large"

Student Submits to Docker Assignment
    [Tags]    happy_path
    Add Upload and Publish Assignment  faculty1  cs1  good_docker
    Clone Assignment  student1  faculty1    cs1     good_docker
    Student Submits    student1    faculty1    cs1    good_docker    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_docker    "In Docker"

Student Submits to No Config Assignment
    [Tags]    happy_path
    Add Upload and Publish Assignment   faculty1    cs1     good_no_config
    Clone Assignment  student1  faculty1    cs1     good_no_config
    Student Submits    student1    faculty1    cs1    good_no_config    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_no_config    "On Host"

Student Submits to Host Assignment
    [Tags]    happy_path
    Add Upload and Publish Assignment  faculty1    cs1     good_host
    Clone Assignment  student1  faculty1    cs1     good_host
    Student Submits    student1    faculty1    cs1    good_host    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_host    "On Host"

Bad Config Format
    [Tags]  Error
    Add Assignment to Client    faculty1    bad_test_config
    Gkeep Upload Fails      faculty1    cs1     bad_test_config

Bad Config No Image
    [Tags]  Error
    Add Assignment to Client    faculty1    bad_docker_no_image
    Gkeep Upload Fails   faculty1   cs1    bad_docker_no_image

Bad Config No Type
    [Tags]  Error
    Add Assignment to Client    faculty1    bad_docker_no_env
    Gkeep Upload Fails   faculty1   cs1    bad_docker_no_env

Bad Docker Extra Field
    [Tags]  Error
    Add Assignment to Client    faculty1    bad_docker_extra_field
    Gkeep Upload Fails   faculty1   cs1    bad_docker_extra field

Bad Firejail Extra Field
    [Tags]  Error
    Add Assignment to Client    faculty1    bad_firejail_extra_field
    Gkeep Upload Fails   faculty1   cs1    bad_firejail_extra field

Docker Container Does Not Exist
    [Tags]  Error
    Add Assignment to Client    faculty1    bad_docker_container
    Gkeep Upload Fails   faculty1   cs1    bad_docker_container

Bad Type in Test Env
    [Tags]  Error
    Add Assignment to Client    faculty1    bad_type
    Gkeep Upload Fails   faculty1   cs1    bad_type

Faculty Updates to Include Docker Before Publish
    [Tags]  happy_path
    Add Assignment to Client  faculty1  good_host
    Gkeep Upload Succeeds   faculty1   cs1    good_host
    Add File to Client      faculty1    files/good_assignment.cfg    good_host/assignment.cfg
    Gkeep Update Succeeds   faculty1    cs1     good_host     all
    Gkeep Publish Succeeds  faculty1    cs1     good_host
    Clone Assignment  student1  faculty1    cs1     good_host
    Student Submits    student1    faculty1    cs1    good_host    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_host    "In Docker"

Faculty Updates to Include Docker After Publish
    [Tags]  happy_path
    Add Upload and Publish Assignment   faculty1    cs1     good_host
    Add File to Client      faculty1    files/good_assignment.cfg    good_host/assignment.cfg
    Gkeep Update Succeeds   faculty1    cs1     good_host     config
    Clone Assignment  student1  faculty1    cs1     good_host
    Student Submits    student1    faculty1    cs1    good_host    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_host    "In Docker"

Faculty Updates to Remove Docker Before Publish
    [Tags]    happy_path
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Delete File on Client   faculty1    good_docker/assignment.cfg
    Gkeep Update Succeeds   faculty1    cs1     good_docker     config
    Gkeep Publish Succeeds  faculty1    cs1     good_docker
    Clone Assignment  student1  faculty1    cs1     good_docker
    Student Submits    student1    faculty1    cs1    good_docker    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_docker    "On Host"

Faculty Updates to Remove Docker After Publish
    [Tags]    happy_path
    Add Upload and Publish Assignment   faculty1    cs1     good_docker
    Delete File on Client   faculty1    good_docker/assignment.cfg
    Gkeep Update Succeeds   faculty1    cs1     good_docker     config
    Clone Assignment  student1  faculty1    cs1     good_docker
    Student Submits    student1    faculty1    cs1    good_docker    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_docker    "On Host"

Update to Bad Config No Image
    [Tags]  Error
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Add File to Client      faculty1    files/bad_no_image_assignment.cfg    good_docker/assignment.cfg
    Gkeep Update Fails   faculty1   cs1    good_docker  config

Update to Bad Config No Env
    [Tags]  Error
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Add File to Client      faculty1    files/bad_no_env_assignment.cfg    good_docker/assignment.cfg
    Gkeep Update Fails   faculty1   cs1    good_docker  config

Update to Docker Container Does Not Exist
    [Tags]  Error
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Add File to Client      faculty1    files/bad_container_assignment.cfg    good_docker/assignment.cfg
    Gkeep Update Fails   faculty1   cs1    good_docker  config

Test Produces Email to Faculty in Docker
    [Tags]  happy_path
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Gkeep Test Succeeds    faculty1    cs1    good_docker    good_docker/correct_solution
    Submission Test Results Email Exists    faculty1    cs1    good_docker    "In Docker"

Assignment Timeout Overrides Server Timeout
    [Tags]  happy_path
    Add Assignment to Client  faculty1  one_second_timeout
    Gkeep Upload Succeeds  faculty1  cs1  one_second_timeout
    Gkeep Test Succeeds  faculty1  cs1  one_second_timeout  one_second_timeout/correct_solution
    Submission Test Results Email Exists  faculty1  cs1  one_second_timeout  "Tests timed out"
