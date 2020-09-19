'''
	NIM	: 1303181077	 
	Nama	: MUhammad Rara El-Ghiffari
	Kelas 	: IT-42-03
'''

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from time import time
from mininet.util import pmonitor
from signal import SIGINT
import os

# (1) Set skenario jaringan dimana server adalah h0 dan client h1 dan h2 dan subprogram test iperf
def testIperf( net, server='h0', clients=('h1', 'h2') ):
    popens = {}
    tperf = 20
    tout = ( tperf + 1 ) * 4
    stopPerf = time() + tout + 5
    inv = 4

    popens[ net[ server ] ] = net[ server ].popen( 'iperf -s -t '+str( tout ) )
    for client in clients:
        popens[ net[ client ] ] = net[ client ].popen( 'iperf -c '+net[ server ].IP()+' -i '+str(inv)+' -t '+str( tperf ) )
    
    logserver = logclient1 = logclient2 = ""

    for host, line in pmonitor(popens, timeoutms=(tperf + tout) * 4):
    	if host:
            if host.name == server: logserver += (host.name +": "+line)
            elif host.name == clients[0]: logclient1 += (host.name +": "+line)
            elif host.name == clients[1]: logclient2 += (host.name +": "+line)


    	if time() >= stopPerf:
    		for p in popens.values(): p.send_signal(SIGINT)

    print(logserver)
    print(logclient1)
    print(logclient2)


def openSwitchNet():
	# (2) Start the Mininet and begin to analysis with iperf
    net = Mininet( controller=Controller, switch=OVSSwitch, link=TCLink )

    info( "* Creating (reference) controllers\n" )
    # (3) Add controller devices to the Network simulation
    c = net.addController( 'c1', port=6633 )

    info( "* Creating switches\n" )
    # (4) Add switch to the Network
    s0 = net.addSwitch( 's0' )

    info( "* Creating hosts\n" )
    # (5) Add host to the Network
    h0 = net.addHost( 'h0', ip='192.168.1.1/24' )
    h1 = net.addHost( 'h1', ip='192.168.1.2/24' )
    h2 = net.addHost( 'h2', ip='192.168.1.3/24' )
    
    info( "* Creating links\n" )
    # (6) Create path and connect the host and switch
    net.addLink( h0, s0, intfName2='s0-eth0', bw=10, use_htb=True ) 
    net.addLink( h1, s0, intfName2='s0-eth1', bw=10, use_htb=True ) 
    net.addLink( h2, s0, intfName2='s0-eth2', bw=10, use_htb=True )

    info( "* Starting network\n" )
    # (7) Start build the predefined network
    net.build()
    # (8) Start to activated the controller
    c.start()
    # (9) Start to activated the switch with the defined controller port 6633
    s0.start([c])

    # (10) Test the network simulation by pinging
    info( '\n', net.ping() ,'\n' )
    

    info( '\n*** Queue Disicline :\n' )
    
    # (11) Set the Queue displine to HTB and run as root
    s0.cmdPrint( 'tc qdisc del dev s0-eth0 root' ) 

    
    s0.cmdPrint( 'tc qdisc add dev s0-eth0 root handle 1:0 htb ' ) 

    # (12) Add the classes
    s0.cmdPrint( 'tc class add dev s0-eth0 parent 1: classid 1:1 htb rate 10Mbit ' )
    
    s0.cmdPrint( 'tc class add dev s0-eth0 parent 1:1 classid 1:2 htb rate 4Mbit ceil 3Mbit ' )
    s0.cmdPrint( 'tc class add dev s0-eth0 parent 1:1 classid 1:3 htb rate 4Mbit ceil 1Mbit ' ) 
    s0.cmdPrint( ' tc class add dev s0-eth0 parent 1:2 classid 1:21 htb rate 2Mbit ceil 2Mbit')
    s0.cmdPrint( ' tc class add dev s0-eth0 parent 1:3 classid 1:31 htb rate 3Mbit ceil 2Mbit')
		
	# (13) Add pfifo queueing
    s0.cmdPrint( ' tc qdisc add dev s0-eth0 parent 1:21 handle 210: pfifo limit 20')
    s0.cmdPrint( ' tc qdisc add dev s0-eth0 parent 1:31 handle 310: pfifo limit 10')
    
	# (14) Set queue discipline filters
    s0.cmdPrint( 'tc filter add dev s0-eth0 parent 1: protocol ip prio 1 u32 match ip src '+net[ 'h0' ].IP()+' flowid 1:21' ) 
    s0.cmdPrint( 'tc filter add dev s0-eth0 parent 1: protocol ip prio 1 u32 match ip src '+net[ 'h1' ].IP()+' flowid 1:31' ) 
    
	# (15) show the result network simulation, run the iperf test and then stop the simulation
    s0.cmdPrint( 'tc qdisc show dev s0-eth0' )
    info( '\n' )

    testIperf( net, 'h0', ('h1', 'h2') )
    net.stop()

if __name__ == '__main__':
    os.system( 'mn -c' )
    os.system( 'clear' )
    setLogLevel( 'info' )
    openSwitchNet()
