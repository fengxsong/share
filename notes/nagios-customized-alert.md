## NAGIOS自定义告警

定义联系人模板

    # notification_period: define timeperiod.
    # notification_options:w=warning, u=unknown, c=critical, r=recovery, f=flapping, n=none
    define contact{
        name                            test-contact
        service_notification_period     24x7
        host_notification_period        24x7
        service_notification_options    c,r		        ; send notifications for critical, recovery
        host_notification_options       d,r	            ; send notifications for host states like down, recovery
        service_notification_commands   notify-service-by-email	; send service notifications via email
        host_notification_commands      notify-host-by-email	; send host notifications via email
        register                        0       		; DONT REGISTER THIS DEFINITION - ITS NOT A REAL CONTACT, JUST A TEMPLATE!
        }

定义联系人

    define contact{
        contact_name    test_someone
        use				test-contact
        alias           测试
        email           test@example.com
        }

定义联系人组

    define contactgroup{
        contactgroup_name       test_group
        alias                   test Groups
        members                 test_someone,
        }

然后定义特定`host`和`service`(模板里)的`contact_groups`或者`contact`使生效。
