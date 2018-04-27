
*** Settings ***

Library    gkeeprobot.keywords.VagrantKeywords
Suite Setup    Vagrant Setup
Suite Teardown    Vagrant Teardown

*** Keywords ***

Vagrant Setup
    Make Boxes if Missing
    Start Vagrant if Not Running
    Set Key Permissions

Vagrant Teardown
    Stop Vagrant if Not Originally Running

