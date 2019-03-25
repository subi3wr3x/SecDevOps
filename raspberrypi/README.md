#### Pi 3 B+ Config for use as a Network Tap 

#### Usage
Add a [USB Ethernet Adapter](https://www.amazon.com/gp/product/B00FFJ0RKE/) to the pi and setup the pi w/the included configs

#### Expectations
The PI will sit between your Cable Modem and Wireless Router using a Linux Ethernet Bridge.

This can be an alternate deployment than the one at [BriarIDS](https://github.com/musicmancorley/BriarIDS/wiki/Deployment-Instructions)

If this config you'll have both Ethernet ports without an IP, but have the PI be accessible via ssh through the local wireless AP for admin access with ssh. 

You can tryout BriarIDS as mentioned or go on your on using any of Suricata, Bro, Snort, etc.

#### Dependencies 
apt-get install bridge-utils

#### Extra Fun
Install the [DataPlicity](https://www.dataplicity.com) client and connect to your PI from anywhere.
