# Copyright 2021 Nathan Sommer and Ben Coleman
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


*** Test Cases ***
Adding Student Succeeds When Account Exists
    [Tags]    happy_path
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Add Account On Server    student1
    Add To Class CSV    faculty1    cs1    student1
    Gkeep Add Succeeds    faculty1    cs1
    Class Contains Student    faculty1    cs1    student11
    New Account Email Exists    student11

Adding Faculty Succeeds When Account Exists
    [Tags]    happy_path
    Launch Gkeepd And Configure Admin Account on Client
    Add Account On Server    faculty1
    Gkeep Add Faculty Succeeds    admin_prof    faculty1
    New Account Email Exists    faculty11
    Create Accounts On Client    faculty11
    Create Git Config    faculty11
    Add To Class CSV    faculty11    cs1    student1
    Gkeep Add Succeeds    faculty11    cs1
    Class Contains Student    faculty11    cs1    student1

Faculty Becomes Student
    [Tags]    happy_path
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1  faculty2
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=faculty2
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    Class Exists    faculty1    cs1
    Class Contains Student    faculty1    cs1    student1
    Class Contains Student    faculty1    cs1    faculty2
    Add Assignment to Client    faculty1    good_simple
    Gkeep Upload Succeeds    faculty1    cs1    good_simple
    Gkeep Publish Succeeds    faculty1    cs1    good_simple
    Clone Assignment    faculty2    faculty1    cs1    good_simple
    Student Submits    faculty2    faculty1    cs1    good_simple    correct_solution
    Submission Test Results Email Exists    faculty2    cs1    good_simple    Done
    # Ensure that faculty2 can still do faculty stuff
    Add To Class CSV    faculty=faculty2    class_name=cs2    username=student1
    Gkeep Add Succeeds    faculty=faculty2    class_name=cs2
    Create Accounts On Client    student1
    Create Git Config    student1
    Add Assignment to Client    faculty2    good_simple
    Gkeep Upload Succeeds    faculty2    cs2    good_simple
    Gkeep Publish Succeeds    faculty2    cs2    good_simple
    Clone Assignment    student1    faculty2    cs2    good_simple
    Student Submits    student1    faculty2    cs2    good_simple    correct_solution
    Submission Test Results Email Exists    student1    cs2    good_simple    Done

Student Becomes Faculty
    [Tags]    happy_path
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student2
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    Add Assignment to Client    faculty1    good_simple
    Create Accounts On Client    student1    student2
    Create Git Config    student1
    Create Git Config    student2
    Gkeep Upload Succeeds    faculty1    cs1    good_simple
    Gkeep Publish Succeeds    faculty1    cs1    good_simple
    Clone Assignment    student1    faculty1    cs1    good_simple
    Student Submits    student1    faculty1    cs1    good_simple    correct_solution
    # student1 now becomes faculty
    Gkeep Add Faculty Succeeds    admin_prof    student1
    Faculty Role Email Exists    student1
    Add To Class CSV    faculty=student1    class_name=cs2    username=student2
    Gkeep Add Succeeds    faculty=student1    class_name=cs2
    Add Assignment To Client    student1    good_simple
    Gkeep Upload Succeeds    student1    cs2    good_simple
    Gkeep Publish Succeeds    student1    cs2    good_simple
    Clone Assignment    student2    student1    cs2    good_simple
    Student Submits    student2    student1    cs2    good_simple    correct_solution
    Submission Test Results Email Exists    student2    cs2    good_simple    Done
    Fetch Assignment    student1    cs2    good_simple    fetched_assignments
