Events are written to event logs. Each line of the log is an event, and is structured like this:

```
<timestamp> <event type> <payload>
```

For example:

```
1463892789 SUBMISSION /home/student/faculty/class/assignment.git
```

Event types are used to determine what event handler should handle the event.

## Student log events

* `SUBMISSION <student assignment repo path>` - Student pushes to an assignment repository. Triggers test running.

## Faculty log events

* `UPLOAD <assignment directory>` - Faculty uploads a new assignment.
* `UPDATE <assignment directory> <item>` - Faculty updates an assignment item.
    * Items:
        * `base_code`
        * `tests`
* `PUBLISH <assignment directory>` - Faculty requests that the assignment be published.
* `DELETE <assignment directory>` - Faculty requests that the assignment be deleted.
* `CLASS_ADD` <class directory>` - Faculty adds a class roster.
* `CLASS_MODIFY` <class directory>` - Faculty modifies a class roster.