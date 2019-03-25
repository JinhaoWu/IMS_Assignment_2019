import subprocess
import sys
import pandas as pd
import os

class percent():
    bar_length = 70
    max = 0
    index = 0

    def __init__(self, max):
        self.max = max
    def display_bar(self):
        if self.index % 1 == 0 or self.index == self.max:
            sys.stdout.write('\r')
            percent =  100 * float(self.index) / float(self.max)
            num_arrow = int(percent / 100 * 70) +1
            num_line = self.bar_length - num_arrow
            bar = '['+'>'* num_arrow + '-'*num_line+']'+'{:.2f}'.format(percent)+'%'
            sys.stdout.write(bar)
            sys.stdout.flush()
        self.index += 1


dname = []
dname_r = []
sname = []

def calculation(sum,sfile):
    #create file name list
    dfile_name_list = []
    file_name_list = []
    for sample_name in sname:
        file_name_list.append(sample_name+'.yuv')
        for d_name in dname:
            for dd_name in d_name:
                dfile_name = sample_name+dd_name+'.yuv'
                dfile_name_list.append(dfile_name)


    #calculate PSNR and create PSNR file
    process_bar = percent(len(dfile_name_list)-1)
    psnr_list =[]
    print('calculating PSNR......\n')
    for dfile_name in dfile_name_list:
        index = dfile_name_list.index(dfile_name)//sum
        ofile_name = file_name_list[index]
        psnr_cmd = './ffmpeg -s 1920x1088 -i '+ dfile_name + ' -s 1920x1088 -i '+ofile_name+' -lavfi psnr="stats_file=psnr.log" -f null -'
        d = subprocess.Popen(psnr_cmd, shell=True,stderr=subprocess.PIPE)
        d.wait()
        sout = d.stderr.readlines()
        psnr_loc = sout[-1].decode('utf-8').find('average:')
        psnr = sout[-1].decode('utf-8')[psnr_loc+8:psnr_loc+17]
        psnr_list.append(psnr)
        process_bar.display_bar()
    psnr_write = ['Name,PSNR']
    for i in range(len(psnr_list)):
        psnr_write.append(dfile_name_list[i]+','+psnr_list[i])
    with open('PSNR_customized.csv','w',newline='') as psnr_csv:
        for row in psnr_write:
            if row != psnr_write[-1]:
                psnr_csv.write(row+'\n')
            else:
                psnr_csv.write(row)


    #calculate VMAF and create VMAF file
    process_bar = percent(len(dfile_name_list)-1)
    vmaf_list =[]
    print('\ncalculating VMAF......\n')
    for dfile_name in dfile_name_list:
        index = dfile_name_list.index(dfile_name)//sum
        ofile_name = file_name_list[index]
        vmaf_cmd = './ffmpeg -s 1920x1088 -i '+ dfile_name + ' -s 1920x1088 -i '+ofile_name+' -lavfi libvmaf="model_path=./model/vmaf_v0.6.1.pkl:psnr=1:log_fmt=json" -f null - -loglevel quiet'
        d = subprocess.Popen(vmaf_cmd, shell=True,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
        d.wait()
        sout = d.stdout.readlines()
        vmaf_loc = sout[-1].decode('utf-8').find('=')
        vmaf = sout[-1].decode('utf-8')[vmaf_loc+2:vmaf_loc+10]
        vmaf_list.append(vmaf)
        process_bar.display_bar()
    vmaf_write = ['Name,VMAF']
    for i in range(len(vmaf_list)):
        vmaf_write.append(dfile_name_list[i]+','+vmaf_list[i])
    with open('VMAF_customized.csv','w',newline='') as vmaf_csv:
        for row in vmaf_write:
            if row != vmaf_write[-1]:
                vmaf_csv.write(row+'\n')
            else:
                vmaf_csv.write(row)


    #calculate SSIM and create ssim file
    process_bar = percent(len(dfile_name_list)-1)
    ssim_list =[]
    print('\ncalculating SSIM......\n')
    for dfile_name in dfile_name_list:
        index = dfile_name_list.index(dfile_name)//sum
        ofile_name = file_name_list[index]
        ssim_cmd = './ffmpeg -s 1920x1088 -i '+ dfile_name + ' -s 1920x1088 -i '+ofile_name+' -lavfi ssim="stats_file=ssim.log" -f null -'
        d = subprocess.Popen(ssim_cmd, shell=True,stderr = subprocess.PIPE)
        d.wait()
        sout = d.stderr.readlines()
        ssim_loc = sout[-1].decode('utf-8').find('All:')
        ssim = sout[-1].decode('utf-8')[ssim_loc+4:ssim_loc+11]
        ssim_list.append(ssim)
        process_bar.display_bar()
    ssim_write = ['Name,SSIM']
    for i in range(len(ssim_list)):
        ssim_write.append(dfile_name_list[i]+','+ssim_list[i])
    with open('SSIM_customized.csv','w',newline='') as ssim_csv:
        for row in ssim_write:
            if row != ssim_write[-1]:
                ssim_csv.write(row+'\n')
            else:
                ssim_csv.write(row)

    #obtain fps
    s_fps_group =[]
    df_score = pd.read_csv(sfile+'.csv')
    sample_list =df_score.loc[:,'Name']
    for sample_name in sname:
        df_sample_fps = pd.DataFrame()
        count = 0
        count_1 = 0
        for samples in sample_list:
             if samples.find(sample_name) != -1:
                 df_sample_fps.insert(count, samples, [df_score.loc[count_1,'Number of Frames'],])
                 count += 1
             count_1 += 1
        s_fps_group.append(df_sample_fps)


    #calculate PSNRHVS and create psnrhvs file
    process_bar = percent(len(dfile_name_list)-1)
    psnrhvs_list =[]
    print('\ncalculating PSNRHVS......\n')
    for dfile_name in dfile_name_list:
        index = dfile_name_list.index(dfile_name)//sum
        ofile_name = file_name_list[index]
        for fps_file in s_fps_group:
            d_file_name = fps_file.columns
            if dfile_name in d_file_name:
                fps = str(fps_file.iloc[0,0])
        psnrhvs_cmd = './vqmt '+ dfile_name + ' '+ofile_name+' 1088 1920 '+fps+' 1 '+dfile_name+' PSNRHVS'
        d = subprocess.Popen(psnrhvs_cmd, shell=True,stderr = subprocess.PIPE,stdout = subprocess.PIPE)
        d.wait()
        psnrhvs_file_name = dfile_name + '_psnrhvs.csv'
        with open(psnrhvs_file_name,'r') as psnrhvs_file:
            psnrhvs_lines = psnrhvs_file.readlines()
            psnrhvs_list.append(psnrhvs_lines[-1][8:-1])
        os.remove(psnrhvs_file_name)
        process_bar.display_bar()
    psnrhvs_write = ['Name,PSNRHVS']
    for i in range(len(psnrhvs_list)):
        psnrhvs_write.append(dfile_name_list[i]+','+psnrhvs_list[i])
    with open('PSNRHVS_customized.csv','w',newline='') as psnrhvs_csv:
        for row in psnrhvs_write:
            if row != psnrhvs_write[-1]:
                psnrhvs_csv.write(row+'\n')
            else:
                psnrhvs_csv.write(row)

    #calculate VIPF and create VIFP file
    process_bar = percent(len(dfile_name_list)-1)
    VIFP_list =[]
    print('\ncalculating VIFP......\n')
    for dfile_name in dfile_name_list:
        index = dfile_name_list.index(dfile_name)//sum
        ofile_name = file_name_list[index]
        for fps_file in s_fps_group:
            d_file_name = fps_file.columns
            if dfile_name in d_file_name:
                fps = str(fps_file.iloc[0,0])
        VIFP_cmd = './vqmt '+ dfile_name + ' '+ofile_name+' 1088 1920 '+fps+' 1 '+dfile_name+' VIFP'
        d = subprocess.Popen(VIFP_cmd, shell=True,stderr = subprocess.PIPE,stdout = subprocess.PIPE)
        d.wait()
        VIFP_file_name = dfile_name + '_VIFP.csv'
        with open(VIFP_file_name,'r') as VIFP_file:
            VIFP_lines = VIFP_file.readlines()
            VIFP_list.append(VIFP_lines[-1][8:-1])
        os.remove(VIFP_file_name)
        process_bar.display_bar()
    VIFP_write = ['Name,VIFP']
    for i in range(len(VIFP_list)):
        VIFP_write.append(dfile_name_list[i]+','+VIFP_list[i])
    with open('VIFP_customized.csv','w',newline='') as VIFP_csv:
        for row in VIFP_write:
            if row != VIFP_write[-1]:
                VIFP_csv.write(row+'\n')
            else:
                VIFP_csv.write(row)


    #calculate VIPF and create PSNRHVSM file
    process_bar = percent(len(dfile_name_list)-1)
    PSNRHVSM_list =[]
    print('calculating PSNRHVSM......\n')
    for dfile_name in dfile_name_list:
        index = dfile_name_list.index(dfile_name)//sum
        ofile_name = file_name_list[index]
        for fps_file in s_fps_group:
            d_file_name = fps_file.columns
            if dfile_name in d_file_name:
                fps = str(fps_file.iloc[0,0])
        PSNRHVSM_cmd = './vqmt '+ dfile_name + ' '+ofile_name+' 1088 1920 '+fps+' 1 '+dfile_name+' PSNRHVSM'
        d = subprocess.Popen(PSNRHVSM_cmd, shell=True,stderr = subprocess.PIPE,stdout = subprocess.PIPE)
        d.wait()
        PSNRHVSM_file_name = dfile_name + '_PSNRHVSM.csv'
        with open(PSNRHVSM_file_name,'r') as PSNRHVSM_file:
            PSNRHVSM_lines = PSNRHVSM_file.readlines()
            PSNRHVSM_list.append(PSNRHVSM_lines[-1][8:-1])
        os.remove(PSNRHVSM_file_name)
        process_bar.display_bar()
    PSNRHVSM_write = ['Name,PSNRHVSM']
    for i in range(len(PSNRHVSM_list)):
        PSNRHVSM_write.append(dfile_name_list[i]+','+PSNRHVSM_list[i])
    with open('PSNRHVSM_customized.csv','w',newline='') as PSNRHVSM_csv:
        for row in PSNRHVSM_write:
            if row != PSNRHVSM_write[-1]:
                PSNRHVSM_csv.write(row+'\n')
            else:
                PSNRHVSM_csv.write(row)

def calculation_1(sfile):
    while (1):
        flag = 0
        set_name = input('Please input the name of the video set (input e to exit): ')
        if set_name == 'e' and sname != []:
            break
        if set_name == 'e' and sname == []:
            print('Please at least input one name')
            flag = 1
        if len(sname) == 10:
            print('This assessment tool only support 10 video sets')
            break
        for p_set_name in sname:
            if set_name == p_set_name:
                print('This name has been input')
                flag = 1
                break
        if flag == 0:
            sname.append(set_name)

    while (1):
        e_name = input('Please input the name of the encodings or distortions (input e to exit): ')
        flag = 0
        if e_name == 'e' and dname_r != []:
            break
        if e_name == 'e' and dname_r == []:
            print('Please at least input one name')
            flag = 1
        if len(dname_r) == 10:
            print('This assessment tool only support 10 types of encodings or distortions')
            break
        for p_e_name in dname_r:
            if p_e_name == e_name:
                print('This name has been input')
                flag = 1
                break
        if flag == 0:
            dname_r.append(e_name)

    names = globals()
    for i in range(len(dname_r)):
        names[dname_r[i]] = []

    for e_name in dname_r:
        while (1):
            try:
                number_e = input('Please input the number of the videos in the ' + e_name + ' distortion: ')
                number_e = int(number_e)
                for i in range(number_e):
                    names[dname_r[dname_r.index(e_name)]].append('_' + e_name + '_' + str(i+1))
                break
            except ValueError:
                print('Please input an integer')
    sum = 0
    for i in range(len(dname_r)):
        sum += len(names[dname_r[i]])
        dname.append(names[dname_r[i]])
    calculation(sum,sfile)











