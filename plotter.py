import json
import glob
import re
import os
import matplotlib.pyplot as plt
import numpy as np
import statistics

tests = dict(dict(dict()))
PLOTSDIR = "plots-webcam"
RESULTSDIR = "results-webcam"
def init_dict():
        tests['ch-ch'] = dict(dict())
        tests['ch-fi'] = dict(dict())
        tests['ch-op'] = dict(dict())
        tests['fi-fi'] = dict(dict())
        tests['fi-ch'] = dict(dict())
        tests['fi-op'] = dict(dict())
        tests['op-op'] = dict(dict())
        tests['op-fi'] = dict(dict())
        tests['op-ch'] = dict(dict())

        for comb in tests:
            tests[comb]['client1'] = dict()
            tests[comb]['client2'] = dict()
            tests[comb]['client1']['video'] = dict()
            tests[comb]['client2']['video'] = dict()
            tests[comb]['client1']['audio'] = dict()
            tests[comb]['client2']['audio'] = dict()
            tests[comb]['client1']['video']['fps'] = 0
            tests[comb]['client2']['video']['fps'] = 0
            tests[comb]['client1']['video']['packets_received'] = []
            tests[comb]['client2']['video']['packets_received'] = []
            tests[comb]['client1']['video']['packets_lost'] = []
            tests[comb]['client2']['video']['packets_lost'] = []
            tests[comb]['client1']['audio']['packets_received'] = []
            tests[comb]['client2']['audio']['packets_received'] = []
            tests[comb]['client1']['audio']['packets_lost'] = []
            tests[comb]['client2']['audio']['packets_lost'] = []
            tests[comb]['client1']['video']['frames_encoded'] = []
            tests[comb]['client1']['video']['frames_decoded'] = []
            tests[comb]['client2']['video']['frames_encoded'] = []
            tests[comb]['client2']['video']['frames_decoded'] = []
            tests[comb]['client1']['video']['bytes_sent'] = []
            tests[comb]['client2']['video']['bytes_sent'] = []
            tests[comb]['client1']['video']['bytes_received'] = []
            tests[comb]['client2']['video']['bytes_received'] = []
            tests[comb]['client1']['audio']['bytes_sent'] = []
            tests[comb]['client2']['audio']['bytes_sent'] = []
            tests[comb]['client1']['audio']['bytes_received'] = []
            tests[comb]['client2']['audio']['bytes_received'] = []
            tests[comb]['client1']['timestamp'] = []
            tests[comb]['client2']['timestamp'] = []
            tests[comb]['client1']['audio']['jitter'] = []
            tests[comb]['client1']['video']['jitter'] = []
            tests[comb]['client2']['audio']['jitter'] = []
            tests[comb]['client2']['video']['jitter'] = []

std_devs = dict(dict(dict()))
def init_stdev_dict():
        std_devs['ch-ch'] = dict(dict())
        std_devs['ch-fi'] = dict(dict())
        std_devs['ch-op'] = dict(dict())
        std_devs['fi-fi'] = dict(dict())
        std_devs['fi-ch'] = dict(dict())
        std_devs['fi-op'] = dict(dict())
        std_devs['op-op'] = dict(dict())
        std_devs['op-fi'] = dict(dict())
        std_devs['op-ch'] = dict(dict())

        for comb in std_devs:
            std_devs[comb]['client1'] = dict()
            std_devs[comb]['client2'] = dict()
            std_devs[comb]['client1']['video'] = dict()
            std_devs[comb]['client2']['video'] = dict()
            std_devs[comb]['client1']['audio'] = dict()
            std_devs[comb]['client2']['audio'] = dict()
            std_devs[comb]['client1']['video']['fps'] = 0
            std_devs[comb]['client2']['video']['fps'] = 0
            std_devs[comb]['client1']['video']['packets_received'] = []
            std_devs[comb]['client2']['video']['packets_received'] = []
            std_devs[comb]['client1']['video']['packets_lost'] = []
            std_devs[comb]['client2']['video']['packets_lost'] = []
            std_devs[comb]['client1']['audio']['packets_received'] = []
            std_devs[comb]['client2']['audio']['packets_received'] = []
            std_devs[comb]['client1']['audio']['packets_lost'] = []
            std_devs[comb]['client2']['audio']['packets_lost'] = []
            std_devs[comb]['client1']['video']['frames_encoded'] = []
            std_devs[comb]['client1']['video']['frames_decoded'] = []
            std_devs[comb]['client2']['video']['frames_encoded'] = []
            std_devs[comb]['client2']['video']['frames_decoded'] = []
            std_devs[comb]['client1']['video']['bytes_sent'] = []
            std_devs[comb]['client2']['video']['bytes_sent'] = []
            std_devs[comb]['client1']['video']['bytes_received'] = []
            std_devs[comb]['client2']['video']['bytes_received'] = []
            std_devs[comb]['client1']['audio']['bytes_sent'] = []
            std_devs[comb]['client2']['audio']['bytes_sent'] = []
            std_devs[comb]['client1']['audio']['bytes_received'] = []
            std_devs[comb]['client2']['audio']['bytes_received'] = []
            std_devs[comb]['client1']['timestamp'] = []
            std_devs[comb]['client2']['timestamp'] = []
            std_devs[comb]['client1']['audio']['jitter'] = []
            std_devs[comb]['client1']['video']['jitter'] = []
            std_devs[comb]['client2']['audio']['jitter'] = []
            std_devs[comb]['client2']['video']['jitter'] = []


def load_data(file):
    with open(file) as results_file:
        print(f"Loading file: {file}")
        data = json.load(results_file)
        name = data['name']
        browsercomb = get_browsers(name)
        tests[browsercomb]['client1']['stats-raw'] = "kite-allure-reports/" + data['steps'][9]['attachments'][0]['source']
        tests[browsercomb]['client1']['stats-summary'] = "kite-allure-reports/" + data['steps'][9]['attachments'][1]['source']
        tests[browsercomb]['client2']['stats-raw'] = "kite-allure-reports/" + data['steps'][10]['attachments'][0]['source']
        tests[browsercomb]['client2']['stats-summary'] = "kite-allure-reports/" + data['steps'][10]['attachments'][1]['source']
        parse_summary(browsercomb, 'client1')
        parse_summary(browsercomb, 'client2')
        parse_raw(browsercomb, 'client1')
        parse_raw(browsercomb, 'client2')

def get_results():
    # getting the result files
    files = glob.glob('kite-allure-reports/*-result.json')

    for file in files:
        load_data(file)

# Get and return browser names
def get_browsers(name):
    browsers = re.findall(r"_\w*_", name)
    browser1 = browsers[0][1:-1]
    browser2 = browsers[1][1:-1]

    browsercomb = browser1 + "-" + browser2
    tests[browsercomb]['client1']['browser'] = browser1
    tests[browsercomb]['client2']['browser'] = browser2

    return browsercomb

# Parse a summary for a test of 2 clients
def parse_summary(browsercomb, client):
    with open(tests[browsercomb][client]['stats-summary']) as results_file:
        data = json.load(results_file)
        tests[browsercomb][client]['rtt'] = data['avg_current_rtt(ms)']
        tests[browsercomb][client]['video']['fps'] = data['inbound']['video'][0]['avg_frame_rate(fps)']

def parse_raw(browsercomb, client):
    parse_stats_array(browsercomb, client)

def parse_stats_array(browsercomb, client):
    audio_packets_received = audio_packets_lost = video_packets_received = video_packets_lost = 0
    count_inbound = count_outbound = 0

    with open(tests[browsercomb][client]['stats-raw']) as results_file:
            data = json.load(results_file)
            timestamps = []
            audio_packets_received = []
            video_packets_received = []
            video_bytes_received = []
            video_bytes_sent = []
            audio_bytes_received = []
            audio_bytes_sent = []
            frames_encoded = []
            frames_decoded = []

            for stats in data['StatsArray']:
                cnt = 0
                for (key, value) in stats['outbound-rtp'].items():
                    # first value is always for audio
                    if cnt%2 == 0: # timeselapsed
                        audio_bytes_sent.append(int(value['bytesSent']))
                    # second value is always for video
                    else:
                        video_bytes_sent.append(int(value['bytesSent']))
                        frames_encoded.append(int(value['framesEncoded']))
                    cnt+=1
                cnt = 0
                for (key, value) in stats['inbound-rtp'].items():
                    if cnt%2 == 0:
                        audio_packets_received.append(int(value['packetsReceived']))
                        tests[browsercomb][client]['audio']['packets_lost'].append(float(value['packetsLost']))
                        tests[browsercomb][client]['audio']['jitter'].append(float(value['jitter']))
                        audio_bytes_received.append(int(value['bytesReceived']))
                    else:
                        video_packets_received.append(int(value['packetsReceived']))
                        tests[browsercomb][client]['video']['packets_lost'].append(float(value['packetsLost']))
                        tests[browsercomb][client]['video']['jitter'].append(float(value['jitter']))
                        video_bytes_received.append(int(value['bytesReceived']))
                        frames_decoded.append(int(value['framesDecoded']))
                        timestamps.append(float(value['timestamp']))
                    cnt+=1
            for i in range (len(timestamps)):
                if i == 0:
                    tests[browsercomb][client]['timestamp'].append(0.0)
                else:
                    difference = (timestamps[i] - timestamps[i - 1]) / 1000
                    timestamp = tests[browsercomb][client]['timestamp'][i - 1] + difference
                    tests[browsercomb][client]['timestamp'].append(timestamp)
            
            # Audio/video packets sent
            for i in range (len(video_packets_received)):
                if i == 0:
                    tests[browsercomb][client]['video']['packets_received'].append(video_packets_received[i])
                    tests[browsercomb][client]['audio']['packets_received'].append(audio_packets_received[i])
                else:
                    difference_vid = (video_packets_received[i] - video_packets_received[i - 1])
                    tests[browsercomb][client]['video']['packets_received'].append(difference_vid)

                    difference_audio = (audio_packets_received[i] - audio_packets_received[i - 1])
                    tests[browsercomb][client]['audio']['packets_received'].append(difference_audio)
            
            # Audio/video bytes sent
            for i in range (len(video_packets_received)):
                if i == 0:
                    tests[browsercomb][client]['video']['bytes_sent'].append(video_bytes_sent[i])
                    tests[browsercomb][client]['audio']['bytes_sent'].append(audio_bytes_sent[i])
                else:
                    difference_vid = (video_bytes_sent[i] - video_bytes_sent[i - 1])
                    tests[browsercomb][client]['video']['bytes_sent'].append(difference_vid)

                    difference_audio = (audio_bytes_sent[i] - audio_bytes_sent[i - 1])
                    tests[browsercomb][client]['audio']['bytes_sent'].append(difference_audio)

            # Audio/video bytes received
            for i in range (len(video_bytes_received)):
                if i == 0:
                    tests[browsercomb][client]['video']['bytes_received'].append(video_bytes_received[i])
                    tests[browsercomb][client]['audio']['bytes_received'].append(audio_bytes_received[i])
                else:
                    difference_vid = (video_bytes_received[i] - video_bytes_received[i - 1])
                    tests[browsercomb][client]['video']['bytes_received'].append(difference_vid)

                    difference_audio = (audio_bytes_received[i] - audio_bytes_received[i - 1])
                    tests[browsercomb][client]['audio']['bytes_received'].append(difference_audio)

            # Frames encoded/decoded
            for i in range (len(frames_decoded)):
                if i == 0:
                    tests[browsercomb][client]['video']['frames_encoded'].append(frames_encoded[i])
                    tests[browsercomb][client]['video']['frames_decoded'].append(frames_decoded[i])
                else:
                    differerence_frames_enc = (frames_encoded[i] - frames_encoded[i - 1])
                    tests[browsercomb][client]['video']['frames_encoded'].append(differerence_frames_enc)

                    differerence_frames_dec = (frames_decoded[i] - frames_decoded[i - 1])
                    tests[browsercomb][client]['video']['frames_decoded'].append(differerence_frames_dec)

def plot_rtt():
    client1_values = []
    client2_values = []
    names = []
    for comb in tests:
        names.append(comb)
        client1_values.append(tests[comb]['client1']['rtt'])
        client2_values.append(tests[comb]['client2']['rtt'])


    plt.bar(names, client1_values, label='client-1')
    plt.bar(names, client2_values, label='client-2')
    plt.xlabel('browser combination')
    plt.legend()
    plt.savefig(f"{PLOTSDIR}/rtt.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)
    plt.clf()


def plot_fps(combs):
    client1_values = []
    client1_errors = []
    client2_values = []
    client2_errors = []
    names = []
    width = 0.32

    plt.rcParams.update({'font.size': 15})
    for comb in combs:
        names.append(comb)
        client1_values.append(int(tests[comb]['client1']['video']['fps']))
        client1_errors.append(int(std_devs[comb]['client1']['video']['fps']))
        client2_values.append(int(tests[comb]['client2']['video']['fps']))
        client2_errors.append(int(std_devs[comb]['client2']['video']['fps']))
    
    ind = np.arange(len(names))
    c1 = plt.bar(ind+width*1/2, client1_values, width, yerr=client1_errors, align='center', capsize=5, label='client-1', color = 'dimgray')
    c2 = plt.bar(ind+width*3/2, client2_values, width, yerr = client2_errors, align='center', capsize=5, label='client-2', color = 'blue')
    plt.xlabel('browser combination')
    plt.ylabel('Frames per Second')
    plt.xticks(ticks=ind+width, labels=names)
    plt.ylim(0, 5)

    plt.legend()
    plt.ylim(bottom=0)
    plt.ylim(top=40)

    autolabel(c1)
    autolabel(c2)
    plt.savefig(f"{PLOTSDIR}/fps-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)
    plt.clf()


def plot_ps(type1, type2, combs):
    client1_values = []
    client2_values = []
    names = []
    width = 0.32

    for comb in combs:
        plt.errorbar(np.array(tests[comb]['client1']['timestamp']), np.array(tests[comb]['client1'][type1][type2]), yerr=std_devs[comb]['client1'][type1][type2], capsize=5, label=comb)

    plt.xlabel('time(s)')

    # plt.xticks(np.arange(0, plot_x_limit, step=1))
    plt.legend()
    plt.xlim([-0.1, plot_x_limit])
    if (type2 != 'bytes_sent' and type2 != 'bytes_received'):
        ymax = 150 if type1 == 'audio' else 800
        plt.ylim(0, ymax)
        plt.ylabel("Packets")
    plt.rcParams.update({'font.size': 15})

    if (type1 == 'audio'):
        if (type2 == 'packets_received'):
            plt.savefig(f"{PLOTSDIR}/audio-packets-sent-ps-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)
        if (type2 == 'bytes_sent'):
            plt.savefig(f"{PLOTSDIR}/audio-bytes-sent-ps-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)
        if (type2 == 'bytes_received'):
            plt.savefig(f"{PLOTSDIR}/audio-bytes-received-ps-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)

    else:
        if (type2 == 'packets_received'):
            plt.savefig(f"{PLOTSDIR}/video-packets-sent-ps-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)
        if (type2 == 'bytes_sent'):
            plt.savefig(f"{PLOTSDIR}/video-bytes-sent-ps-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)
        if (type2 == 'bytes_received'):
            plt.savefig(f"{PLOTSDIR}/video-bytes-received-ps-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)
    plt.clf()


def plot_total_packets_received(type, combs):
    client1_values = []
    client2_values = []
    client1_errors = []
    names = []
    width = 0.32

    for comb in combs:
        names.append(comb)
        client1_values.append(sum(tests[comb]['client1'][type]['packets_received']))
        client1_errors.append(statistics.mean(std_devs[comb]['client1'][type]['packets_received']))
    
    ind = np.arange(len(names))
    c1 = plt.bar(ind+width, client1_values, width, yerr=client1_errors, capsize=5, align='center')
    plt.xlabel('browser combination')
    plt.xticks(ticks=ind+width, labels=names)
    plt.rcParams.update({'font.size': 15})
    plt.ylabel("Packets")


    ymax = 1200 if type == 'audio' else 5300
    plt.ylim(0, ymax)
    autolabel(c1)
    
    if (type == 'audio'):
        plt.savefig(f"{PLOTSDIR}/total-audio-packets-received-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)
    if (type == 'video'):
        plt.savefig(f"{PLOTSDIR}/total-video-packets-received-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)

    plt.clf()


def plot_total_bytes(type1, type2, combs):
    """ type1 = audio/video
        type2 = sent/received"""

    client1_values = []
    client2_values = []
    client1_errors = []
    names = []
    width = 0.32

    for comb in combs:
        names.append(comb)
        client1_values.append(sum(tests[comb]['client1'][type1][f"bytes_{type2}"]))
        client1_errors.append(statistics.mean(std_devs[comb]['client1'][type1][f"bytes_{type2}"]))
    
    ind = np.arange(len(names))
    c1 = plt.bar(ind+width, client1_values, width, yerr=client1_errors, capsize=5, align='center')
    plt.xlabel('browser combination')
    plt.xticks(ticks=ind+width, labels=names)
    plt.ylabel("Bytes")
    plt.rcParams.update({'font.size': 15})

    # ymax = 1200 if type == 'audio' else 5300
    # plt.ylim(0, ymax)
    autolabel(c1)

    plt.savefig(f"{PLOTSDIR}/total-{type1}-bytes-{type2}-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)

    plt.clf()

def plot_total_audio_bytes(client, type2, combs):
    """type2 = sent/received"""

    client_values = []
    client_errors = []
    names = []
    width = 0.32

    for comb in combs:
        names.append(comb)
        client_values.append(sum(tests[comb][client]['audio'][f"bytes_{type2}"]))
        client_errors.append(statistics.mean(std_devs[comb][client]['audio'][f"bytes_{type2}"]))
    
    ind = np.arange(len(names))
    c1 = plt.bar(ind+width, client_values, width, yerr=client_errors, capsize=5, align='center')
    plt.xlabel('browser combination')
    plt.xticks(ticks=ind+width, labels=names)
    plt.ylabel("Bytes")
    plt.rcParams.update({'font.size': 15})

    # ymax = 1200 if type == 'audio' else 5300
    # plt.ylim(0, ymax)
    autolabel(c1)

    plt.savefig(f"{PLOTSDIR}/total-audio-bytes-{type2}-{'_'.join(map(str, combs))}-client2.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)

    plt.clf()

def plot_jitter(type, combs):
    client1_values = []
    client2_values = []
    names = []
    width = 0.32

    for comb in combs:
        plt.errorbar(np.array(tests[comb]['client1']['timestamp']), np.array(tests[comb]['client1'][type]['jitter']), std_devs[comb]['client1'][type]['jitter'], capsize=5, label=comb)

    plt.xlabel('time(s)')
    plt.ylabel('Average jitter (ms)')
    plt.legend()
    plt.xlim([-0.1, plot_x_limit])
    plt.rcParams.update({'font.size': 15})

    if type == 'audio':
        plt.savefig(f"{PLOTSDIR}/audio-jitter-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)
    else:
        plt.savefig(f"{PLOTSDIR}/video-jitter-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)
    plt.clf()


def plot_frames(type, combs):
    client1_values = []
    client2_values = []
    names = []
    width = 0.32

    for comb in combs:
        plt.errorbar(np.array(tests[comb]['client1']['timestamp']), np.array(tests[comb]['client1']['video'][type]), yerr=std_devs[comb]['client1']['video'][type], capsize=5, label=comb)

    plt.xlabel('time(s)')
    plt.ylabel('Frames')
    plt.legend(ncol=2) # ncol=2 for multi column
    plt.xlim([-0.1, plot_x_limit])

    y_max = 100
    plt.ylim(0, y_max)
    plt.rcParams.update({'font.size': 15})

    if (type == 'frames_encoded'):
        plt.savefig(f"{PLOTSDIR}/frames-encoded-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)
    else:
        plt.savefig(f"{PLOTSDIR}/frames-decoded-{'_'.join(map(str, combs))}.png", dpi=200, bbox_inches='tight', pad_inches = 0.05)

    plt.clf()

def autolabel(client):
    for c in client:
        h = c.get_height()
        plt.text(c.get_x()+c.get_width()/2., h, '%d'%int(h),
                ha='center', va='bottom')

def avg_dicts(client, results):

    # average timestamps
    for comb in tests:
        i = 0
        while (i < len(results[0]['ch-ch'][client]['timestamp'])):
            avg_timestamps = []
            for dict in results:
                avg_timestamps.append(dict[comb][client]['timestamp'][i])
            avt = statistics.mean(avg_timestamps)
            std_devs[comb][client]['timestamp'].append(statistics.stdev(avg_timestamps))
            tests[comb][client]['timestamp'].append(avt)
            i+=1


    for comb in tests:
        i = 0           
        while (i < len(results[0]['ch-ch'][client]['video']['jitter'])):
            avg_video_jitter = []
            avg_audio_jitter = []
            for dict in results:
                avg_video_jitter.append(dict[comb][client]['video']['jitter'][i])
                avg_audio_jitter.append(dict[comb][client]['audio']['jitter'][i])
            avj = statistics.mean(avg_video_jitter)
            aaj = statistics.mean(avg_audio_jitter)

            std_devs[comb][client]['video']['jitter'].append(statistics.stdev(avg_video_jitter))
            std_devs[comb][client]['audio']['jitter'].append(statistics.stdev(avg_audio_jitter))
            tests[comb][client]['video']['jitter'].append(avj)
            tests[comb][client]['audio']['jitter'].append(aaj)
            i+=1


    # average packets sent
    for comb in tests:
        i = 0           
        while (i < len(results[0]['ch-ch'][client]['video']['packets_received'])): # video and audio have same length
            avg_v_packets_received = []
            avg_a_packets_received = []
            for dict in results:
                avg_v_packets_received.append(dict[comb][client]['video']['packets_received'][i])
                avg_a_packets_received.append(dict[comb][client]['audio']['packets_received'][i])
            avs = statistics.mean(avg_v_packets_received)
            aas = statistics.mean(avg_a_packets_received)
            std_devs[comb][client]['video']['packets_received'].append(statistics.stdev(avg_v_packets_received))
            std_devs[comb][client]['audio']['packets_received'].append(statistics.stdev(avg_a_packets_received))
            tests[comb][client]['video']['packets_received'].append(avs)
            tests[comb][client]['audio']['packets_received'].append(aas)
            i+=1

    # average bytes sent
    for comb in tests:
        i = 0           
        while (i < len(results[0]['ch-ch'][client]['video']['bytes_sent'])): # video and audio have same length
            avg_v_bytes_sent = []
            avg_a_bytes_sent = []
            for dict in results:
                avg_v_bytes_sent.append(dict[comb][client]['video']['bytes_sent'][i])
                avg_a_bytes_sent.append(dict[comb][client]['audio']['bytes_sent'][i])
            avs = statistics.mean(avg_v_bytes_sent)
            aas = statistics.mean(avg_a_bytes_sent)
            std_devs[comb][client]['video']['bytes_sent'].append(statistics.stdev(avg_v_bytes_sent))
            std_devs[comb][client]['audio']['bytes_sent'].append(statistics.stdev(avg_a_bytes_sent))
            tests[comb][client]['video']['bytes_sent'].append(avs)
            tests[comb][client]['audio']['bytes_sent'].append(aas)
            i+=1

    # average bytes received
    for comb in tests:
        i = 0           
        while (i < len(results[0]['ch-ch'][client]['video']['bytes_received'])): # video and audio have same length
            avg_v_bytes_received = []
            avg_a_bytes_received = []
            for dict in results:
                avg_v_bytes_received.append(dict[comb][client]['video']['bytes_received'][i])
                avg_a_bytes_received.append(dict[comb][client]['audio']['bytes_received'][i])
            avs = statistics.mean(avg_v_bytes_received)
            aas = statistics.mean(avg_a_bytes_received)
            std_devs[comb][client]['video']['bytes_received'].append(statistics.stdev(avg_v_bytes_received))
            std_devs[comb][client]['audio']['bytes_received'].append(statistics.stdev(avg_a_bytes_received))
            tests[comb][client]['video']['bytes_received'].append(avs)
            tests[comb][client]['audio']['bytes_received'].append(aas)
            i+=1
            
    for comb in tests:
        i = 0          
        while (i < len(results[0]['ch-ch'][client]['video']['frames_encoded'])):
            avg_frames_enc = []
            avg_frames_dec = []
            for dict in results:
                avg_frames_enc.append(dict[comb][client]['video']['frames_encoded'][i])
                avg_frames_dec.append(dict[comb][client]['video']['frames_decoded'][i])
            afe = statistics.mean(avg_frames_enc)
            afd = statistics.mean(avg_frames_dec)

            std_devs[comb][client]['video']['frames_encoded'].append(statistics.stdev(avg_frames_enc))
            std_devs[comb][client]['video']['frames_decoded'].append(statistics.stdev(avg_frames_dec))
            tests[comb][client]['video']['frames_encoded'].append(afe)
            tests[comb][client]['video']['frames_decoded'].append(afd)
            i+=1
 
        avg_fps = []
        for res in results:
            avg_fps.append(int(res[comb][client]['video']['fps']))
        afps = statistics.mean(avg_fps) 
        tests[comb][client]['video']['fps'] = afps
        std_devs[comb][client]['video']['fps'] = statistics.stdev(avg_fps)


if __name__ == "__main__":

    os.makedirs(f"{PLOTSDIR}/", exist_ok=True)
    results = []
    chrome_combs = ['ch-ch', 'ch-fi', 'ch-op']
    firefox_combs = ['fi-fi', 'fi-ch', 'fi-op']
    opera_combs = ['op-op', 'op-ch', 'op-fi']
    
    resultdir = glob.glob(f"{RESULTSDIR}/run_*")
    for rundir in resultdir:
        print(f"Checking {rundir}")
        os.chdir(f"{rundir}")
        init_dict()
        get_results()
        results.append(tests.copy())
        tests.clear()
        os.chdir("../..")

    # Reinit dict for avg results
    init_dict()
    
    # Reset tests to get averages and then plot it
    tests.clear()
    init_dict()
    init_stdev_dict()
    avg_dicts('client1', results)
    avg_dicts('client2', results)

    timestamp_min = []
    for comb in tests:
        timestamp_min.append(tests[comb]['client1']['timestamp'][len(tests[comb]['client1']['timestamp'])-1])
    plot_x_limit = min(timestamp_min)
    # Plotting all results
    # plot_rtt()
    plot_fps(chrome_combs)
    plot_fps(firefox_combs)
    plot_fps(opera_combs)
    plot_ps('video', 'packets_received', chrome_combs)
    plot_ps('video', 'packets_received', firefox_combs)
    plot_ps('video', 'packets_received', opera_combs)

    plot_ps('video', 'bytes_sent', chrome_combs)
    plot_ps('video', 'bytes_sent', firefox_combs)
    plot_ps('video', 'bytes_sent', opera_combs)
    plot_ps('video', 'bytes_received', chrome_combs)
    plot_ps('video', 'bytes_received', firefox_combs)
    plot_ps('video', 'bytes_received', opera_combs)
    # plot_packets('video', 'packets_lost') #! don't use, don't record value anymore in averaging
    plot_ps('audio', 'packets_received', chrome_combs) 
    plot_ps('audio', 'packets_received', firefox_combs) 
    plot_ps('audio', 'packets_received', opera_combs) 
    # plot_packets('audio', 'packets_lost') #! don't use, don't record value anymore in averaging
    # plot_jitter('audio', chrome_combs)
    # plot_jitter('audio', firefox_combs)
    # plot_jitter('audio', opera_combs)
    # plot_jitter('video', chrome_combs)
    # plot_jitter('video', firefox_combs)
    # plot_jitter('video', opera_combs)
    plot_frames('frames_encoded', chrome_combs)
    plot_frames('frames_encoded', firefox_combs)
    plot_frames('frames_encoded', opera_combs)
    plot_frames('frames_decoded', chrome_combs)
    plot_frames('frames_decoded', firefox_combs)
    plot_frames('frames_decoded', opera_combs)
    plot_total_packets_received('audio', chrome_combs)
    plot_total_packets_received('audio', firefox_combs)
    plot_total_packets_received('audio', opera_combs)
    plot_total_packets_received('video', chrome_combs)
    plot_total_packets_received('video', firefox_combs)
    plot_total_packets_received('video', opera_combs)
    plot_total_bytes('audio', 'sent', chrome_combs)
    plot_total_bytes('audio', 'sent', firefox_combs)

    # Plot the received audio bytes for firefox
    plot_total_audio_bytes('client2', 'received', firefox_combs)

    plot_total_bytes('audio', 'sent', opera_combs)
    plot_total_bytes('audio', 'received', chrome_combs)
    plot_total_bytes('audio', 'received', firefox_combs)
    plot_total_bytes('audio', 'received', opera_combs)
    plot_total_bytes('video', 'sent', chrome_combs)
    plot_total_bytes('video', 'sent', firefox_combs)
    plot_total_bytes('video', 'sent', opera_combs)
    plot_total_bytes('video', 'received', chrome_combs)
    plot_total_bytes('video', 'received', firefox_combs)
    plot_total_bytes('video', 'received', opera_combs)