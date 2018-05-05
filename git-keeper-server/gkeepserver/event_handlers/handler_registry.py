# Copyright 2016, 2017 Nathan Sommer and Ben Coleman
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


"""
Provides a dictionary which maps event type strings to event handler
classes. Pass event_handlers_by_type to a EventHandlerAssignerThread
constructor.
"""

from gkeepserver.event_handlers.class_add_handler import ClassAddHandler
from gkeepserver.event_handlers.class_modify_handler import ClassModifyHandler
from gkeepserver.event_handlers.class_status_handler import ClassStatusHandler
from gkeepserver.event_handlers.delete_handler import DeleteHandler
from gkeepserver.event_handlers.faculty_add_handler import FacultyAddHandler
from gkeepserver.event_handlers.publish_handler import PublishHandler
from gkeepserver.event_handlers.submission_handler import SubmissionHandler
from gkeepserver.event_handlers.trigger_handler import TriggerHandler
from gkeepserver.event_handlers.update_handler import UpdateHandler
from gkeepserver.event_handlers.upload_handler import UploadHandler


event_handlers_by_type = {
    'CLASS_ADD': ClassAddHandler,
    'CLASS_MODIFY': ClassModifyHandler,
    'CLASS_STATUS': ClassStatusHandler,
    'SUBMISSION': SubmissionHandler,
    'UPLOAD': UploadHandler,
    'UPDATE': UpdateHandler,
    'PUBLISH': PublishHandler,
    'DELETE': DeleteHandler,
    'TRIGGER': TriggerHandler,
    'FACULTY_ADD': FacultyAddHandler,
}
