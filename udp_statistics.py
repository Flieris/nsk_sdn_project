import sqlite3
import datetime
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ether
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import in_proto
from ryu.lib.packet import ipv4
from ryu.lib.packet import udp


DATABASE_FILE = "./statisticsDB.db"


class UdpStatistics(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(UdpStatistics, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(
            ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]

        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        in_port = msg.match['in_port']
        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            # we mostly want to get UDP statistics
            # probably could extend it to gather info of all protocols
            ip = pkt.get_protocol(ipv4.ipv4)
            src_ip = ip.src
            dst_ip = ip.dst
            protocol = ip.proto

            if protocol == in_proto.IPPROTO_UDP:
                u = pkt.get_protocol(udp.udp)
                pkt.serialize()
                self.save_packet_information(pkt)
                self.logger.debug("Source Address: %s:%s, Destination Address: %s:%s, dataload: %s",
                                  src_ip, u.src_port, dst_ip, u.dst_port, pkt[-1].rstrip())

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def save_packet_information(self, data_packet):
        ip_pkt = data_packet.get_protocol(ipv4.ipv4)
        udp_dtg = data_packet.get_protocol(udp.udp)
        eth_pkt = data_packet.get_protocol(ethernet.ethernet)
        conn = get_database(DATABASE_FILE)
        # insert data
        if conn is not None:
            # validate if packet information is already in database
            cur = conn.cursor()
            validate = "select count(*) from tudpstatistics where id = " + \
                str(ip_pkt.identification)
            cur.execute(validate)
            row = cur.fetchone()
            if row[0] == 1:
                return
            self.logger.debug("Count(*) rows: %s", row[0])
            # insert udp packet stats
            query1 = "insert into tudpstatistics(id,event_time,source_ip,source_port,destination_ip,destination_port,payload) values({},'{}','{}',{},'{}',{},'{}')".format(
                ip_pkt.identification, datetime.datetime.now(), ip_pkt.src, udp_dtg.src_port, ip_pkt.dst, udp_dtg.dst_port, data_packet[-1].rstrip())
            cur.execute(query1)
            cur.close()
            # insert or update host info
            self.save_host_information(
                ip_pkt.src, eth_pkt.src, udp_dtg.total_length, conn)
            conn.close()

    def save_host_information(self, ip_addr, eth_addr, data, conn):
        if conn is not None:
            # validate
            cur = conn.cursor()
            validate = "select count(*) from thoststatistics where id = '{}'".format(eth_addr)
            cur.execute(validate)
            row = cur.fetchone()
            if row[0] == 0:
                insert = "insert into thoststatistics(id, ip_addr, eth_addr, total_data)values('{}', '{}', '{}', {})".format(
                    eth_addr, ip_addr, eth_addr, data)
                cur.execute(insert)
            else:
                update = "update thoststatistics set total_data=total_data+{} where id = '{}'".format(
                    data, eth_addr)
                cur.execute(update)
            cur.close()
            return


def get_database(file):
    try:
        conn = sqlite3.connect(file)
        return conn
    except sqlite3.Error as e:
        print e
    return None
