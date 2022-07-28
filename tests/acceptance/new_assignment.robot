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
Force Tags    gkeep_new_assignment

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course  faculty1    cs1     student1  student2

*** Test Cases ***

Default Assignment with no Template
    [Tags]    happy_path
    New Assignment Succeeds       faculty1      homework1
    Folder Exists       faculty1      homework1
    Folder Exists       faculty1      homework1/base_code
    Folder Exists       faculty1      homework1/tests
    File Exists     faculty1      homework1/email.txt
    File Exists     faculty1      homework1/assignment.cfg
    File Exists     faculty1      homework1/tests/action.sh


Default Assignment with Template
    [Tags]      happy_path
    Add Assignment Template     faculty1      basic_assignment    default
    New assignment Succeeds      faculty1      homework1
    Folder Exists       faculty1      homework1
    Folder Exists       faculty1      homework1/base_code
    file exists     faculty1      homework1/base_code/README.md
    Folder Exists       faculty1      homework1/tests
    File Exists     faculty1      homework1/email.txt
    File Exists     faculty1      homework1/assignment.cfg
    File Exists     faculty1      homework1/tests/action.sh

Template Assignment
    [Tags]      happy_path
    Add Assignment Template     faculty1      basic_assignment    homework
    New Assignment Succeeds      faculty1      homework1     homework
    Folder Exists       faculty1      homework1
    Folder Exists       faculty1      homework1/base_code
    file exists     faculty1      homework1/base_code/README.md
    Folder Exists       faculty1      homework1/tests
    File Exists     faculty1      homework1/email.txt
    File Exists     faculty1      homework1/assignment.cfg
    File Exists     faculty1      homework1/tests/action.sh

Default Assignment With Alternate Template Path
    [Tags]      happy_path
    Add Templates Folder to Config       faculty1     ~/templates
    Add Assignment Template     faculty1    basic_assignment    default     templates
    New Assignment Succeeds      faculty1    homework1
    Folder Exists       faculty1      homework1
    Folder Exists       faculty1      homework1/base_code
    file exists     faculty1      homework1/base_code/README.md
    Folder Exists       faculty1      homework1/tests
    File Exists     faculty1      homework1/email.txt
    File Exists     faculty1      homework1/assignment.cfg
    File Exists     faculty1      homework1/tests/action.sh


Template Assignment with Alternate Template Path
    [Tags]      happy_path
    Add Templates Folder to Config       faculty1     ~/templates
    Add Assignment Template     faculty1    basic_assignment    homework     templates
    New Assignment Succeeds      faculty1    homework1   homework
    Folder Exists       faculty1      homework1
    Folder Exists       faculty1      homework1/base_code
    file exists     faculty1      homework1/base_code/README.md
    Folder Exists       faculty1      homework1/tests
    File Exists     faculty1      homework1/email.txt
    File Exists     faculty1      homework1/assignment.cfg
    File Exists     faculty1      homework1/tests/action.sh


New Default Assignment Fails When Folder Exists
    [Tags]      error
    Make Empty Directory    faculty1    homework1
    New Assignment Fails     faculty1    homework1

New Template Assignment Fails When Folder Exists
    [Tags]      error
    Add Assignment Template     faculty1      basic_assignment    homework
    Make Empty Directory    faculty1    homework1
    New Assignment Fails     faculty1    homework1   homework