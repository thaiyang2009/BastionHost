# coding:utf-8

import re


class AuditLogHandler(object):
    def __init__(self, log_file):
        self.log_file = log_file
        self.log_file_obj = self.__get_file_obj()

    def __get_file_obj(self):
        return open(self.log_file, 'r')

    def parse(self):
        cmd_list = []
        cmd_str = ''

        catch_write5_flag = False

        for line in self.log_file_obj:
            line = line.split()
            # print(line)
            try:
                time_clock, io_call, char = line[0:3]
                if io_call.startswith('read(4'):

                    if char == '"\\177",':  # 回退
                        char = '[1<-del]'
                    elif char == '"\\33OB",':  # vim 下
                        char = '[down 1]'
                    elif char == '"\\33OA",':  # vim 上
                        char = '[up 1]'
                    elif char == '"\\33OC",':  # vim 左
                        char = '[right 1]'
                    elif char == '"\\33OD",':  # vim 右
                        char = '[left 1]'
                    elif char == '"\33[2;2R]",':  # 进入vim
                        continue
                    elif char == '"\\33[>1;95;0c]",':  # 进入vim
                        char = '[---enter vim mode---]'
                    elif char == '"\\33[A",':  # 命令行上
                        char = '[up 1]'
                        catch_write5_flag = True  # 取向上按键拿到的历史命令
                    elif char == '"\\33[B",':  # 命令行下
                        char = '[down 1]'
                        catch_write5_flag = True  # 取向下按键拿到的历史命令
                    elif char == '"\\33[C",':  # 命令行左
                        char = '[left 1]'
                    elif char == '"\\33[D",':  # 命令行右
                        char = '[right 1]'

                    cmd_str += char.strip('"",')
                    if char == '"\\t",':
                        catch_write5_flag = True
                        continue
                    if char == '"\\r",':
                        cmd_list.append((time_clock, cmd_str))
                        cmd_str = ''
                    if char == '"':
                        cmd_str += '  '
                if catch_write5_flag:
                    if io_call.startswith('write(5'):
                        if io_call == '"\7",':  # 空键，不是空格，是回退不了就是这个代码
                            pass
                        else:
                            cmd_str += char.strip('"",')
                        catch_write5_flag = False
            except ValueError as e:
                print("\033[031;1mSession log record err, plase...")

        # for cmd in cmd_list:
        #     print(cmd)

        return cmd_list

if __name__ == '__main__':
    obj = AuditLogHandler('../logs/audit/2017_12_03/b64f8fefe8719d88c4a209c6a107a2a1.log')
    print(obj.parse())