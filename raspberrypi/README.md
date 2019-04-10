#### Pi 3 B+ Config for use as a Network Tap 

#### Usage
Add a [USB Ethernet Adapter](https://www.amazon.com/gp/product/B00FFJ0RKE/) to the pi and setup the pi w/the included configs

#### Expectations
The PI will sit between your Cable Modem and Wireless Router using a [Linux Ethernet Bridge](http://www.microhowto.info/howto/bridge_traffic_between_two_or_more_ethernet_interfaces_on_linux.html):

```
+-------------------+
|                   |
|    Cable Modem    |
|                   |
+----+--------------+
     |
     |
     |
     +<------------------Eth0 (No IP)--+
     |
     +-----+
     |     |
     | Pi  |
     |     |XXXXXXXXXXX...Wifi Signal.....XXXXXXXXX
     +----++                                    XX
          |                                    XX
          +<-------------Eth1 (No IP)--+      XX
          |                                  XX
      +---+---------------------------+    XXX
      |  (DMZ port has the ISP IP)    |  XXX
      |                               | XX
      |  Wirleless Router             |XX
      |                               |
      |  (internal ports)             |
      +-------------------------------+
         |
         |
        +------------------------+
        | Internal wired pc, etc.|
        +------------------------+

```

This can be an alternate deployment than the one at [BriarIDS](https://github.com/musicmancorley/BriarIDS/wiki/Deployment-Instructions)

In this config you'll have both Ethernet ports without an IP (ifconfig output below), but have the PI be accessible via ssh through the local wireless AP for admin access with ssh. 

You can tryout BriarIDS as mentioned or go on your on using any of Suricata, Bro, Snort, etc.

#### Dependencies 
apt-get install bridge-utils

#### ifconfig

```
br0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::3e8c:f8ff:feff:8e00  prefixlen 64  scopeid 0x20<link>
        ether 3c:8c:f8:ff:8e:00  txqueuelen 1000  (Ethernet)
        RX packets 19271001  bytes 936365318 (892.9 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 34  bytes 3114 (3.0 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        ether b8:27:eb:11:05:34  txqueuelen 1000  (Ethernet)
        RX packets 7923169  bytes 1482418997 (1.3 GiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 33942973  bytes 3411605549 (3.1 GiB)
        TX errors 78  dropped 78 overruns 0  carrier 0  collisions 0

eth1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        ether 3c:8c:f8:ff:8e:00  txqueuelen 1000  (Ethernet)
        RX packets 33943235  bytes 20116284673 (18.7 GiB)
        RX errors 1844  dropped 0  overruns 0  frame 1844
        TX packets 7923192  bytes 1545805272 (1.4 GiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 388  bytes 54562 (53.2 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 388  bytes 54562 (53.2 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.0.199  netmask 255.255.255.0  broadcast 192.168.0.255
        inet6 fe80::d3b1:d50b:a9c0:d153  prefixlen 64  scopeid 0x20<link>
        ether b8:27:eb:44:50:61  txqueuelen 1000  (Ethernet)
        RX packets 1006190  bytes 388728973 (370.7 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 1721033  bytes 812955265 (775.2 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

#### Extra Fun
Install the [DataPlicity](https://www.dataplicity.com) client and connect to your PI from anywhere.

#### Fancy Images By  ####
[http://asciiflow.com/](http://asciiflow.com/)
