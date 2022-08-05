The testing environment for an assignment can be specified in the optional file
`test_env.yaml` within the assignment directory. If this file does not exist
for a given assignment, the assignment will default to the `host` environment,
described below.

### Host Environment

This testing environment is straightforward, but less secure than the other
environment types, and requires that any dependencies for the tests be
installed on the server itself.

The git-keeper server creates a user named `tester`, and tests are run within a
temporary directory in `/home/tester`. The `tester` user cannot access any
other user home directories, but student code could potentially access other
files within the `tester` home directory, including files for other currently
running tests (if multiple threads are used for testing).

If `test_env.yaml` is omitted, this environment will be used by
default. Alternatively, the following may be placed in `test_env.yaml`:

```
type: host
```

### Firejail Environment

This testing environment uses [Firejail](https://firejail.wordpress.com/) for
sandboxing. As with `host` environments, tests are run by the `tester` user
within a temporary directory in `/home/tester`, but `firejail` is used to limit
the process so that it can only access files within the temporary testing
directory. Dependencies for the tests must still be installed directly on the
server.

The `firejail` package may need to be explicitly installed on the server
before this environment can be used. It is available in the official
repositories for many Linux distributions, including Ubuntu.

By default, `firejail` is run with the following options:

```
--noprofile --quiet --private=/home/tester/<temporary testing directory>
```

This makes `firejail` ignore any default profiles that may be installed on the
server, supresses `firejail` output so that it is not included in the results
email, and sandboxes the tests within the testing directory.

To use the default options, simply create a `test_env.yaml` file with the
following contents:

```
type: firejail
```

Additional options may be specified using the `append_args` field. For example,
if you wish to prohibit any network activity and prevent the process from
writing any files larger than 100 KB, you could use the following:

```
type: firejail
append_args: --net=none --rlimit-fsize=102400
```

These options will be used in addition to the default options. For a full list
of options available for `firejail`, see the
[Firejail homepage](https://firejail.wordpress.com/) or read through the man
page.

### Docker Environment

Tests may be run in a Docker container, which can provide both sandboxing and
encapsulation of dependencies.

TODO: setting up docker on the server

To use this environment, a Docker container image must be specified in
`test_env.yaml`. For example, to use our Python 3.10 container the following
may be used:

```
type: docker
image: gitkeeper/git-keeper-tester:python3.10
```

The first time tests are run using a particular image, the server must download
the image. This can take some time, so it is important to submit a test
submission before publishing the assignment so that the image is downloaded to
the server before students start submitting.

TODO: Describe and link to our Docker Hub images

When tests are run, the temporary testing directory is mounted as a volume
within the container at `/git-keeper-testing`, and the `tests` directory is at
`/git-keeper-testing/tests`. To create your own container images, you will need
to use the `tests` directory as the working directory, and set the command to
run either `action.sh` or `action.py` depending on your preference.

For example, here is a `Dockerfile` to build an image with Python 3.10 that can
be used with git-keeper:

```
FROM python:3.10-slim

WORKDIR /git-keeper-tester/tests

CMD ["bash", "action.sh"]
```

If you want to install additional Python packages within the container, use
`RUN` commands. For example, this installs the `pytest` and `pytest-timeout`
packages using `pip`:

```
FROM python:3.10-slim

RUN pip install pytest pytest-timeout

WORKDIR /git-keeper-tester/tests

CMD ["bash", "action.sh"]
```

TODO: Describe how to test the image locally

You can upload your images to Docker Hub, where they can then be accessed by
the server. See the
[Docker Hub documentation](https://docs.docker.com/docker-hub/) for more
information.
