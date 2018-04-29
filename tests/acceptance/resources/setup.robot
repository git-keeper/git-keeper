*** Keywords ***

Launch Gkeepd With Faculty
    [Arguments]    @{faculty_names}
    Reset Server
    Reset Client
    Configure Faculty   @{faculty_names}
    Add File To Server    keeper    files/valid_server.cfg    server.cfg
    Start gkeepd

Setup Faculty Accounts
    [Arguments]    @{usernames}
    :FOR    ${username}    IN    @{usernames}
    \    Create Accounts    ${username}
    \    Establish SSH Keys    ${username}
    \    Create Gkeep Config File    ${username}
