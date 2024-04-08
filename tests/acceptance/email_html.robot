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
Force Tags    email_html


*** Keywords ***

Launch With Cfg And Submit Assignment
    [Arguments]    ${config_file}    ${assignment_name}
    Launch Gkeepd And Configure Admin Account on Client    ${config_file}
    Gkeepd Is Running
    Add Faculty and Configure Accounts on Client    faculty1
    Establish Course    faculty1    cs1    student1
    Create Accounts On Client    student1
    Create Git Config    student1
    Add Assignment to Client    faculty1    ${assignment_name}
    Gkeep Upload Succeeds    faculty1    cs1    ${assignment_name}
    Gkeep Publish Succeeds    faculty1    cs1    ${assignment_name}
    Clone Assignment  student1  faculty1    cs1     ${assignment_name}
    Student Submits    student1    faculty1    cs1    ${assignment_name}    correct_solution


*** Test Cases ***

Assignment Html True Server Html False
    [Tags]    happy_path
    Launch With Cfg And Submit Assignment    files/use_html_false_server.cfg    use_html_true
    Submission Test Results Email Exists    student1    cs1    use_html_true    <pre>Solution\ output\n</pre>

Assignment Html False Server Html True
    [Tags]    happy_path
    Launch With Cfg And Submit Assignment    files/use_html_true_server.cfg    use_html_false
    Submission Test Results Email Exists    student1    cs1    use_html_false    Solution\ output
    Submission Test Results Email Does Not Exist    student1    cs1    use_html_false    <pre>Solution\ output\n</pre>

Server Html True
    [Tags]    happy_path
    Launch With Cfg And Submit Assignment    files/use_html_true_server.cfg    good_simple
    Submission Test Results Email Exists    student1    cs1    good_simple    <pre>Done\n</pre>

Server Html False
    [Tags]    happy_path
    Launch With Cfg And Submit Assignment    files/use_html_false_server.cfg    good_simple
    Submission Test Results Email Does Not Exist    student1    cs1    good_simple    <pre>Done\n</pre>
    Submission Test Results Email Exists    student1    cs1    good_simple    Done
