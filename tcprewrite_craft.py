import os, re


l = os.listdir('pcaps')
print(l)
for file in l:
    index = file.replace("client", "").replace(".pcap", "")

    cmd = f"tcprewrite -D [0.0.0.0/0]:[10.0.0.1] -S [0.0.0.0/0]:[10.0.0.{index}] "\
          f"--enet-dmac=00:00:00:00:00:01  --enet-smac=00:00:00:00:00:02 "\
          f"-o pcaps/client{index}.pcap -i pcaps/client{index}.pcap --hdlc-address 0x0F --hdlc-control 0"

    b = os.popen(cmd)

    print(b)
    print(cmd)

