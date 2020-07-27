# Copyright 2019 Nathan Sommer and Ben Coleman
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
Test Setup    Setup Server and Client Accounts
Force Tags    gkeep_query

*** Keywords ***

Setup Server and Client Accounts
    Launch Gkeepd And Configure Admin Account on Client
    Add Faculty and Configure Accounts on Client    faculty1

*** Test Cases ***

No Class Results in Empty Reports JSON
    Gkeep Query JSON Produces Results    faculty1   classes   []
    Gkeep Query JSON Produces Results    faculty1   assignments   {}
    Gkeep Query JSON Produces Results    faculty1   students   {}
    Gkeep Query JSON Produces Results    faculty1   recent   {}


Class With Assignment Results in JSON
    Establish Course  faculty1    cs1     student1
    Add Assignment to Client  faculty1  good_simple
    Gkeep Upload Succeeds   faculty1   cs1    good_simple

    Gkeep Query JSON Produces Results    faculty1   classes   ["cs1"]
    Gkeep Query JSON Produces Results    faculty1   assignments   {"cs1":[{"name":"good_simple","published":false,"disabled":false}]}
    Gkeep Query JSON Produces Results    faculty1   students   {"cs1":[{"first_name":"First","last_name":"Last","username":"student1","email_address":"student1@gitkeeper.edu"}]}
    Gkeep Query JSON Produces Results    faculty1   recent   {}
