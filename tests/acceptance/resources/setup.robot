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

Add Faculty and Configure Accounts on Client
    [Arguments]    @{faculty_names}
    FOR    ${username}    IN    @{faculty_names}
            Gkeep Add Faculty Succeeds    admin_prof    ${username}
            Wait For Email    to_user=${username}    subject_contains="New git-keeper account"    body_contains=Password
    END
    Create Accounts On Client  @{faculty_names}
    FOR    ${username}    IN    @{faculty_names}
                Create Git Config    ${username}
    END

Launch Gkeepd And Configure Admin Account on Client
    [Arguments]    ${server_cfg}=files/valid_server.cfg
    Reset Server
    Reset Client
    Add File To Server    keeper    ${server_cfg}    server.cfg
    Start gkeepd
    Wait For Gkeepd
    Wait For Email    to_user=admin_prof    subject_contains="New git-keeper account"    body_contains=Password
    Create Accounts On Client    admin_prof

Establish Course
    [Arguments]    ${faculty}    ${class}    @{students}
    FOR     ${student}    IN    @{students}
        Add To Class CSV   faculty=${faculty}    class_name=${class}    username=${student}
    END
    Gkeep Add Succeeds    faculty=${faculty}   class_name=${class}


Create Accounts On Client
    [Arguments]    @{usernames}
    FOR    ${username}    IN    @{usernames}
           Create Account    ${username}
           Establish SSH Keys    ${username}
           Create Gkeep Config File    ${username}
    END
