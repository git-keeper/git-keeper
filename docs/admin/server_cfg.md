`server.cfg` has three sections: `[server]`, `[email]`, and `[gkeepd]`.

### `[server]`

The `[server]` section has a single required parameter `hostname`, which is the hostname of the server.

### `[email]`

The `[email]` section is also required. The following parameters are required:

```
from_name: <name that the emails will be from>
from_address: <email address that the emails come from>
smtp_server: <hostname of the SMTP server>
smtp_port: <SMTP server port>
```

The following parameters are optional:

```
use_tls: <true or false, defaults to true>
email_username: <username for the SMTP server>
email_password: <password for the SMTP server>
```

### `[gkeepd]`

The `[gkeepd]` section is optional. Below are the allowed parameters and their defaults:

```
keeper_user: keeper
keeper_group: keeper
faculty_group: faculty
student_group: student
```

