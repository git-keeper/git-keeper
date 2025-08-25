## Security

* `tester` account run student submission has non-root authority
* Students only have a git-shell
* Students cannot force push
* tester has no password, so no-one can login (or change the password)
* tester is disabled for ssh login
* Time and memory limits all test processes (global setting is generous and then additional restrictions are possible per assignment)


## Risks

* Student process could fill up the harddrive
* No network restriction on submitted code
* .bashrc of tester account (could a student do something bad?  When is this run?)
* Student could launch a background process (e.g. with `nohup`)
* 