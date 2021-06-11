import json
import glob
import re
import os
import matplotlib.pyplot as plt
import numpy as np
import statistics

tests = dict(dict(dict()))
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
            tests[comb]['client1']['video']['packets_sent'] = []
            tests[comb]['client2']['video']['packets_sent'] = []
            tests[comb]['client1']['video']['packets_lost'] = []
            tests[comb]['client2']['video']['packets_lost'] = []
            tests[comb]['client1']['audio']['packets_sent'] = []
            tests[comb]['client2']['audio']['packets_sent'] = []
            tests[comb]['client1']['audio']['packets_lost'] = []
            tests[comb]['client2']['audio']['packets_lost'] = []
            tests[comb]['client1']['video']['frames_encoded'] = []
            tests[comb]['client1']['video']['frames_decoded'] = []
            tests[comb]['client2']['video']['frames_encoded'] = []
            tests[comb]['client2']['video']['frames_decoded'] = []
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
            std_devs[comb]['client1']['video']['packets_sent'] = []
            std_devs[comb]['client2']['video']['packets_sent'] = []
            std_devs[comb]['client1']['video']['packets_lost'] = []
            std_devs[comb]['client2']['video']['packets_lost'] = []
            std_devs[comb]['client1']['audio']['packets_sent'] = []
            std_devs[comb]['client2']['audio']['packets_sent'] = []
            std_devs[comb]['client1']['audio']['packets_lost'] = []
            std_devs[comb]['client2']['audio']['packets_lost'] = []
            std_devs[comb]['client1']['video']['frames_encoded'] = []
            std_devs[comb]['client1']['video']['frames_decoded'] = []
            std_devs[comb]['client2']['video']['frames_encoded'] = []
            std_devs[comb]['client2']['video']['frames_decoded'] = []
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
    audio_packets_sent = audio_packets_lost = video_packets_sent = video_packets_lost = 0
    count_inbound = count_outbound = 0

    with open(tests[browsercomb][client]['stats-raw']) as results_file:
            data = json.load(results_file)
            timestamps = []
            audio_packets_sent = []
            video_packets_sent = []
            frames_encoded = []
            frames_decoded = []

            for stats in data['StatsArray']:
                cnt = 0
                for (key, value) in stats['outbound-rtp'].items():
                    # first value is always for audio
                    if cnt%2 == 0: # timeselapsed
                        audio_packets_sent.append(int(value['packetsSent']))
                    # second value is always for video
                    else:
                        video_packets_sent.append(int(value['packetsSent']))
                        frames_encoded.append(int(value['framesEncoded']))
                    cnt+=1
                cnt = 0
                for (key, value) in stats['inbound-rtp'].items():
                    if cnt%2 == 0:
                        tests[browsercomb][client]['audio']['packets_lost'].append(float(value['packetsLost']))
                        tests[browsercomb][client]['audio']['jitter'].append(float(value['jitter']))
                    else:
                        tests[browsercomb][client]['video']['packets_lost'].append(float(value['packetsLost']))
                        tests[browsercomb][client]['video']['jitter'].append(float(value['jitter']))
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
            for i in range (len(video_packets_sent)):
                if i == 0:
                    tests[browsercomb][client]['video']['packets_sent'].append(video_packets_sent[i])
                    tests[browsercomb][client]['audio']['packets_sent'].append(audio_packets_sent[i])
                else:
                    difference_vid = (video_packets_sent[i] - video_packets_sent[i - 1])
                    tests[browsercomb][client]['video']['packets_sent'].append(difference_vid)

                    difference_audio = (audio_packets_sent[i] - audio_packets_sent[i - 1])
                    tests[browsercomb][client]['audio']['packets_sent'].append(difference_audio)
            
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
    client1_errors = []
    client2_values = []
    client2_errors = []
    names = []
    width = 0.32

    for comb in tests:
        names.append(comb)
        client1_values.append(int(tests[comb]['client1']['video']['fps']))
        client1_errors.append(int(std_devs[comb]['client1']['video']['fps']))
        client2_values.append(int(tests[comb]['client2']['video']['fps']))
        client2_errors.append(int(std_devs[comb]['client2']['video']['fps']))

    ind = np.arange(len(names))
    c1 = plt.bar(ind+width*1/2, client1_values, width, yerr=client1_errors, align='center', capsize=5, label='client-1', color = 'dimgray')
    c2 = plt.bar(ind+width*3/2, client2_values, width, yerr = client2_errors, align='center', capsize=5, label='client-2',  color = 'blue')
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
    for comb in tests:
        plt.errorbar(np.array(tests[comb]['client1']['timestamp']), np.array(tests[comb]['client1'][type1][type2]), yerr=std_devs[comb]['client1'][type1][type2], capsize=5)

    plt.xlabel('time(s)')

    # plt.xticks(np.arange(0, plot_x_limit, step=1))
    plt.legend()
    plt.xlim([-0.1, plot_x_limit]) #

    if (type1 == 'audio'):
        if (type2 == 'packets_sent'):
            plt.title('Audio Packets Sent Per Second')
            plt.savefig('plots/audio-packets-sent-ps.png', dpi=200)
        # else:
        #     plt.title('Audio Packets Lost')
        #     plt.savefig('plots/audio-packets-lost.png', dpi=200)
    else:
        if (type2 == 'packets_sent'):
            plt.title('Video Packets Sent Per Second')
            plt.savefig('plots/video-packets-sent-ps.png', dpi=200)
        # else:
        #     plt.title('Video Packets Lost')
        #     plt.savefig('plots/video-packets-lost.png', dpi=200)
    plt.clf()


def plot_total_packets_sent(type):
    client1_values = []
    client2_values = []
    client1_errors = []
    names = []
    width = 0.32

    for comb in tests:
        names.append(comb)
        client1_values.append(sum(tests[comb]['client1'][type]['packets_sent']))
        client1_errors.append(statistics.mean(std_devs[comb]['client1'][type]['packets_sent']))
    
    ind = np.arange(len(names))
    c1 = plt.bar(ind+width, client1_values, width, yerr=client1_errors, capsize=5, align='center', color = 'blue')
    plt.xlabel('browser combinations')
    plt.xticks(ticks=ind+width, labels=names)
    plt.ylim(bottom=0)
    autolabel(c1)
    # plt.ylim(top=)
    
    if (type == 'audio'):
        plt.title('Total audio packets sent')
        plt.savefig('plots/total-audio-packets-sent.png', dpi=200)
    if (type == 'video'):
        plt.title('Total video packets sent')
        plt.savefig('plots/total-video-packets-sent.png', dpi=200)

    plt.clf()

def plot_jitter(type):
    client1_values = []
    client2_values = []

    names = []
    width = 0.32

    for comb in tests:
        plt.plot(np.array(tests[comb]['client1']['timestamp']), np.array(tests[comb]['client1'][type]['jitter']), label=comb)
    for comb in tests:
        plt.errorbar(np.array(tests[comb]['client1']['timestamp']), np.array(tests[comb]['client1'][type]['jitter']), std_devs[comb]['client1'][type]['jitter'], capsize=5)

    plt.xlabel('time(s)')
    plt.ylabel('Average jitter (ms)')
    plt.legend()
    plt.xlim([-0.1, plot_x_limit])

    if type == 'audio':
        plt.title('Audio Jitter per Second')
        plt.savefig('plots/audio-jitter.png', dpi=200)
    else:
        plt.title('Video Jitter per Second')
        plt.savefig('plots/video-jitter.png', dpi=200)
    plt.clf()


def plot_frames(type):
    client1_values = []
    client2_values = []

    names = []
    width = 0.32

    for comb in tests:
        plt.plot(np.array(tests[comb]['client1']['timestamp']), np.array(tests[comb]['client1']['video'][type]), label=comb)
    for comb in tests:
        plt.errorbar(np.array(tests[comb]['client1']['timestamp']), np.array(tests[comb]['client1']['video'][type]), yerr=std_devs[comb]['client1']['video'][type], capsize=5)

    plt.xlabel('time(s)')
    plt.ylabel('Frames per sec')
    plt.legend(ncol=2) # ncol=2 for multi column
    plt.xlim([-0.1, plot_x_limit])

    if (type == 'frames_encoded'):
        plt.title("Frames Encoded per Second")
        plt.savefig('plots/frames-encoded.png', dpi=200)
    else:
        plt.title("Frames Decoded per Second")
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
        plt.text(c.get_x()+c.get_width()/2., h, '%d'%int(h),
                ha='center', va='bottom')

def avg_dicts(results):

    # average timestamps
    for comb in tests:
        i = 0
        while (i < len(results[0]['ch-ch']['client1']['timestamp'])):
            avg_timestamps = []
            for dict in results:
                avg_timestamps.append(dict[comb]['client1']['timestamp'][i])
            avt = statistics.mean(avg_timestamps)
            std_devs[comb]['client1']['timestamp'].append(statistics.stdev(avg_timestamps))
            tests[comb]['client1']['timestamp'].append(avt)
            i+=1


    for comb in tests:
        i = 0           
        while (i < len(results[0]['ch-ch']['client1']['video']['jitter'])):
            avg_video_jitter = []
            avg_audio_jitter = []
            for dict in results:
                avg_video_jitter.append(dict[comb]['client1']['video']['jitter'][i])
                avg_audio_jitter.append(dict[comb]['client1']['audio']['jitter'][i])
            avj = statistics.mean(avg_video_jitter)
            aaj = statistics.mean(avg_audio_jitter)

            std_devs[comb]['client1']['video']['jitter'].append(statistics.stdev(avg_video_jitter))
            std_devs[comb]['client1']['audio']['jitter'].append(statistics.stdev(avg_audio_jitter))
            tests[comb]['client1']['video']['jitter'].append(avj)
            tests[comb]['client1']['audio']['jitter'].append(aaj)
            i+=1


    # average packets sent
    for comb in tests:
        i = 0           
        while (i < len(results[0]['ch-ch']['client1']['video']['packets_sent'])): # video and audio have same length
            avg_v_packets_sent = []
            avg_a_packets_sent = []
            for dict in results:
                avg_v_packets_sent.append(dict[comb]['client1']['video']['packets_sent'][i])
                avg_a_packets_sent.append(dict[comb]['client1']['audio']['packets_sent'][i])
            avs = statistics.mean(avg_v_packets_sent)
            aas = statistics.mean(avg_a_packets_sent)
            std_devs[comb]['client1']['video']['packets_sent'].append(statistics.stdev(avg_v_packets_sent))
            std_devs[comb]['client1']['audio']['packets_sent'].append(statistics.stdev(avg_a_packets_sent))
            tests[comb]['client1']['video']['packets_sent'].append(avs)
            tests[comb]['client1']['audio']['packets_sent'].append(aas)
            i+=1

    for comb in tests:
        i = 0          
        while (i < len(results[0]['ch-ch']['client1']['video']['frames_encoded'])):
            avg_frames_enc = []
            avg_frames_dec = []
            for dict in results:
                avg_frames_enc.append(dict[comb]['client1']['video']['frames_encoded'][i])
                avg_frames_dec.append(dict[comb]['client1']['video']['frames_decoded'][i])
            afe = statistics.mean(avg_frames_enc)
            afd = statistics.mean(avg_frames_dec)

            std_devs[comb]['client1']['video']['frames_encoded'].append(statistics.stdev(avg_frames_enc))
            std_devs[comb]['client1']['video']['frames_decoded'].append(statistics.stdev(avg_frames_dec))
            tests[comb]['client1']['video']['frames_encoded'].append(afe)
            tests[comb]['client1']['video']['frames_decoded'].append(afd)
            i+=1
 
        avg_fps_c1 = []
        avg_fps_c2 = []
        for res in results:
            avg_fps_c1.append(int(res[comb]['client1']['video']['fps']))
            avg_fps_c2.append(int(res[comb]['client2']['video']['fps']))
        afps1 = statistics.mean(avg_fps_c1) 
        afps2 = statistics.mean(avg_fps_c2)
        tests[comb]['client1']['video']['fps'] = afps1
        tests[comb]['client2']['video']['fps'] = afps2
        std_devs[comb]['client1']['video']['fps'] = statistics.stdev(avg_fps_c1)
        std_devs[comb]['client2']['video']['fps'] = statistics.stdev(avg_fps_c2)


if __name__ == "__main__":
    os.makedirs('plots/', exist_ok=True)
    results = []
    
    resultdir = glob.glob("results/*")
    for rundir in resultdir:
        print(f"Checking {rundir}")
        os.chdir(f"{rundir}")
        init_dict()
        get_results()
        results.append(tests.copy())
        tests.clear()
        os.chdir("../..")

    # Reinit dict for avf results
    init_dict()
    
    # Reset tests to get averages and then plot it
    tests.clear()
    init_dict()
    init_stdev_dict()
    avg_dicts(results)

    timestamp_min = []
    for comb in tests:
        timestamp_min.append(tests[comb]['client1']['timestamp'][len(tests[comb]['client1']['timestamp'])-1])
    plot_x_limit = min(timestamp_min)
    # Plotting all results
    # plot_rtt()
    plot_fps()
    plot_packets('video', 'packets_sent')
    # plot_packets('video', 'packets_lost') #! don't use, don't record value anymore in averaging
    plot_packets('audio', 'packets_sent') 
    # plot_packets('audio', 'packets_lost') #! don't use, don't record value anymore in averaging
    plot_jitter('audio')
    plot_jitter('video')
    plot_frames('frames_encoded')
    plot_frames('frames_decoded')
    plot_total_packets_sent('audio')
    plot_total_packets_sent('video')