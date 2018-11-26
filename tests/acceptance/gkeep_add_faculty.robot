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
Library    gkeeprobot.keywords.ServerSetupKeywords
Library    gkeeprobot.keywords.ServerCheckKeywords
Library    gkeeprobot.keywords.ServerWaitKeywords
Library    gkeeprobot.keywords.ClientSetupKeywords
Library    gkeeprobot.keywords.ClientCheckKeywords
Resource    resources/setup.robot
Test Setup    Reset And Launch Gkeepd
Force Tags    gkeep_add_faculty

*** Test Cases ***

Add One Faculty
    [Tags]    happy_path
    Add Faculty    prof2
    User Exists    prof2
    Email Exists    to_user=prof2    contains=Password

Duplicate Faculty
    [Tags]    error
    Add Faculty    prof2
    Gkeep Add Faculty Fails    admin_prof    prof2
    Gkeepd Is Running

Add Faculty As Non Admin
    [Tags]    error
    Add Faculty    prof2
    Setup Faculty Accounts    prof2
    Gkeep Add Faculty Fails    prof2    prof3
    Gkeepd Is Running
