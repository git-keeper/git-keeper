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

*** Keywords ***

Reset And Launch Gkeepd
    Reset Server
    Reset Client
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd
    Wait For Gkeepd
    Setup Faculty Accounts    admin_prof

Add Faculty
    [Arguments]    @{faculty_names}
    :FOR    ${username}    IN    @{faculty_names}
    \        Gkeep Add Faculty Succeeds    admin_prof    ${username}
    \        Wait For Email    to_user=${username}    contains=Password

Launch Gkeepd With Faculty
    [Arguments]    @{faculty_names}
    Reset And Launch Gkeepd
    Add Faculty    @{faculty_names}

Setup Faculty Accounts
    [Arguments]    @{usernames}
    :FOR    ${username}    IN    @{usernames}
    \    Create Accounts    ${username}
    \    Establish SSH Keys    ${username}
    \    Create Gkeep Config File    ${username}
