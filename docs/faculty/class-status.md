
Each class in `git-keeper` has a status, "open" or "closed."  When created a class it is open,
and it remains open until the faculty explicitly closes it.  To change the status of a class run
the command

```
gkeep status <class_name> <status>
```

where `<status>` is `open` or `closed`.  The system will respond with

```
Status updated successfully
```

When a class is open, the faculty member can publish assignments and the students can
receive results.

When a class is closed, the faculty cannot upload or publish any new assignments.  If
they run `gkeep upload` or `gkeep publish` on a closed course, they will receive a message,
"Class <classname> is closed."

If a student pushes to a repo associated with a closed course they will receive an email
indicating that the course is closed:

```
Subject: [cs1] class is closed

You have pushed a submission for a class that is is closed.
```

