import os
import json
import time
from coin_helper.settings import BASE_DIR

def split_hump_2_words(string):
    word_list = []
    char_list = []
    for _ in string:
        if (not char_list) or _.islower():
            char_list.append(_)
        else:
            word_list.append(''.join(char_list).lower())
            char_list = [_]
    word_list.append(''.join(char_list).lower())
    return word_list


def logger(cate,cname,fname,level='debug',info=''):
    log_dir = os.path.join(BASE_DIR,'logs')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_file_name = os.path.join(log_dir,cate+'.log')
    log_line = f'{time.strftime("%Y-%m-%d %H:%M:%S")} |class:{cname} |func:{fname} |level:{level} |{json.dumps(info)}\n'
    with open(log_file_name,'a') as f:
        f.write(log_line)

