import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calculate_light

dirac = ['_dirac_1', '_dirac_2', '_dirac_3']
h264 = ['_h264_1', '_h264_2', '_h264_3', '_h264_4']
ip = ['_ip_1', '_ip_2', '_ip_3','_ip_4']
mpeg2 = ['_mpeg2_1', '_mpeg2_2', '_mpeg2_3']
dname = [dirac, h264, mpeg2, ip]
dname_r = ['dirac', 'h264', 'mpeg2','ip']
sname = ['laser']
metric_group = ['PSNR','SSIM','VMAF','PSNRHVS','VIFP','PSNRHVSM']
psnr_group =[]
vmaf_group =[]
ssim_group =[]
psnrhvs_group =[]
vifp_group = []
psnrhvsm_group =[]
metric_result_group =[psnr_group,ssim_group,vmaf_group,psnrhvs_group,vifp_group,psnrhvsm_group]
s_score_group =[]
markers = ['o','v','^','<','>','d','s','p','h']

def plot(mindex,metric):
    df = pd.read_csv(metric+'_light.csv')
    sample_list = df.loc[:, 'Name']
    for sample_name in sname:
        df_sample = pd.DataFrame()
        count = 0
        count_1 = 0
        for samples in sample_list:
            if samples.find(sample_name) != -1:
                df_sample.insert(count, samples, [df.loc[count_1, metric], ])
                count += 1
            count_1 += 1
        metric_result_group[mindex].append(df_sample)
    # plot starts
    plt.xlim((-20, 120))
    if metric == 'PSNR':
        y_axi = (24, 42)
        y_linespace = [24, 42, 9]
    elif metric == 'SSIM':
        y_axi = (0.75,1.05)
        y_linespace = [0.75, 1.05, 9]
    elif metric == 'VMAF':
        y_axi = (30,110)
        y_linespace = [30, 110, 9]
    elif metric == 'PSNRHVS':
        y_axi = (24, 42)
        y_linespace = [24, 42, 9]
    elif metric == 'VIFP':
        y_axi = (0.3,0.9)
        y_linespace = [0.3, 0.9, 9]
    elif metric == 'PSNRHVSM':
        y_axi = (24, 42)
        y_linespace = [24, 42, 9]
    plt.ylim(y_axi)
    x_ax = np.linspace(-20, 120, 8)
    y_ax = np.linspace(y_linespace[0], y_linespace[1], y_linespace[2])
    plt.xticks(x_ax)
    plt.yticks(y_ax)
    x_set_total = []
    y_set_total = []
    index = 0
    for sample_metric in metric_result_group[mindex]:
        y_dirac_set = []
        y_h264_set = []
        y_mpeg2_set = []
        y_ip_set = []
        for i in range(4):
            y_ip_set.append(sample_metric.iloc[0, i + 10])
            y_h264_set.append(sample_metric.iloc[0, i + 3])
        for i in range(3):
            y_dirac_set.append(sample_metric.iloc[0, i])
            y_mpeg2_set.append(sample_metric.iloc[0, i + 7])
        y_set = y_dirac_set + y_h264_set + y_mpeg2_set + y_ip_set
        for i in y_set:
            y_set[y_set.index(i)] = float(i)
        x_set = []
        for i in range(14):
            x_set.append(s_score_group[index].iloc[0, i])
        plt.xlabel("DMOS")
        plt.ylabel(metric)
        marker = markers[index]
        P1 = plt.scatter(x_set[0:3], y_set[0:3], s = 13, c='r', marker=marker)
        P2 = plt.scatter(x_set[3:7], y_set[3:7], s = 13, c='g', marker=marker)
        P3 = plt.scatter(x_set[7:10], y_set[7:10], s = 13, c='b', marker=marker)
        P4 = plt.scatter(x_set[10:14], y_set[10:14], s = 13, c='orange', marker=marker)
        x_set_total += x_set
        y_set_total += y_set
        index += 1
    plt.title(metric)
    plt.grid(ls='--')
    np_x = np.array(x_set_total)
    np_y = np.array(y_set_total)
    std_x = np_x.std(ddof=1)
    std_y = np_y.std(ddof=1)
    cov_xy_m = np.cov(np_x, np_y)
    cov_xy = cov_xy_m[0, 1]
    PCC = cov_xy / (std_x * std_y)
    PCC = str(PCC)
    np_x_sorted = np.sort(np_x, axis=None)
    np_y_sorted = np.sort(np_y, axis=None)
    np_x_order = []
    np_y_order = []
    for x in np_x:
        for i in range(np_x_sorted.shape[0]):
            if (np_x_sorted[i] == x).all():
                np_x_order.append(i + 1)
                break
    for y in np_y:
        for i in range(np_y_sorted.shape[0]):
            if (np_y_sorted[i] == y).all():
                np_y_order.append(i + 1)
                break
    d_order = [np_y_order[i] - np_x_order[i] for i in range(len(np_y_order))]
    d_order_square = [d_order[i] * d_order[i] for i in range(len(d_order))]
    d_order_square_sum = 0
    for item in d_order_square:
        d_order_square_sum += item
    SRCC = 1 - 6 * d_order_square_sum / ((len(d_order)) ** 3 - len(d_order))
    SRCC = str(SRCC)
    xy_couple = []
    xy_couple_group = []
    C = 0
    D = 0
    for item in range(len(np_x_order)):
        xy_couple.append(np_x_order[item])
        xy_couple.append(np_y_order[item])
        xy_couple_group.append(xy_couple)
        xy_couple = []
    for item in range(len(xy_couple_group)):
        for item_1 in range(item + 1, len(xy_couple_group)):
            if xy_couple_group[item][0] > xy_couple_group[item_1][0] and xy_couple_group[item][1] > \
                    xy_couple_group[item_1][1]:
                C += 1
            elif xy_couple_group[item][0] < xy_couple_group[item_1][0] and xy_couple_group[item][1] < \
                    xy_couple_group[item_1][1]:
                C += 1
            else:
                D += 1
    KRCC = (C - D) / (0.5 * len(np_x_order) * (len(np_x_order) - 1))
    KRCC = str(KRCC)
    if metric == 'PSNR':
        p_text = [0, 39]
    elif metric == 'SSIM':
        p_text = [0, 1]
    elif metric == 'VMAF':
        p_text = [0, 97]
    elif metric == 'PSNRHVS':
        p_text = [0, 39]
    elif metric == 'VIFP':
        p_text = [0, 0.800]
    elif metric == 'PSNRHVSM':
        p_text = [0, 39]
    plt.legend([P1, P2, P3, P4], ['Dirac', 'h264', 'mpeg2', 'packet loss'], loc='lower right', scatterpoints=1)
    plt.text(p_text[0], p_text[1], 'PCC:' + PCC + '\n' + 'SRCC:' + SRCC + '\n' + 'KRCC:' + KRCC, fontdict={'size': 13, 'color': 'r'})
    plt.savefig('./'+metric+'_light_.png')
    plt.show()

def import_dmos():
    df_score = pd.read_csv('subjective_score_all.csv')
    sample_list = df_score.loc[:, 'Name']
    for sample_name in sname:
        df_sample_score = pd.DataFrame()
        count = 0
        count_1 = 0
        for samples in sample_list:
            if samples.find(sample_name) != -1:
                df_sample_score.insert(count, samples, [df_score.loc[count_1, 'DMOS'], ])
                count += 1
            count_1 += 1
        s_score_group.append(df_sample_score)
    for df_sample_score in s_score_group:
        for i in range(14):
            df_sample_score.iloc[0, i] = (1 - df_sample_score.iloc[0, i] / 5) * 100

def plotting():
    for mindex in range(len(metric_group)):
        plot(mindex,metric_group[mindex])

if __name__ == '__main__':
    calculate_light.calculation()
    import_dmos()
    plotting()
