import models
from models import settings, pomdp_mapper, agent, alert, ryuapi
import psutil
import traceback
import time
import numpy as np
import os, paramiko, json
import sys, traceback

SSH_STATUS = input('monitor: ')
if SSH_STATUS == 'y':
    SSH_USERNAME = input('Username: ')
    SSH_PASSWD = input('Password: ')

def clear_and_reset(old_file="", new_file=''):
    r = open(old_file, 'r')
    content = r.read()
    r.close()

    w = open(new_file, 'w')
    w.write(content)
    w.close()

    w = open(old_file, 'w')
    w.write('')
    w.close()


def write_ryu_status(status=True):
    if SSH_STATUS:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('labgen.lid.uff.br', username=SSH_USERNAME, password=SSH_PASSWD)
        conn = ssh
        ftp = conn.open_sftp()
        file = ftp.file('/var/www/html/ryu/status.txt', "w", -1)
        file.write(json.dumps(dict(status=status)))
        file.flush()
        ftp.close()


def main(max_t, filename, states=settings.STATES, step=settings.STEP, index=1):

    print('FILENAME=', filename)
    cpus = []
    differ = pomdp_mapper.NetProcDiff()
    t = 0
    try:
        client_count = ryuapi.RyuApi().client_count()
    except:
        print("RYU DOWN")
        write_ryu_status(False)
        sys.exit()
        exit()
    dc = models.DC(cap=settings.MAX_SERVER_LOAD*client_count)
    clients = list()
    print("CLIENT COUNT: ", client_count)



    for i in range(client_count):
        clients.append(models.Client(i + 2, settings.CLIENT1_BW + i*settings.BW_STEP, dc, states=states))




    rp = models.RewardProvider(settings.SERVER_IP, clients, dc, pomdp=settings.POMDP)


    try:
        rp.enabled = True
        if settings.PARALLEL:
            rp.parallel_start()
        print("START REWARD PROVIDER")
        while 1:
            print("T =", t, " ------------------------------------------------------------------")
            if settings.INTERCALATE:
                if t % 2 == 0:
                    settings.POMDP = True
                else:
                    settings.POMDP = False

            cpus.append((psutil.cpu_percent(), psutil.virtual_memory().percent, rp.dc.load))
            differ.dump_diff(psutil.cpu_percent(), psutil.virtual_memory().percent, rp.dc.load)

            ERROR = False

            # print("CPU=", np.mean(cpus))
            #print("STEP", step)
            time.sleep(step)
            #print("PASSOU DO SLEEP")
            try:
                rp.step()
            except:
                ERROR = True
                print("DEU ERRO NO STEP")
                traceback.print_exc()
            #print("PASSOU DO STEP")
            t += 1
            errors = 0
            for client in rp.clients:
                if client.error:
                    errors += 1
            #print("PASSOU DA VER DE ERRO")
            #print(errors, len(rp.clients))
            if t > max_t or errors == len(rp.clients) or ERROR:
                for c in rp.clients:
                    c.agent.dump_q_table(index)
                clear_and_reset(settings.MAIN_FILE, filename)
                rp.enabled = False
                for thread in rp.threads:
                    thread.join()
                    print("TERMINARAM AS THREADS!!!")
                break
    except:
        traceback.print_exc()
        print(cpus)




def cp(filename, new_filename):
    try:
        f = open(filename, 'r')
        content = f.read()
        f.close()
        if content:
            f = open(new_filename, 'w+')
            f.write(content)
            f.close()
        f = open(filename, 'w+')
        f.write('')
        f.close()
    except:
        f = open(filename, 'w+')
        f.write('')
        f.close()


if __name__ == "__main__":
    if 1:
        write_ryu_status(status=True)
        repeat = 2
        repeat_count = settings.REPEAT_COUNT
        fuzzy_times = [2, 5]
        while 1:
            repeat_count += 1
            #cp(f'{settings.STATE_FILE}{settings.STATES}.txt',
            #   f'{settings.STATE_FILE}{settings.STATES}-{repeat_count}.txt')
            print(settings.STATES, "ANTES")
            if repeat_count > repeat:
                repeat_count = 0
                settings.STATES += 1
            print(settings.STATES, "Depois")
            sm, trained = "", ""
            if settings.EXPLORATION == "softmax":
                sm = "-sm"
            if settings.Q_TABLE_INDEX:
                trained = "-trained"
            filenames = [
                f'results-dataset_{settings.STRATEGY.split("_")[0]}/{settings.STRATEGY.split("_")[0]}-compare-aw-{sm}{trained}',
            ]


            for filename in filenames:
                if filename.lower().count('pomdp'):
                    settings.POMDP = True
                elif filename.lower().count('inter'):
                    settings.POMDP = True
                    settings.INTERCALATE = True
                if settings.FUZZY:
                    for t in fuzzy_times:
                        for count in range(0, 20):
                            now_file = f'{filename}-{t}-{count}.txt'
                            if os.path.isfile(now_file):
                                file = open(now_file, "r")
                                content = file.read()
                                file.close()
                                if len(content.splitlines()) > 99:
                                    continue
                            print(now_file)
                            print(count,
                                  "TAKE ########################################################################")
                            main(settings.LOOP, now_file, step=t)
                        exit()

                elif settings.TEST_STATES_RANGE:
                    #for count in range(0, 10):
                    for s in settings.TEST_STATES_RANGE:
                        for count in range(0, 10):
                        #for s in settings.TEST_STATES_RANGE:
                            now_file = f'{filename}{count}-{s}-{repeat_count}--teststates.txt'
                            print(now_file)
                            if os.path.isfile(now_file):
                                file = open(now_file, "r")
                                content = file.read()
                                file.close()
                                if len(content.splitlines()) > 99:
                                    continue
                            print("REPETITION", count)
                            print(count, "TAKE ########################################################################")
                            main(settings.LOOP, now_file, index=count, states=s)

                else:
                    for count in range(0, 20):
                        now_file = f'{filename}{count}-{settings.STATES}-{repeat_count}.txt'
                        print(now_file)
                        if os.path.isfile(now_file):
                            file = open(now_file, "r")
                            content = file.read()
                            file.close()
                            if len(content.splitlines()) > 99:
                                continue
                        print("REPETITION", count)
                        print(count, "TAKE ########################################################################")
                        main(settings.LOOP, now_file, index=count)
                        #alert.notice()
                    #alert.scream()
                    exit()
    #write_ryu_status(status=False)
