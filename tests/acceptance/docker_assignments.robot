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
Force Tags    gkeepd_launch

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course  faculty1    cs1     student1
    Create Accounts On Client    student1
    Create Git Config    student1

Add Docker Images
    Load Docker Image   gitkeeper/git-keeper-tester:python3.10

*** Test Cases ***

Student Submits to Docker Assignment
    [Tags]    happy_path
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Gkeep Publish Succeeds  faculty1    cs1     good_docker
    Clone Assignment  student1  faculty1    cs1     good_docker
    Student Submits    student1    faculty1    cs1    good_docker    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_docker    "In Docker"

Student Submits to NonDocker Assignment
    [Tags]    happy_path
    Add Assignment to Client  faculty1  good_not_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_not_docker
    Gkeep Publish Succeeds  faculty1    cs1     good_not_docker
    Clone Assignment  student1  faculty1    cs1     good_not_docker
    Student Submits    student1    faculty1    cs1    good_not_docker    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_not_docker    "On Host"

Student Submits to NonDocker Assignment With On Host Specified
    [Tags]    happy_path
    Add Assignment to Client  faculty1  good_not_docker_test_env
    Gkeep Upload Succeeds   faculty1   cs1    good_not_docker_test_env
    Gkeep Publish Succeeds  faculty1    cs1     good_not_docker_test_env
    Clone Assignment  student1  faculty1    cs1     good_not_docker_test_env
    Student Submits    student1    faculty1    cs1    good_not_docker_test_env    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_not_docker_test_env    "On Host"

Bad YAML Format
    [Tags]  Error
    Add Assignment to Client    faculty1    bad_test_yaml
    Gkeep Upload Fails      faculty1    cs1     bad_test_yaml

Bad YAML No Image
    [Tags]  Error
    Add Assignment to Client    faculty1    bad_docker_no_image
    Gkeep Upload Fails   faculty1   cs1    bad_docker_no_image

Bad YAML No Type
    [Tags]  Error
    Add Assignment to Client    faculty1    bad_docker_no_type
    Gkeep Upload Fails   faculty1   cs1    bad_docker_no_type

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
    Add Assignment to Client  faculty1  good_not_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_not_docker
    Add File to Client      faculty1    files/good_test_env.yaml    good_not_docker/test_env.yaml
    Gkeep Update Succeeds   faculty1    cs1     good_not_docker     all
    Gkeep Publish Succeeds  faculty1    cs1     good_not_docker
    Clone Assignment  student1  faculty1    cs1     good_not_docker
    Student Submits    student1    faculty1    cs1    good_not_docker    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_not_docker    "In Docker"

Faculty Updates to Include Docker After Publish
    [Tags]  happy_path
    Add Assignment to Client  faculty1  good_not_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_not_docker
    Gkeep Publish Succeeds  faculty1    cs1     good_not_docker
    Add File to Client      faculty1    files/good_test_env.yaml    good_not_docker/test_env.yaml
    Gkeep Update Succeeds   faculty1    cs1     good_not_docker     test_env
    Clone Assignment  student1  faculty1    cs1     good_not_docker
    Student Submits    student1    faculty1    cs1    good_not_docker    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_not_docker    "In Docker"

Faculty Updates to Remove Docker Before Publish
    [Tags]    happy_path
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Delete File on Client   faculty1    good_docker/test_env.yaml
    Gkeep Update Succeeds   faculty1    cs1     good_docker     test_env
    Gkeep Publish Succeeds  faculty1    cs1     good_docker
    Clone Assignment  student1  faculty1    cs1     good_docker
    Student Submits    student1    faculty1    cs1    good_docker    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_docker    "On Host"

Faculty Updates to Remove Docker After Publish
    [Tags]    happy_path
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Gkeep Publish Succeeds  faculty1    cs1     good_docker
    Delete File on Client   faculty1    good_docker/test_env.yaml
    Gkeep Update Succeeds   faculty1    cs1     good_docker     test_env
    Clone Assignment  student1  faculty1    cs1     good_docker
    Student Submits    student1    faculty1    cs1    good_docker    correct_solution
    Submission Test Results Email Exists    student1    cs1    good_docker    "On Host"

Update to Bad YAML No Image
    [Tags]  Error
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Add File to Client      faculty1    files/bad_no_image_test_env.yaml    good_docker/test_env.yaml
    Gkeep Update Fails   faculty1   cs1    good_docker  test_env

Update to Bad YAML No Type
    [Tags]  Error
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Add File to Client      faculty1    files/bad_no_type_test_env.yaml    good_docker/test_env.yaml
    Gkeep Update Fails   faculty1   cs1    good_docker  test_env

Update to Docker Container Does Not Exist
    [Tags]  Error
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Add File to Client      faculty1    files/bad_container_test_env.yaml    good_docker/test_env.yaml
    Gkeep Update Fails   faculty1   cs1    good_docker  test_env

Test Produces Email to Faculty in Docker
    [Tags]  happy_path
    Add Assignment to Client  faculty1  good_docker
    Gkeep Upload Succeeds   faculty1   cs1    good_docker
    Gkeep Test Succeeds    faculty1    cs1    good_docker    good_docker/correct_solution
    Submission Test Results Email Exists    faculty1    cs1    good_docker    "In Docker"

