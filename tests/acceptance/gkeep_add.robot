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
Test Setup    Launch Gkeepd With Faculty    washington    adams
Force Tags    gkeep_add

*** Test Cases ***

Valid Class
    [Tags]    happy_path
    Setup Faculty Accounts    washington
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Add To Class    faculty=washington    class_name=cs1    student=gonzo
    Gkeep Add Succeeds    faculty=washington    class_name=cs1
    User Exists    kermit
    User Exists    gonzo
    Email Exists    to_user=kermit    contains=Password
    Email Exists    to_user=gonzo    contains=Password
    Gkeep Query Contains    washington    classes    cs1
    Gkeep Query Contains    washington    students    kermit    gonzo

Missing CSV
    [Tags]    error
    Setup Faculty Accounts    washington
    Gkeep Add Fails    faculty=washington    class_name=cs1

Existing Student
    [Tags]    error
    Setup Faculty Accounts    washington
    Add Account on Server    gonzo
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Add To Class    faculty=washington    class_name=cs1    student=gonzo
    Gkeep Add Succeeds    faculty=washington    class_name=cs1
    User Exists    kermit
    User Exists    gonzo
    Email Exists    to_user=kermit    contains=Password
    Email Does Not Exist    to_user=gonzo
    Gkeep Query Contains    washington    classes    cs1
    Gkeep Query Contains    washington    students    kermit    gonzo

Call Add Twice
    [Tags]    error
    Setup Faculty Accounts    washington
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Gkeep Add Succeeds    faculty=washington    class_name=cs1
    Gkeep Add Fails    faculty=washington    class_name=cs1
    Gkeep Query Contains    washington    classes    cs1
    Gkeep Query Contains    washington    students    kermit

Duplicate Student
    [Tags]    error
    Setup Faculty Accounts    washington
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Gkeep Add Fails    faculty=washington    class_name=cs1

Malformed CSV
    [Tags]    error
    Setup Faculty Accounts    washington
    Add File To Client    washington    files/malformed_cs1.csv    cs1.csv
    Gkeep Add Fails    faculty=washington    class_name=cs1

Student Named Student
    [Tags]    error
    Setup Faculty Accounts    washington
    Add To Class    faculty=washington    class_name=cs1    student=student
    Gkeep Add Fails    faculty=washington    class_name=cs1

Duplicate Class Name
    [Tags]    happy_path
    Setup Faculty Accounts    washington    adams
    Add To Class    faculty=washington    class_name=cs1    student=kermit
    Gkeep Add Succeeds    faculty=washington    class_name=cs1
    Add To Class    faculty=adams    class_name=cs1    student=gonzo
    Gkeep Add Succeeds    faculty=adams    class_name=cs1

Empty CSV
    [Tags]    error
    Setup Faculty Accounts    washington
    Make Empty File    washington    cs1.csv
    Gkeep Add Fails    faculty=washington    class_name=cs1
