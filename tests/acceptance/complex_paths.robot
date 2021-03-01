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
Adding And Removing Students
    [Tags]    happy_path
    # start with an empty class, upload and publish good_simple
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1
    Make Empty File    faculty1    cs1.csv
    Gkeep Add Succeeds    faculty=faculty1    class_name=cs1
    Add Assignment to Client    faculty1    good_simple
    Gkeep Upload Succeeds    faculty1    cs1    good_simple
    New Assignment Email Exists    faculty1    cs1    good_simple
    Gkeep Publish Succeeds    faculty1    cs1    good_simple
    # add student1, who should then get good_simple
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Gkeep Modify Succeeds    faculty=faculty1    class_name=cs1
    Create Accounts On Client    student1
    Create Git Config    student1
    New Assignment Email Exists    student1    cs1    good_simple
    Clone Assignment    student1    faculty1    cs1    good_simple
    Student Submits Correct Solution    student1    faculty1    cs1    good_simple
    Submission Test Results Email Exists    student1    cs1    good_simple    Done
    # add student2, who should also get good_simple
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student2
    Gkeep Modify Succeeds    faculty=faculty1    class_name=cs1
    Create Accounts On Client    student2
    Create Git Config    student2
    New Assignment Email Exists    student2    cs1    good_simple
    Clone Assignment    student2    faculty1    cs1    good_simple
    Student Submits Correct Solution    student2    faculty1    cs1    good_simple
    Submission Test Results Email Exists    student2    cs1    good_simple    Done
    # remove student1
    Remove From Class    faculty=faculty1    class_name=cs1    student=student1
    Gkeep Modify Succeeds    faculty=faculty1    class_name=cs1
    Class Does Not Contain Student    faculty1    cs1    student1
    # add and publish good_simple2, which student2 should get but student1
    # should not
    Add Assignment to Client    faculty1    good_simple2
    Gkeep Upload Succeeds    faculty1    cs1    good_simple2
    New Assignment Email Exists    faculty1    cs1    good_simple2
    Gkeep Publish Succeeds    faculty1    cs1    good_simple2
    New Assignment Email Exists    student2    cs1    good_simple2
    New Assignment Email Does Not Exist    student1    cs1    good_simple_2
    Clone Assignment    student2    faculty1    cs1    good_simple2
    Student Submits Correct Solution    student2    faculty1    cs1    good_simple2
    Submission Test Results Email Exists    student2    cs1    good_simple2    Done
    # add student1 back in, who should get good_simple2
    Add To Class CSV    faculty=faculty1    class_name=cs1    username=student1
    Gkeep Modify Succeeds    faculty=faculty1    class_name=cs1
    Class Contains Student    faculty1    cs1    student1
    Class Contains Student    faculty1    cs1    student2
    New Assignment Email Exists    student1    cs1    good_simple2
    Clone Assignment    student1    faculty1    cs1    good_simple2
    Student Submits Correct Solution    student1    faculty1    cs1    good_simple2
    Submission Test Results Email Exists    student1    cs1    good_simple2    Done
