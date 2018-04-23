
*** Settings ***

Library    gkeeprobot.keywords.VagrantKeywords
Suite Setup    Vagrant Setup
Suite Teardown    Vagrant Teardown

*** Keywords ***

Vagrant Setup
    Make Boxes if Missing
    Start Vagrant   ${ROBOT_CONTROLS_VAGRANT}

Vagrant Teardown
    Stop Vagrant    ${ROBOT_CONTROLS_VAGRANT}

*** Variables ***
${ROBOT_CONTROLS_VAGRANT}    No
