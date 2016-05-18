# Copyright 2016 Nathan Sommer and Ben Coleman
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

import gkeepserver.server_configuration as server_config


def test_config_values():
    """This test shows example usage more than anything. It requires creating a
    config.cfg in ~/.config/git-keeper/. It should be changed/replaced/removed
    when there is a better test harness in place.
    """

    config = server_config.get_config()

    assert 'git keeper' == config.from_name
    assert 'gitkeeper@moravian.edu' == config.from_address
    assert 'smtp.gmail.com' == config.smtp_server
    assert '587' == config.smtp_port
    assert 'gitkeeper@moravian.edu' == config.email_username
    assert 'password123' == config.email_password
