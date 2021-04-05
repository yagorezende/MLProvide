#!/bin/bash
source venv/bin/activate
ryu-manager ryu_apps/simple_switch_stp_13.py ryu_apps/ofctl_rest.py --observe-links &
sudo python ryu_apps/simpleTopo.py
sudo python ryu_apps/killRyu.py
