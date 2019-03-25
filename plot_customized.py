import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calculate_customized

dname = calculate_customized.dname
dname_r = calculate_customized.dname_r
sname = calculate_customized.sname
metric_group = ['PSNR','SSIM','VMAF','PSNRHVS','VIFP','PSNRHVSM']
psnr_group =[]
vmaf_group =[]
ssim_group =[]
psnrhvs_group =[]
vifp_group = []
psnrhvsm_group =[]
metric_result_group =[psnr_group,ssim_group,vmaf_group,psnrhvs_group,vifp_group,psnrhvsm_group]
s_score_group =[]
markers = ['o','v','^','<','>','d','s','p','h','D']
colors = ['r','g','b','y','c','m','k','orange','pink','purple']

def plot(mindex,metric):
    df = pd.read_csv(metric+'_customized.csv')
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
        names = locals()
        for i in range(len(dname_r)):
            names['y_'+dname_r[i]+'_set'] = []
        p_number_list = [0]
        p_number = 0
        total_number = 0
        for i in range(len(dname)):
            for ii in range(len(dname[i])):
                names['y_'+dname_r[i]+'_set'].append(sample_metric.iloc[0, ii + p_number])
                total_number += 1
            p_number += len(dname[i])
            p_number_list.append(p_number)
        y_set = []
        for i in range(len(dname)):
            y_set += names['y_'+dname_r[i]+'_set']
        for i in y_set:
            y_set[y_set.index(i)] = float(i)
        x_set = []
        for i in range(total_number):
            x_set.append(s_score_group[index].iloc[0, i])
        plt.xlabel("DMOS")
        plt.ylabel(metric)
        marker = markers[index]
        P_list = []
        for i in range(len(dname)):
            names['P%i'%i] = plt.scatter(x_set[p_number_list[i]:p_number_list[i+1]], y_set[p_number_list[i]:p_number_list[i+1]], s = 13, c=colors[i], marker=marker)
            P_list.append(names['P%i'%i])
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
            if xy_couple_group[item][0] > xy_couple_group[item_1][0] and xy_couple_group[item][1] > xy_couple_group[item_1][1]:
                C += 1
            elif xy_couple_group[item][0] < xy_couple_group[item_1][0] and xy_couple_group[item][1] < xy_couple_group[item_1][1]:
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
    plt.legend(P_list, dname_r, loc='lower right', scatterpoints=1)
    plt.text(p_text[0], p_text[1], 'PCC:' + PCC + '\n' + 'SRCC:' + SRCC + '\n' + 'KRCC:' + KRCC, fontdict={'size': 13, 'color': 'r'})
    plt.savefig('./'+metric+'_customized_.png')
    plt.show()

def import_dmos(sfile):
    df_score = pd.read_csv(sfile+'.csv')
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
    total_number = 0
    for i in range(len(dname)):
        for ii in range(len(dname[i])):
            total_number += 1
    for df_sample_score in s_score_group:
        for i in range(total_number):
            df_sample_score.iloc[0, i] = (1 - df_sample_score.iloc[0, i] / 5) * 100

def plotting():
    for mindex in range(len(metric_group)):
        plot(mindex,metric_group[mindex])

if __name__ == '__main__':
    while(1):
        try:
            sfile = input('Please input the file name of the subjective score: ')
            s = open(sfile+'.csv','r')
            break
        except:
            print('No such files, please input again')
    s.close()
    calculate_customized.calculation_1(sfile)
    import_dmos(sfile)
    plotting()
