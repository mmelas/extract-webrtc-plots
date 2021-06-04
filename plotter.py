import json
import glob
import re
import os
import matplotlib.pyplot as plt
import numpy as np

browsers_files = {'ch-ch' : [], 'ch-fi' : [], 'ch-op' :[],
                  'fi-fi' : [], 'fi-op' : [], 'op-op' :[]}

data_dict = {
    'client1': {
        'stats-raw': None,
        'stats-summary': None,
        'browser': None,
        'rtt': 0,
        'timestamp':  0,
        'audio': {
            'packets_sent': 0,
            'packets_lost': 0,
            'jitter': 0
        },
        'video': {
            'packets_sent': 0,
            'packets_lost': 0,
            'jitter': 0,
            'frames-encoded': 0,
            'frames-decoded': 0,
            'fps': 0
        },
    },
    'client2': {
        'stats-raw': None,
        'stats-summary': None,
        'browser': None,
        'rtt': 0,
        'timestamp':  0,
        'audio': {
            'packets_sent': 0,
            'packets_lost': 0,
            'jitter': 0
        },
        'video': {
            'packets_sent': 0,
            'packets_lost': 0,
            'jitter': 0,
            'frames-encoded': 0,
            'frames-decoded': 0,
            'fps': 0
        },
    }
}
tests = dict(dict(dict()))
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
    tests[comb]['client1']['video']['packets_sent'] = []
    tests[comb]['client2']['video']['packets_sent'] = []
    tests[comb]['client1']['video']['packets_lost'] = []
    tests[comb]['client2']['video']['packets_lost'] = []
    tests[comb]['client1']['audio']['packets_sent'] = []
    tests[comb]['client2']['audio']['packets_sent'] = []
    tests[comb]['client1']['audio']['packets_lost'] = []
    tests[comb]['client2']['audio']['packets_lost'] = []
    tests[comb]['client1']['video']['framesEncoded'] = []
    tests[comb]['client1']['video']['framesDecoded'] = []
    tests[comb]['client2']['video']['framesEncoded'] = []
    tests[comb]['client2']['video']['framesDecoded'] = []
    tests[comb]['client1']['timestamp'] = []
    tests[comb]['client2']['timestamp'] = []
    tests[comb]['client1']['audio']['jitter'] = []
    tests[comb]['client1']['video']['jitter'] = []
    tests[comb]['client2']['audio']['jitter'] = []
    tests[comb]['client2']['video']['jitter'] = []


def load_data(file):
    with open(file) as results_file:
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
    audio_packets_sent = audio_packets_lost = video_packets_sent = video_packets_lost = 0
    count_inbound = count_outbound = 0

    with open(tests[browsercomb][client]['stats-raw']) as results_file:
            data = json.load(results_file)
            timestamps = []

            for stats in data['StatsArray']:
                cnt = 0
                for (key, value) in stats['outbound-rtp'].items():
                    # first value is always for audio
                    if cnt%2 == 0: # timeselapsed
                        tests[browsercomb][client]['audio']['packets_sent'].append(int(value['packetsSent']))
                    # second value is always for video
                    else:
                        tests[browsercomb][client]['video']['packets_sent'].append(int(value['packetsSent']))
                        tests[browsercomb][client]['video']['framesEncoded'].append(int(value['framesEncoded']))
                    cnt+=1
                cnt = 0
                for (key, value) in stats['inbound-rtp'].items():
                    if cnt%2 == 0:
                        tests[browsercomb][client]['audio']['packets_lost'].append(float(value['packetsLost']))
                        tests[browsercomb][client]['audio']['jitter'].append(float(value['jitter']))
                    else:
                        tests[browsercomb][client]['video']['packets_lost'].append(float(value['packetsLost']))
                        tests[browsercomb][client]['video']['jitter'].append(float(value['jitter']))
                        tests[browsercomb][client]['video']['framesDecoded'].append(int(value['framesDecoded']))
                        timestamps.append(float(value['timestamp']))
                    cnt+=1
            for i in range (len(timestamps)):
                if i == 0:
                    tests[browsercomb][client]['timestamp'].append(0.0)
                else:
                    difference = (timestamps[i] - timestamps[i - 1]) / 1000
                    timestamp = tests[browsercomb][client]['timestamp'][i - 1] + difference
                    tests[browsercomb][client]['timestamp'].append(timestamp)



    # with open(tests[browsercomb][client]['stats-raw']) as results_file:
    #     data = json.load(results_file)

    #     for stats in data['StatsArray']:
    #         cnt = 0
    #         for (key, value) in stats['outbound-rtp'].items():
    #             # first value is always for audio
    #             if cnt%2 == 0:
    #                 audio_packets_sent += int(value['packetsSent'])
    #             # second value is always for video
    #             else:
    #                 video_packets_sent += int(value['packetsSent'])
    #             count_outbound += 1
    #             cnt+=1
    #         cnt = 0
    #         for (key, value) in stats['inbound-rtp'].items():
    #             if cnt%2 == 0:
    #                 audio_packets_lost += int(value['packetsLost'])
    #             else:
    #                 print(int(value['packetsLost']) )
    #                 video_packets_lost += int(value['packetsLost'])
    #             count_inbound += 1
    #             cnt+=1

    #     tests[browsercomb][client]['video']['packets_sent'] = video_packets_sent/count_outbound
    #     tests[browsercomb][client]['video']['packets_lost'] = video_packets_lost/count_inbound
    #     tests[browsercomb][client]['audio']['packets_sent'] = audio_packets_sent/count_outbound
    #     tests[browsercomb][client]['audio']['packets_lost'] = audio_packets_lost/count_inbound

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
    plt.xlabel('browser combinations')
    plt.legend()
    plt.savefig('plots/rtt.png', dpi=200)
    plt.clf()


def plot_fps():
    client1_values = []
    client2_values = []
    names = []
    width = 0.32

    for comb in tests:
        names.append(comb)
        client1_values.append(int(tests[comb]['client1']['video']['fps']))
        client2_values.append(int(tests[comb]['client2']['video']['fps']))

    ind = np.arange(len(names))
    c1 = plt.bar(ind+width*1/2, client1_values, width,  label='client-1', color = 'dimgray')
    c2 = plt.bar(ind+width*3/2, client2_values, width, label='client-2',  color = 'blue')
    plt.xlabel('browser combinations')
    plt.xticks(ticks=ind+width, labels=names)
    plt.legend()
    plt.ylim(bottom=0)
    plt.ylim(top=40)
    plt.title('Average FPS Incoming')

    autolabel(c1)
    autolabel(c2)
    plt.savefig('plots/fps.png', dpi=200)
    plt.clf()


def plot_packets(type1, type2):
    client1_values = []
    client2_values = []

    names = []
    width = 0.32

    for comb in tests:
        plt.plot(np.array(tests[comb]['client1']['timestamp']), np.array(tests[comb]['client1'][type1][type2]), label=comb)
    plt.xlabel('time(s)')
    plt.legend()

    if (type1 == 'audio'):
        if (type2 == 'packets_sent'):
            plt.title('Audio Packets Sent')
            plt.savefig('plots/audio-packets-sent.png', dpi=200)
        else:
            plt.title('Audio Packets Lost')
            plt.savefig('plots/audio-packets-lost.png', dpi=200)
    else:
        if (type2 == 'packets_sent'):
            plt.title('Video Packets Sent')
            plt.savefig('plots/video-packets-sent.png', dpi=200)
        else:
            plt.title('Video Packets Lost')
            plt.savefig('plots/video-packets-lost.png', dpi=200)
    plt.clf()

def plot_jitter(type):
    client1_values = []
    client2_values = []

    names = []
    width = 0.32

    for comb in tests:
        plt.plot(np.array(tests[comb]['client1']['timestamp']), np.array(tests[comb]['client1'][type]['jitter']), label=comb)
    plt.xlabel('time(s)')
    plt.ylabel('Average jitter (ms)')
    plt.legend()

    if type == 'audio':
        plt.title('Audio Jitter')
        plt.savefig('plots/audio-jitter.png', dpi=200)
    else:
        plt.title('Video Jitter')
        plt.savefig('plots/video-jitter.png', dpi=200)
    plt.clf()


def plot_frames(type):
    client1_values = []
    client2_values = []

    names = []
    width = 0.32

    for comb in tests:
        plt.plot(np.array(tests[comb]['client1']['timestamp']), np.array(tests[comb]['client1']['video'][type]), label=comb)
    plt.xlabel('time(s)')
    plt.ylabel('Frames per sec')
    plt.legend()

    if (type == 'framesEncoded'):
        plt.title("Frames Encoded")
        plt.savefig('plots/frames-encoded.png', dpi=200)
    else:
        plt.title("Frames Decoded")
        plt.savefig('plots/frames-decoded.png', dpi=200)

    plt.clf()

#AVERAGE
# def plot_packets(type1, type2):
#     client1_values = []
#     client2_values = []

#     # TODO remove harcoded x axis with real time values

#     names = []
#     width = 0.32
#     fig = plt.figure()
#     ax = fig.add_subplot(111)

    # for comb in tests:
    #     names.append(comb)
        # client1_values.append(int(tests[comb]['client1'][type1][type2]))
        # client2_values.append(int(tests[comb]['client2'][type1][type2]))

#     # TODO get time
#     ind = np.arange(len(names))

#     # c1 = ax.line(ind+width*1/2, client1_values, width,  label='client-1', color = 'dimgray')
#     # c2 = ax.line(ind+width*3/2, client2_values, width, label='client-2',  color = 'blue')
#     ax.set_xlabel('browser combinations')
#     ax.set_xticks(ind+width)
#      ax.set_xticklabels(np.array(tests[comb]['client1']['timestamp']))
#     ax.legend()
#      ax.set_ylim(bottom=0)
#      ax.set_ylim(top=30)


#      autolabel(c1, ax)
#      autolabel(c2, ax)

#     if (type1 == 'audio'):
#         if (type2 == 'packets_sent'):
#             ax.set_title('Audio Packets Sent')
#             plt.figure(1)
#         else:
#             ax.set_title('Audio Packets Lost')
#             plt.figure(2)
#     else:
#         if (type2 == 'packets_sent'):
#             ax.set_title('Video Packets Sent')
#             plt.figure(3)
#         else:
#             ax.set_title('Video Packets Lost')
#             plt.figure(4)



def autolabel(client):
    for c in client:
        h = c.get_height()
        plt.text(c.get_x()+c.get_width()/2., 1.05*h, '%d'%int(h),
                ha='center', va='bottom')


if __name__ == "__main__":
    os.makedirs('plots/', exist_ok=True)
    get_results()

    # Plotting all results
    # plot_rtt()
    plot_fps()
    plot_packets('video', 'packets_sent')
    plot_packets('video', 'packets_lost')
    plot_packets('audio', 'packets_sent')
    plot_packets('audio', 'packets_lost')
    plot_jitter('audio')
    plot_jitter('video')
    plot_frames('framesEncoded')
    plot_frames('framesDecoded')
