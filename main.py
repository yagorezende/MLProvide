import models
from models import settings, pomdp_mapper, agent, alert, ryuapi
import psutil
import traceback
import time
import numpy as np
import os


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


def main(max_t, filename, states=settings.STATES, step=settings.STEP, index=1):
    print('FILENAME=', filename)
    cpus = []
    differ = pomdp_mapper.NetProcDiff()
    t = 0
    client_count = ryuapi.RyuApi().client_count()
    dc = models.DC(cap=settings.MAX_SERVER_LOAD*client_count)
    clients = list()
    print("CLIENT COUNT: ", client_count)

    for i in range(client_count):
        clients.append(models.Client(i + 2, settings.CLIENT1_BW + i*50, dc, states=states))




    rp = models.RewardProvider(settings.SERVER_IP, clients, dc, pomdp=settings.POMDP)


    try:
        rp.enabled = True
        if settings.PARALLEL:
            rp.parallel_start()
        while 1:
            print("T =", t, " ------------------------------------------------------------------")
            if settings.INTERCALATE:
                if t % 2 == 0:
                    settings.POMDP = True
                else:
                    settings.POMDP = False

            cpus.append((psutil.cpu_percent(), psutil.virtual_memory().percent, rp.dc.load))
            differ.dump_diff(psutil.cpu_percent(), psutil.virtual_memory().percent, rp.dc.load)

            # print("CPU=", np.mean(cpus))
            time.sleep(step)
            rp.step()
            t += 1
            if t > max_t:
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
    if input("The current data will be destroyed, is this ok?") == "y":
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
                f'results-dataset_{settings.STRATEGY.split("_")[0]}/{settings.STRATEGY.split("_")[0]}-compare-VT{sm}{trained}',
            ]


            for filename in filenames:
                if filename.lower().count('pomdp'):
                    settings.POMDP = True
                elif filename.lower().count('inter'):
                    settings.POMDP = True
                    settings.INTERCALATE = True
                if settings.FUZZY:
                    for t in fuzzy_times:

                        for count in range(0, 100):
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
                else:
                    for count in range(0, 100):

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
                        alert.notice()
                    alert.scream()
                    exit()
