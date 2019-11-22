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
Test Setup      Setup Server and Client Accounts
Force Tags    gkeep_add

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1  faculty2

*** Test Cases ***

Valid Class
    [Tags]    happy_path
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student2
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    User Exists On Server    student1
    User Exists On Server    student2
    New Account Email Exists    student1
    New Account Email Exists    student2
    Class Exists    faculty1    cs1
    Class Contains Student    faculty1    cs1    student1
    Class Contains Student    faculty1    cs1    student2

Byte Order Mark CSV
    [Tags]    happy_path
    Add File To Client    faculty1    files/byte_order_mark.csv   byte_order_mark.csv
    Gkeep Add Succeeds    faculty=faculty1    class_name=byte_order_mark
    User Exists On Server    student1
    New Account Email Exists    student1
    Class Contains Student    faculty1    byte_order_mark    student1

Missing CSV
    [Tags]    error
    Gkeep Add Fails    faculty=faculty1    class_name=cs1

Invalid Username
    [Tags]    error
    Add File To Client    faculty1    files/invalid_username.csv   invalid_username.csv
    Gkeep add Fails    faculty=faculty1    class_name=invalid_username

Existing Student
    [Tags]    error
    Add Account on Server    student2
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student2
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    User Exists On Server    student1
    User Exists On Server    student2
    New Account Email Exists    student1
    Email Does Not Exist    to_user=student2
    Class Contains Student    faculty1    cs1    student1
    Class Contains Student    faculty1    cs1    student2

Call Add Twice
    [Tags]    error
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    Gkeep Add Fails    faculty=faculty1    class_name=cs1
    Class Contains Student    faculty1    cs1    student1

Duplicate Student
    [Tags]    error
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Gkeep Add Fails    faculty=faculty1    class_name=cs1

Malformed CSV
    [Tags]    error
    Add File To Client    faculty1    files/malformed_cs1.csv    cs1.csv
    Gkeep Add Fails    faculty=faculty1    class_name=cs1

Student Named Student
    [Tags]    error
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student
    Gkeep Add Fails    faculty=faculty1    class_name=cs1

Same Class Name From Different Faculty
    [Tags]    happy_path
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    Add To Class CSV    faculty=faculty2    class_name=cs1    username=student2
    Gkeep Add Succeeds    faculty=faculty2    class_name=cs1

Faculty Adds Class Twice With Different Enrollment
    [Tags]  error
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student2
    Gkeep Add Fails    faculty=faculty1    class_name=cs1

Empty CSV
    [Tags]    happy_path
    Make Empty File    faculty1    cs1.csv
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1

No CSV
    [Tags]  happy_path
    Make Empty File    faculty1    cs1.csv
    Gkeep Add No CSV Succeeds    faculty=faculty1    class_name=cs1
