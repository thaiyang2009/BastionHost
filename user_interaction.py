# coding:utf-8

import os
import sys
from getpass import getpass
import subprocess
import time
import hashlib

class UserPortal(object):
    def __init__(self):
        self.user = None

    def user_auth(self):
        retry_count = 0
        while retry_count < 3:
            email = input('Email:')
            if len(email) == 0: continue
            password = ''
            while len(password) == 0:
                password = getpass()
            from django.contrib.auth import authenticate
            user = authenticate(username=email, password=password)
            if user:
                self.user = user
                print("Welcome back!")
                break
            else:
                retry_count += 1
                print('Email or password error!')
        else:
            print("The retry was too many!")
            sys.exit()


    def interaction(self):
        self.user_auth()
        if self.user:
            exit_flag = False
            while not exit_flag:
                # UserProfile.host_groups.all().count()
                bind_hosts = self.user.bind_hosts.all()
                host_groups = self.user.host_groups.all()
                # print(bind_hosts, host_groups)
                print('Host Group %s' % host_groups.count())
                for index, group in enumerate(host_groups):
                    print(index, group.name)
                print(index + 1, 'Ungrouped Host %s' % bind_hosts.count())

                choose = input('Select group index:')
                if choose == 'q':
                    exit_flag = True
                    continue
                elif choose.isdigit() and int(choose) >= 0 and int(choose) <= host_groups.count():
                    choose = int(choose)
                    if choose < host_groups.count():
                        select_host_group = host_groups[choose]
                        select_bind_hosts = select_host_group.bind_hosts.all()
                    else:
                        select_bind_hosts = bind_hosts

                    while not exit_flag:
                        for index, bind_host in enumerate(select_bind_hosts):
                            print(index, bind_host.host.ip_addr, bind_host.host.host_name, bind_host.user.username)
                        choose = input("Please select host index:")
                        if choose == 'q':
                            exit_flag = True
                            continue
                        elif choose == 'b':
                            break
                        elif choose.isdigit() and int(choose) >= 0 and int(choose) < select_bind_hosts.count():
                            choose = int(choose)
                            select_bind_host = select_bind_hosts[choose]

                            print(select_bind_host)

                            m = hashlib.md5()
                            m.update(str(time.time()).encode('utf-8'))
                            session_tag = m.hexdigest()
                            cmd_format = 'sshpass -p {password} /usr/local/openssh7/bin/ssh {username}@{ip_addr} -z {session_tag} -o "StrictHostKeyChecking no"'
                            cmd_str = cmd_format.format(username=select_bind_host.user.username,
                                                        password=select_bind_host.user.password,
                                                        ip_addr=select_bind_host.host.ip_addr,
                                                        session_tag=session_tag)
                            SessionLog.objects.create(user=self.user, bind_host=select_bind_host, session_tag=session_tag)
                            subprocess.Popen('%s %s' % (settings.SESSION_TRACKER_SCRIPT, session_tag),
                                             cwd=settings.BASE_DIR,
                                             shell=True,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)

                            subprocess.run(cmd_str, shell=True)

                            print('---logout---')

                        else:
                            print("Input error!")
                            continue
                else:
                    print("Input error!")
                    continue
            else:
                print("Bye!")




if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BastionHost.settings")
    import django
    django.setup()
    from audit.models import UserProfile
    from audit.models import SessionLog
    from django.conf import settings

    obj = UserPortal()
    obj.interaction()


