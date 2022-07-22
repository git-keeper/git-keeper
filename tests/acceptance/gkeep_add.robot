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

Add Students With Same Email Username
    [Tags]    happy_path
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=user    email_domain=one.edu
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=user    email_domain=two.edu
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=user    email_domain=three.edu
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    User Exists On Server    user
    User Exists On Server    user1
    User Exists On Server    user2
    New Account Email Exists    user
    # Checking for the other emails will involve significant changes to the
    # email system
    # New Account Email Exists    user1
    # New Account Email Exists    user2
    Class Exists    faculty1    cs1
    Class Contains Student    faculty1    cs1    user
    Class Contains Student    faculty1    cs1    user1
    Class Contains Student    faculty1    cs1    user2

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

Non ASCII Characters
    [Tags]    happy_path
    Add File To Client    faculty1    files/non_ascii_characters.csv   non_ascii_characters.csv
    Gkeep Add Succeeds    faculty=faculty1    class_name=non_ascii_characters
    User Exists On Server    funny

Existing Student
    [Tags]    error
    Add Account on Server    student2
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student2
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    User Exists On Server    student1
    User Exists On Server    student2
    New Account Email Exists    student1
    New Account Email Does Not Exist    to_user=student2
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
    Gkeep Add No CSV Succeeds    faculty=faculty1    class_name=cs1

Uppercase Email
    [Tags]    happy_path
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=STUDENT1    email_domain=SCHOOL.EDU
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    Class Contains Student    faculty1    cs1    student1
    User Exists On Server    student1

Different Case Email Username
    [Tags]    error
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=STUDENT1
    Gkeep Add Fails    faculty=faculty1    class_name=cs1
    Gkeepd Is Running

Different Case Email Domain
    [Tags]    error
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1    email_domain='SCHOOL.EDU'
    Gkeep Add Fails    faculty=faculty1    class_name=cs1
    Gkeepd Is Running
