#!/bin/bash/python
# _*_ coding: utf-8 _*_
# file： parse_cpu_header
# date-time: 2024/8/13-14:48
# auth:hard work
# description
#"""解析CPU HEADER"""
import binascii
from datetime import datetime


def parser_ToCpuHeader(toCpuHeader):
    cpuHeader = toCpuHeader.replace(' ', '')

    temp = bin(int(cpuHeader, 16))[2:]
    tempS = temp[-8:] + temp[-16:-8] + temp[-24:-16] + temp[-32:-24]
    crcs = int(tempS[-32:-24], 2)
    # print('crcs', crcs)
    reserve4 = int(tempS[-24:-1], 2)
    # print('reserve4', reserve4)

    tempS = temp[-40:-32] + temp[-48:-40] + temp[-56:-48] + temp[-64:-56]
    packetLength = int(tempS[-13:], 2)
    reserve3 = int(tempS[-32:-14], 2)

    tempS = temp[-72:-64] + temp[-80:-72] + temp[-88:-80] + temp[-96:-88]

    outerIsCvlan = int(tempS[-1:], 2)
    srcVlanId = int(tempS[-12:-1], 2)
    srcTagCfi = int(tempS[-13:-12], 2)
    srcTagCos = int(tempS[-16:-14], 2)
    exceptionEn = int(tempS[-17:-16], 2)
    exceptionIndex = int(tempS[-25:-18], 2)
    reserve2 = int(tempS[-32:-26], 2)
    tempS = temp[-104:-96] + temp[-112:-104] + temp[-120:-112] + temp[-128:-120]
    srcPort = int(tempS[-5:], 2)
    truncated = int(tempS[-6:-5], 2)
    priority = int(tempS[-12:-6], 2)
    reserve1 = int(tempS[-20:-12], 2)
    fid = int(tempS[-32:-20], 2)

    tempS = int(temp[-136:-128] + temp[-144:-136] + temp[-152:-144] + temp[-160:-152], 2)
    # print(tempS)

    timestampS = datetime.fromtimestamp(tempS)
    # print("second", timestampS)

    timestampNs = int(temp[-166:-160] + temp[-176:-168] + temp[-184:-176] + temp[-192:-184], 2)
    # print("ns", timestampNs)
    reserve0 = int(temp[-168:-166], 2)
    print('toCpuHeader:')
    print(
        '[timestampNs: %s],[reserve0: %s], '
        '[timestampS: %s or timestampS:%s], [srcPort: %s],'
        ' [truncated: %s],[priority:%s],[reserve1: %s], [fid: %s], [outerIsCvlan: %s], [srcVlanId: %s], '
        '[srcTagCfi: %s], [srcTagCos: %s], [exceptionEn: %s], [exceptionIndex: %s], [reserve2: %s], [packetLength: %s],[reserve3: %s], [reserve4: %s],[crc: %s]' %
        (
            timestampNs, reserve0, timestampS, tempS, srcPort, truncated, priority, reserve1, fid, outerIsCvlan,
            srcVlanId,
            srcTagCfi,
            srcTagCos, exceptionEn, exceptionIndex, reserve2, packetLength, reserve3, reserve4, crcs))
    return {'timestampNs': '%s' % timestampNs, 'reserve0': '%s' % reserve0,
            'timestampS': '%s' % tempS,
            'srcPort': '%s' % srcPort,
            'truncated': '%s' % truncated,
            'priority': '%s' % priority,
            'reserve1': '%s' % reserve1,
            'fid': '%s' % fid,
            'outerIsCvlan': '%s' % outerIsCvlan,
            'srcVlanId': '%s' % srcVlanId,
            'srcTagCfi': '%s' % srcTagCfi,
            'srcTagCos': '%s' % srcTagCos,
            'exceptionEn': '%s' % exceptionEn,
            'exceptionIndex': '%s' % exceptionIndex,
            'reserve2': '%s' % reserve2,
            'packetLength': '%s' % packetLength,
            'reserve3': '%s' % reserve3,
            'reserve4': '%s' % reserve4,
            'crcs': '%s' % crcs}


def cpu_pkt_field_len():
    fromcpuhder_len = {'isRep': 1, 'destMap': 12, 'headerHash': 18, 'hwFwd': 1, 'ingressTsNs': 30, 'reserve0': 2,
                       'opCode': 3,
                       'nextHopId': 14, 'ptpProfileId': 4, 'ptpEn': 1, 'priority': 6, 'learningDisable': 1,
                       'forceDestination': 1, 'criticalPacket': 1, 'forbidEdit': 1, 'reserve1': 24, 'crc': 8}
    return fromcpuhder_len


def cpu_pkt_field():
    """default field"""
    From_cpuHeader_field = {
        'isRep': '0',  # 1bit 0
        'destMap': '000000000000',  # 12bit 	12:1
        'headerHash': '000000000000000000',  # 18bit  	30:13
        'hwFwd': '0',  # 1bit 	31
        'ingressTsNs': '000000000000000000000000000000',  # 30bit 29:0
        'reserve0': '00',  # 3bit 29:31
        'opCode': '000',  # 3bit 2:0
        'nextHopId': '00000000000000',  # 14bit	16:3
        'ptpProfileId': '0000',  # 4bit 20:17
        'ptpEn': '0',  # 1bit 21
        'priorityT': '000000',  # 6bit 27:22
        'learningDisable': '0',  # 1bit 28
        'forceDestination': '0',  # 1bit 29
        'criticalPacket': '0',  # 1bit 30
        'forbidEdit': '0',  # 1bit 31
        'reserve1': '000000000000000000000000'  # 24bit 24:0
    }
    return From_cpuHeader_field


def compose_fromCpuHeader(FromCPUHeader_dicts):
    cpu_pkt = cpu_pkt_field()
    fromCpuHerder_length = cpu_pkt_field_len()
    _str = ""
    _from_cpu_dict = {}
    for k, v in FromCPUHeader_dicts.items():
        input_field = bin(v)[2:]
        if k in fromCpuHerder_length:

            if len(input_field) < fromCpuHerder_length[k]:
                realLength = fromCpuHerder_length[k] - len(input_field)
                _final_input_field = '0' * realLength + input_field
                _from_cpu_dict.update({k: _final_input_field})

            elif len(input_field) == fromCpuHerder_length[k]:
                _from_cpu_dict.update({k: input_field})
            else:
                print(f"{k, v} length error")

        else:
            print(f"{k, v} key error")

    new_str = ""
    for ks, vs in cpu_pkt.items():

        new_str += _from_cpu_dict.get(ks, cpu_pkt[ks])[::-1]

    final_cpu_str = parser_FromCpuHeader(new_str)
    print("\nfromCPUHeader: ", final_cpu_str)


def parser_FromCpuHeader(fromCpuHeader):
    b_list = []

    groups = [fromCpuHeader[i:i + 8] for i in range(0, len(fromCpuHeader), 8)]

    reversed_groups = [group[::-1] for group in groups]

    # hex_str = ''.join(f'{int(binary_string, 2):02x}' for binary_string in reversed_groups)
    hex_str = ""
    for binary_string in reversed_groups:

        tmp = f'{int(binary_string, 2):02x}'
        b_list.append(int(tmp, 16))
        hex_str += tmp

    final_str = hex_str + hex(cal_crc8(b_list))[2:]
    return final_str


def cal_crc(data):
    crc = data
    poly = 0x07  # 多项式x^8 + x^2 + x^1 + 1，即0x107，（根据原理）省略了最高位1而得0x07
    for i in range(8, 0, -1):
        if ((crc & 0x80) >> 7) == 1:  # 判断最高位是否为1，如果是需要异或，否则仅左移
            crc = (crc << 1) ^ poly
        else:
            crc = (crc << 1)
    return crc & 0xFF  # 计算后需要进行截取


def cal_crc8(datas):
    length = len(datas)
    crc = 0x00
    for i in range(length):
        if i == 0:
            crc = cal_crc(datas[0])  # 先计算第1个数据的CRC8
        else:
            crc = (crc ^ datas[i]) & 0xFF  # 其余的均将上次的CRC8结果与本次数据异或
            crc = cal_crc(crc)  # 再计算CRC8
    return crc & 0xFF


if __name__ == '__main__':
    # toCpuHeader = 'e6 b8 e1 18 c8 b9 89 67 00 04 10 00 00 00 08 00 94 00 00 00 00 00 00 a2'
    toCpuHeader = '60214008f9e8a467c000f007fe0020009c000000000000c8'
    parser_ToCpuHeader(toCpuHeader)

    FromCPUHeader_dicts = {
        'destMap': 22,
        'opCode': 1,

    }
    compose_fromCpuHeader(FromCPUHeader_dicts)

