#### Pi 3 B+ Config for use as a Network Tap 

#### Usage
Add a [USB Ethernet Adapter](https://www.amazon.com/gp/product/B00FFJ0RKE/) to the pi and setup the pi w/the included configs

#### Expectations
The PI will sit between your Cable Modem and Wireless Router using a Linux Ethernet Bridge.

This can be an alternate deployment than the one at [BriarID](https://github.com/musicmancorley/BriarIDS)

If this config you'll have both Ethernet ports without an IP, but have the PI be accessible via ssh through the local wireless AP for admin access with ssh. 

#### Dependencies 
apt-get install bridge-utils
