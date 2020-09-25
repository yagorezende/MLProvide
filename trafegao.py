import argparse
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("index", help="display a square of a given number",
                        type=int)
    args = parser.parse_args()

    cmd = f"tcpreplay -i h{args.index}-eth0 -l 0 --multiplier=100000 /home/reiner/Mestrado/pcaps/client{args.index}.pcap"

    print(cmd)
    os.system(cmd)



