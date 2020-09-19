'''
	NIM	: 1303181077 
	Nama	: Muhammad Rara El-Ghiffari
	Kelas 	: IT-42-03
'''

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import Node
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.util import pmonitor
from signal import SIGINT
from time import time
import os

# (1) setup jaringan dimana server adalah h0 dan sisanya sebagai client
def testIperf( net, server='h0', clients=('h1', 'h2', 'h3') ):
    popens = {}
    tperf = 20
    tout = ( tperf + 1 ) * 4
    stopPerf = time() + tout + 5
    inv = 4

    popens[ net[ server ] ] = net[ server ].popen( 'iperf -s -t '+str( tout ) )
    for client in clients:
        popens[ net[ client ] ] = net[ client ].popen( 'iperf -c '+net[ server ].IP()+' -i '+str(inv)+' -t '+str( tperf ) )
    
    logserver = logclient1 = logclient2 = logclient3 = ""

    for host, line in pmonitor(popens, timeoutms=(tperf + tout) * 4):
    	if host:
            if host.name == server: logserver += (host.name +": "+line)
            elif host.name == clients[0]: logclient1 += (host.name +": "+line)
            elif host.name == clients[1]: logclient2 += (host.name +": "+line)
            elif host.name == clients[2]: logclient3 += (host.name +": "+line)

    	if time() >= stopPerf:
    		for p in popens.values(): p.send_signal(SIGINT)

    print(logserver)
    print(logclient1)
    print(logclient2)
    print(logclient3)
      
def routerNet():
    # (2) Run Mininet
    net = Mininet( link=TCLink )
    
    # (3) Setup and add Host in the Topology
    net.addHost( 'r0', ip='192.168.1.1/24' )
    net.addHost( 'h0', ip='192.168.1.2/29', defaultRoute='via 192.168.1.1' )
    net.addHost( 'h1', ip='123.123.123.2/29', defaultRoute='via 123.123.123.1' )
    net.addHost( 'h2', ip='10.16.0.2/29', defaultRoute='via 10.16.0.1' )
    net.addHost( 'h3', ip='200.100.1.2/29', defaultRoute='via 200.100.1.1' )

    # (4) Setup the connection between devices
    net.addLink( net[ 'h0' ], net[ 'r0' ], intfName2='r0-eth0', bw=10 ) 
    net.addLink( net[ 'h1' ], net[ 'r0' ], intfName2='r0-eth1', bw=10 ) 
    net.addLink( net[ 'h2' ], net[ 'r0' ], intfName2='r0-eth2', bw=10 )
    net.addLink( net[ 'h3' ], net[ 'r0' ], intfName2='r0-eth3', bw=10 )

    # (5) Setup the line in the Topology
    net[ 'r0' ].cmd( 'ip addr add 192.168.1.1/29 brd + dev r0-eth0' )
    net[ 'r0' ].cmd( 'ip addr add 123.123.123.1/29 brd + dev r0-eth1' )
    net[ 'r0' ].cmd( 'ip addr add 10.16.0.1/29 brd + dev r0-eth2' )
    net[ 'r0' ].cmd( 'ip addr add 200.100.1.1/29 brd + dev r0-eth3' )
    
    # (6) Network system controller
    net[ 'r0' ].cmd( 'sysctl net.ipv4.ip_forward=1' )
    
    # (7) Start the Mininet
    net.start()
    
    # (8) Ping the Connection
    info( '\n', net.ping() ,'\n' )
    
    # (9) Output
    info( '\n*** Queue Disicline :\n' )
    
    # (10) Set Queue Discipline to CBQ
    net[ 'r0' ].cmdPrint( 'tc qdisc del dev r0-eth0 root' ) 

    # (11) Setup parameter rate dan avpkt
    net[ 'r0' ].cmdPrint( 'tc qdisc add dev r0-eth0 root handle 1: cbq rate 5Mbit avpkt 1000' ) 
    
    # (12) Set the Queue discipline and add the classes 
    net[ 'r0' ].cmdPrint( 'tc class add dev r0-eth0 parent 1: classid 1:1 cbq rate 3Mbit avpkt 1000 bounded' )
    net[ 'r0' ].cmdPrint( 'tc class add dev r0-eth0 parent 1: classid 1:2 cbq rate 3Mbit avpkt 1000 isolated' ) 

    # (13) Set Queue discipline filters
    net[ 'r0' ].cmdPrint( 'tc filter add dev r0-eth0 parent 1: protocol ip u32 match ip src '+net[ 'h1' ].IP()+' flowid 1:1' ) 
    net[ 'r0' ].cmdPrint( 'tc filter add dev r0-eth0 parent 1: protocol ip u32 match ip src '+net[ 'h2' ].IP()+' flowid 1:2' ) 
    net[ 'r0' ].cmdPrint( 'tc qdisc show dev r0-eth0' )
    info( '\n' )

    # (14) Test Iperf 
    testIperf( net, 'h0', ('h1', 'h2', 'h3') )

    # (15) Stop Mininet
    net.stop()

if __name__ == '__main__':
    os.system('mn -c')
    os.system( 'clear' )
    setLogLevel( 'info' )
    routerNet()
