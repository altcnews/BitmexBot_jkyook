import time
import pandas as pd
import scipy.stats as stat
from datetime import datetime
from sklearn import datasets, linear_model
# import matplotlib
# matplotlib.use("qt4agg")
import matplotlib.pyplot as plt
# from bitmex_bot.settings import settings
import threading
import multiprocessing

class Nprob:

    def __init__(self):
        # global df , nf
        self.nf=0
        self.nfset=0
        self.tick = 0.5
        self.inp=0
        self.profit=0
        self.startime=time.time()
        self.sig_1 = 0
        self.sig_2 = 0
        self.in_str = 0
        self.piox = 0
        self.inp_preset=0
        self.OrgMain='n'
        self.ord_count = 1
        self.turnover=0
        self.org_in_2=0
        self.cri=0
        self.cri_r=0
        self.hit_peak=0
        self.loop=0.5           #Loop_interval(0.25)
        self.sec_15 = int(15 / self.loop)  # = 75  ns, nPXY, stPXY, a~e, ee_s, bump, abump, s1, s2_s, s3, s3_m_m
        self.sec_30 = int(30 / self.loop)  # = 150  mtm, PXYm, stXY, pindex, slope, ee_s_slope, s2_c_m, s3_c, s3_m_short
        self.min_1 = int(60 / self.loop)  # = 300  ststPXY, pindex2, ee_s_ave, ee_s_ox, s3_m_m, dt_main1,2, org_in_2, cri, cri_r, ee_s_cri
        self.min_3 = int(180 / self.loop) # = 900  ee_s_ave_long
        self.min_5 = int(300 / self.loop)
        print 'init Nprob', self.nf
        a = pd.read_csv("index_mex.csv").columns.values.tolist()
        self.df = pd.DataFrame()
        self.df = pd.DataFrame(index=range(0, 1), columns=a)
        print self.df
        # self.thread_plot = multiprocessing.Process(target=self.btnPlot_Clicked, args=())


    def nprob(self, price, timestamp, mt, count, cgubun_sum, cvolume_sum, volume,  lblSqty2v, lblSqty1v, lblShoga1v, lblBqty1v, lblBhoga1v, lblBqty2v): # lblShoga2v,, lblBhoga2v
        # global nf, df, nfset, OrgMain, nowtime

        t_start = time.time()
        self.df.at[self.nf, "nf"] = self.nf
        print 'nf: %d   /prc: %0.1f  /sig_1: %d   /sig_2: %d   /turn_over: %d' % (self.nf, price, self.sig_1, self.sig_2, self.turnover)
        # nowtime=time.time()

        if self.nf!=0 and self.nf%2000==0: # and self.nf>self.min_5
            # self.df=self.df[self.nf-self.min_/3-1:self.nf]
            self.btnSave_Clicked()

        regr = linear_model.LinearRegression()

        ###############################
        # Raw Data
        ###############################

        self.df.at[self.nf, "price"] = price
        self.df.at[self.nf, "cgubun"] = cgubun_sum
        self.df.at[self.nf, "cvolume"] = cvolume_sum
        self.df.at[self.nf, "volume"] = volume
        self.df.at[self.nf, "y2"] = int(lblSqty2v)
        # self.df.at[self.nf, "py2"] = float(lblShoga2v)
        self.df.at[self.nf, "y1"] = int(lblSqty1v)
        self.df.at[self.nf, "py1"] = float(lblShoga1v)
        self.df.at[self.nf, "x1"] = int(lblBqty1v)
        self.df.at[self.nf, "px1"] = float(lblBhoga1v)
        self.df.at[self.nf, "x2"] = int(lblBqty2v)
        # self.df.at[self.nf, "px2"] = float(lblBhoga2v)

        # mt
        if mt ==0:
            mt = self.df.at[self.nf-1, "mt"]

        # cvol_m
        if self.nf < self.sec_15+1:
            cvol_m = 0
        if self.nf >= self.sec_15+1:
            cvol_m = self.df.ix[self.nf - self.sec_15:self.nf - 1, "cvolume"].mean()
        self.df.at[self.nf, "cvol_m"] = cvol_m

        # cvol_s
        if self.nf < self.min_1+1:
            cvol_s = 0
        if self.nf >= self.min_1+1:
            c_y = self.df.ix[self.nf - 9:self.nf - 1, "cvol_m"]
            c_x = self.df.ix[self.nf - 9:self.nf - 1, "stime"]
            cvol_s = regr.fit(c_x.values.reshape(-1, 1), c_y.values.reshape(-1, 1)).coef_[0][0]
        self.df.at[self.nf, "cvol_s"] = cvol_s

        # cvol_t
        if self.nf < self.sec_15+1:
            cvol_t = 0
        if self.nf >= self.sec_15+1:
            cvol_t = cvolume_sum / mt /1000000
        self.df.at[self.nf, "cvol_t"] = cvol_t

        # xnet, ynet
        if self.nf < 2:
            dx1 = 0
            dy1 = 0
            cvol = int(cvolume_sum)
        if self.nf >= 2:
            py1 = float(lblShoga1v)
            px1 = float(lblBhoga1v)
            cvol = int(cvolume_sum)
            y1 = int(lblSqty1v)
            x1 = int(lblBqty1v)
            y2 = int(lblSqty2v)
            x2 = int(lblBqty2v)
            n1px1 = float(self.df.ix[self.nf - 1, "px1"])
            n1py1 = float(self.df.ix[self.nf - 1, "py1"])
            n1x1 = int(self.df.x1[self.nf - 1])
            n1x2 = int(self.df.x2[self.nf - 1])
            n1y1 = int(self.df.y1[self.nf - 1])
            n1y2 = int(self.df.y2[self.nf - 1])
            dx1 = xnet(px1, n1px1, cvol, cgubun_sum, x1, n1x1, x2, n1x2)
            dy1 = ynet(py1, n1py1, cvol, cgubun_sum, y1, n1y1, y2, n1y2)

        self.df.at[self.nf, "dy1"] = dy1
        self.df.at[self.nf, "dx1"] = dx1

        # dxx, dyy, dxy
        if cgubun_sum == "Buy":
            wx = 0
            wy = cvol
        elif cgubun_sum == "Sell":
            wx = cvol
            wy = 0
        else:
            wx = 0
            wy = 0
        #     print("gubun error @ ", self.nf)

        dxx = dx1 + wy
        dyy = dy1 + wx
        dxy = dxx - dyy
        self.df.at[self.nf, "dxx"] = dxx
        self.df.at[self.nf, "dyy"] = dyy
        self.df.at[self.nf, "dxy"] = dxy

        # sX, sY, sXY
        if self.nf == 0:
            sX = 0
            sY = 0
            sXY = 0
        else:
            sX = self.df.ix[self.nf - 1, "sX"] + dxx
            sY = self.df.ix[self.nf - 1, "sY"] + dyy
            sXY = self.df.ix[self.nf - 1, "sXY"] + dxy

        self.df.at[self.nf, "sX"] = sX
        self.df.at[self.nf, "sY"] = sY
        self.df.at[self.nf, "sXY"] = sXY

        #stime
        if self.nf == 1:
            print("startime", self.startime)
        self.df.at[self.nf, "stime"] = timestamp #n
        # owtime

        # dt => count
        self.df.at[self.nf, "dt"] = count

        # count_m
        if self.nf < self.sec_15+1:
            count_m = 0
        if self.nf >= self.sec_15+1:
            count_m = self.df.ix[self.nf - 4:self.nf - 1, "dt"].mean()
        self.df.at[self.nf, "count_m"] = count_m

        # mt
        if self.nf==0:
            mt = 0.5
        self.df.at[self.nf, "mt"] = mt

        # mtm
        if self.nf < self.sec_30+1:
            mtm = 0
        if self.nf >= self.sec_15+1:
            mtm = self.df.ix[self.nf - self.sec_15:self.nf - 1, "mt"].mean()
        self.df.at[self.nf, "mtm"] = mtm

        # count_s
        if self.nf < self.sec_15+1:
            count_s = 0
        if self.nf >= self.sec_15+1:
            r_dt = self.df.ix[self.nf - 5:self.nf - 1, "count_m"]
            r_stime = self.df.ix[self.nf - 5:self.nf - 1, "stime"]
            count_s = regr.fit(r_stime.values.reshape(-1, 1), r_dt.values.reshape(-1, 1)).coef_[0][0]*1000
        self.df.at[self.nf, "count_s"] = count_s

        # ns
        ns = self.nf-self.sec_15
        self.df.at[self.nf, "ns"] = ns

        # nsf
        if ns == 0:
            nsf = 0
        if ns != 0:
            nsf = self.nf - ns
        self.df.at[self.nf, "nsf"] = nsf

        # # nPX, nPY
        # if self.nf < self.sec_30+1:
        #     nPX = 0
        #     nPY = 0
        #     nPXY_d = 0
        # if self.nf >= self.sec_30+1:
        #     nPX = float(3*self.df.ix[self.nf - self.sec_30:self.nf - 1, "x1"].mean() + self.df.ix[self.nf - self.sec_30:self.nf - 1, "x2"].mean()) / 4
        #     nPY = float(3*self.df.ix[self.nf - self.sec_30:self.nf - 1, "y1"].mean() + self.df.ix[self.nf - self.sec_30:self.nf - 1, "y2"].mean()) / 4
        # nPXY = float(nPX + nPY) / 2
        # nPXY_d = nPX- nPY
        # self.df.at[self.nf, "nPX"] = nPX
        # self.df.at[self.nf, "nPY"] = nPY
        # self.df.at[self.nf, "nPXY"] = nPXY
        # self.df.at[self.nf, "nPXY_d"] = nPXY_d

        # x1_m, y1_m
        if self.nf < self.min_1+1:
            x1_m = 0
            y1_m = 0
            nPXY_d_m = 0
        if self.nf >= self.min_1+1:
            x1_m = self.df.ix[self.nf - int(self.min_1*0.75):self.nf - 1, "x1"].mean()
            y1_m = self.df.ix[self.nf - int(self.min_1*0.75):self.nf - 1, "y1"].mean()
            # nXY_d_m = self.df.ix[self.nf - int(self.min_1*0.75):self.nf - 1, "nPXY_d"].mean()
        self.df.at[self.nf, "x1_m"] = x1_m
        self.df.at[self.nf, "y1_m"] = y1_m
        # self.df.at[self.nf, "nXY_d_m"] = nXY_d_m

        # x1_s, y1_s
        if self.nf >= self.min_1+1:
            r_ny = self.df.ix[self.nf - self.sec_15:self.nf - 1, "y1"]
            r_nx = self.df.ix[self.nf - self.sec_15:self.nf - 1, "x1"]
            r_t = self.df.ix[self.nf - self.sec_15:self.nf - 1, "stime"]
            y1_s = regr.fit(r_t.values.reshape(-1, 1), r_ny.values.reshape(-1, 1)).coef_[0][0]
            x1_s = regr.fit(r_t.values.reshape(-1, 1), r_nx.values.reshape(-1, 1)).coef_[0][0]
        else:
            y1_s = 0
            x1_s = 0
        self.df.at[self.nf, "y1_s"] = y1_s
        self.df.at[self.nf, "x1_s"] = x1_s

        # x1_ss, y1_ss
        if self.nf >= self.min_1+1:
            r_ny_s = self.df.ix[self.nf - 7:self.nf - 1, "y1_s"] #.iloc[c]
            r_nx_s = self.df.ix[self.nf - 7:self.nf - 1, "x1_s"] #.iloc[c]
            r_t = self.df.ix[self.nf - 7:self.nf - 1, "stime"] #.iloc[c]
            y1_ss = regr.fit(r_t.values.reshape(-1, 1), r_ny_s.values.reshape(-1, 1)).coef_[0][0]*1000
            x1_ss = regr.fit(r_t.values.reshape(-1, 1), r_nx_s.values.reshape(-1, 1)).coef_[0][0]*1000
        else:
            y1_ss = 0
            x1_ss = 0
        self.df.at[self.nf, "y1_ss"] = y1_ss
        self.df.at[self.nf, "x1_ss"] = x1_ss
        #
        # # stXY
        # if self.nf < self.sec_30+1:
        #     stXY = 0
        # if self.nf >= self.sec_30+1:
        #     stXY = self.df.ix[self.nf - self.sec_30:self.nf - 1, "sXY"].std()
        # self.df.at[self.nf, "stXY"] = stXY

        # # stPXY
        # if self.nf >= self.sec_15+1 and ns < self.nf - 1:
        #     stPXY = self.df.ix[ns:self.nf - 1, "PXY"].std()
        # else:
        #     stPXY = 0
        # self.df.at[self.nf, "stPXY"] = stPXY

        # slope = slope
        if self.nf >= self.sec_15+1:
            # c = range(0, 300, 5)
            ry = self.df.ix[self.nf - self.sec_15:self.nf - 1, "sXY"] #.iloc[c]
            rx = self.df.ix[self.nf - self.sec_15:self.nf - 1, "stime"] #.iloc[c]
            slope = regr.fit(rx.values.reshape(-1, 1), ry.values.reshape(-1, 1)).coef_[0][0]
        else:
            slope = 0
            p_value = 0
            std_err = 0
        self.df.at[self.nf, "slope"] = slope

        # slope_m
        if self.nf < self.sec_15+1:
            slope_m = 0
        if self.nf >= self.sec_15+1:
            slope_m = self.df.ix[self.nf - self.sec_15:self.nf - 1, "slope"].mean()
        self.df.at[self.nf, "slope_m"] = slope_m


        # slope_s
        if self.nf >= self.sec_30+1:
            ry = self.df.ix[self.nf - self.sec_15:self.nf - 1, "slope"] #.iloc[c]
            rx = self.df.ix[self.nf - self.sec_15:self.nf - 1, "stime"] #.iloc[c]
            slope_s = regr.fit(rx.values.reshape(-1, 1), ry.values.reshape(-1, 1)).coef_[0][0] * 1000
        else:
            slope_s = 0
            p_value_s = 0
            std_err_s = 0
        self.df.at[self.nf, "slope_s"] = slope_s

        # ee
        if self.nf >= self.sec_15+1:
            if mt < 0.98:
                ee_mt = 1 + stat.norm.ppf((1 - mt) / float(1))
            if mt >= 0.98:
                ee_mt = 1
        else:
            ee_mt = 1
        if ee_mt<0:
            ee_mt=0.001
        self.df.at[self.nf, "ee_mt"] = ee_mt

        # ee_s
        if self.nf >= self.sec_15+1:
            ee_s = self.df.ix[self.nf - self.sec_15:self.nf-1, "ee_mt"].mean()
        else:
            ee_s = 1
        self.df.at[self.nf, "ee_s"] = ee_s

        # ee_s_ave
        if self.nf >= self.min_1+1:
            ee_s_ave = self.df.ix[self.nf - self.min_1:self.nf, "ee_s"].mean()
        else:
            ee_s_ave = 1
        self.df.at[self.nf, "ee_s_ave"] = ee_s_ave


        ###############################
        #  // PIOX //
        ###############################

        if self.piox == 8:
            if cvol_t < 15:
                self.piox = 0
        if self.piox == -8:
            if cvol_t > -15:
                self.piox = 0

        if self.piox < 5 and self.piox > 0 :
            if slope_s<5 and slope_m<100:
                if y1_m > 500000 or y1 > y1_m:
                    self.piox = 0

        if self.piox > -5 and self.piox < 0 :
            if slope_s>-5 and slope_m>-100:
                if x1_m > 500000 or x1 > x1_m:
                    self.piox = 0

        ###############################
        #  // In Decision //
        ###############################

        if self.nf >  self.min_1+1 :

            # after-peak
            if cvol_t > 15:
                self.sig_1 = 0.5
            if self.sig_1 == 0.5 and cvol_t < 15:
                self.sig_1 = 0
            if self.sig_1 == 0.5 and cvol_s < 0 and cvol_t < -5:
                self.sig_1 = 1
                if self.OrgMain == 'n' and self.piox==0:
                    self.in_str = 1
                    self.OrgMain = "s"
                    self.nfset = self.nf
                    self.inp = float(lblBhoga1v)

            if cvol_t < -15:
                self.sig_1 = -0.5
            if self.sig_1 == -0.5 and cvol_t > -15:
                self.sig_1 = 0
            if self.sig_1 == -0.5 and cvol_s > 0 and cvol_t > 5:
                self.sig_1 = -1
                if self.OrgMain == 'n' and self.piox==0:
                    self.in_str = -1
                    self.OrgMain = "b"
                    self.nfset = self.nf
                    self.inp = float(lblShoga1v)

            # keep-going
            if count_m<20 and abs(slope)<200:

                if cvol_t>15 and cvol_s>10: #and y1 < 200000
                    self.sig_2 = 2
                    if self.OrgMain == 'n' and self.piox==0:
                        self.in_str = 2
                        self.OrgMain = "b"
                        self.nfset = self.nf
                        self.inp = float(lblShoga1v)

                if cvol_t<-15 and cvol_s<-10:  #and x1 < 200000
                        self.sig_2 = -2
                        if self.OrgMain == 'n' and self.piox==0:
                            self.in_str= -2
                            self.OrgMain = "s"
                            self.nfset = self.nf
                            self.inp = float(lblBhoga1v)

                    # if y1_m != 0 and y1 < 100000 and y1_s<0: # and y1_ss<0:
                    #     if  count_s>0.5 and cvol_s>0:
                    #             if self.OrgMain == 'n':
                    #                 self.sig = 2
                    #                 self.OrgMain = "b"
                    #                 self.nfset = self.nf
                    #                 self.inp = float(lblShoga1v)
                    #
                    # if x1_m != 0 and x1 < 100000 and x1_s<0: # and x1_ss<0:
                    #     if count_s > 0.5 and cvol_s < 0:
                    #         if self.OrgMain == 'n':
                    #             self.sig = -2
                    #             self.OrgMain = "s"
                    #             self.nfset = self.nf
                    #             self.inp = float(lblBhoga1v)

            # # afterpeaking
            # if self.piox==0 and nPX>nPX_m and cvol_s > 5 and slope<-30:
            #     if self.OrgMain == 'n':
            #         self.sig = 1
            #         self.OrgMain = "b"
            #         self.nfset = self.nf
            #         self.inp = float(lblShoga1v)
            #
            # if self.piox==0 and nPY > nPY_m and cvol_s < -5 and slope > 30:
            #     if self.OrgMain == 'n':
            #         self.sig = -1
            #         self.OrgMain = "s"
            #         self.nfset = self.nf
            #         self.inp = float(lblBhoga1v)

        self.df.at[self.nf, "inp"] = self.inp
        self.df.at[self.nf, "inp_preset"] = self.inp_preset
        self.df.at[self.nf, "sig_1"] = self.sig_1
        self.df.at[self.nf, "sig_2"] = self.sig_2
        self.df.at[self.nf, "nfset"] = self.nfset

        ###############################
        # hit_peak setting
        ###############################

        # prf_able
        prf_able = 0
        profit_band = 20 * ee_s
        loss_band = 30 * ee_s
        if profit_band>40:
            profit_band=40
        if profit_band<30:
            profit_band=30
        if loss_band>60:
            loss_band=60
        if loss_band<40:
            loss_band=40
        if self.OrgMain == "b":
            if price >= self.inp + self.tick * profit_band:
                prf_able = 1
            if price <= self.inp - self.tick * loss_band:
                prf_able = -1
        if self.OrgMain == "s":
            if price <= self.inp - self.tick * profit_band:
                prf_able = 1
            if price >= self.inp + self.tick * loss_band:
                prf_able = -1
        self.df.at[self.nf, "prf_able"] = prf_able

            # cvol_peak
        if cvol_s>50:
            self.hit_peak = 6
        if cvol_s<-50:
            self.hit_peak = -6

        ###############################
        #  // Out Decision //
        ###############################

        # piox
        self.piox=0
        if self.OrgMain == "b":

            # #  high peak (same direction)
            # if count > 15 and slope > 200:
            #     self.profit += ((float(lblBhoga1v) - self.inp) - (
            #             float(lblBhoga1v) + self.inp) * 0.00075) * self.ord_count
            #     self.piox = 9
            #     self.OrgMain = 'n'
            #     self.turnover += 1
            #     self.inp_preset = 0

            #  high peak (slope_s conversion)
            if self.in_str == 2 and cvol_t<15 and y1>100000 and slope>30:
                if cvol_s < -5 or y1_ss >0:
                    self.profit += ((float(lblBhoga1v) - self.inp) - (
                            float(lblBhoga1v) + self.inp) * 0.00075 /2) * self.ord_count
                    self.piox = 8
                    self.in_str = 0
                    self.OrgMain = 'n'
                    self.turnover += 1

            #  after - peak

            if self.in_str == -1 and cvol_s < 0:
                self.profit += ((float(lblBhoga1v) - self.inp) - (
                        float(lblBhoga1v) + self.inp) * 0.00075 /2) * self.ord_count
                self.piox = 7
                self.in_str = 0
                self.OrgMain = 'n'
                self.turnover += 1


            # # high peak (opposite direction)
            # if self.OrgMain == "b" and count_m > 10 and slope_m < 0:
            #     self.profit += ((float(lblBhoga1v) - self.inp) - (
            #             float(lblBhoga1v) + self.inp) * 0.00075) * self.ord_count
            #     self.piox = 6
            #     self.OrgMain = 'n'
            #     self.turnover += 1
            #     self.inp_preset = 0

            if prf_able != 0:

                # bad_out (opposite direction)
                if self.OrgMain == "b" and ee_s > ee_s_ave and ee_s>1.5  and ee_s_ave > 1.3:
                    if slope_s<0 and slope_m < -100:
                        self.profit+=((float(lblBhoga1v)-self.inp) - (float(lblBhoga1v)+self.inp)*0.00075/2)* self.ord_count
                        self.piox = 1
                        self.in_str = 0
                        self.OrgMain='n'
                        self.turnover += 1

                # good_out (weakening)
                if self.OrgMain == "b":
                    if count_m<5:
                        if ee_s<ee_s_ave or y1_m>400000 or y1>y1_m:
                            self.profit += ((float(lblBhoga1v) - self.inp) - (
                                        float(lblBhoga1v) + self.inp) * 0.00075/2) * self.ord_count
                            self.piox = 4
                            self.in_str = 0
                            self.OrgMain='n'
                            self.turnover += 1

        elif self.OrgMain == "s": #  and lstm_mean>0.75:

            # #  high peak (same direction)
            # if count > 20 and slope < -200:
            #     self.profit += ((self.inp - float(lblBhoga1v)) - (
            #             float(lblBhoga1v) + self.inp) * 0.00075) * self.ord_count
            #     self.piox = -9
            #     self.OrgMain = 'n'
            #     self.turnover += 1
            #     self.inp_preset = 0

            #  high peak (slope_s conversion)
            if cvol_t<15 and x1>100000 and cvol_s > 5 and slope<-30:
                if cvol_s > 5 or x1_ss > 0:
                    self.profit += ((self.inp - float(lblBhoga1v)) - (
                            float(lblBhoga1v) + self.inp) * 0.00075/2) * self.ord_count
                    self.piox = -8
                    self.in_str = 0
                    self.OrgMain = 'n'
                    self.turnover += 1
                    self.in_str = 0

            if self.in_str == 1 and cvol_s > 0:
                self.profit += ((self.inp - float(lblBhoga1v)) - (
                        float(lblBhoga1v) + self.inp) * 0.00075 / 2) * self.ord_count
                self.piox = -7
                self.in_str = 0
                self.OrgMain = 'n'
                self.turnover += 1

            # # high peak (opposite direction)
            # if self.OrgMain == "s" and count_m > 10 and slope_m > 0:
            #     self.profit += ((self.inp - float(lblBhoga1v)) - (
            #             float(lblBhoga1v) + self.inp) * 0.00075) * self.ord_count
            #     self.piox = -6
            #     self.OrgMain = 'n'
            #     self.turnover += 1
            #     self.inp_preset = 0

            if prf_able != 0:

                # bad_out (opposite direction)
                if self.OrgMain == "s" and ee_s > ee_s_ave and ee_s>1.5  and ee_s_ave > 1.3:
                    if slope_s>0 and slope_m > 100:
                        self.profit += ((self.inp-float(lblBhoga1v)) - (float(lblBhoga1v)+self.inp)*0.00075/2) * self.ord_count
                        self.piox = -1
                        self.in_str = 0
                        self.OrgMain='n'
                        self.turnover += 1

                # good_out (weakening)
                if self.OrgMain == "s":
                    if count_m<5:
                        if ee_s<ee_s_ave or x1_m>400000 or x1>x1_m:
                            self.profit += ((self.inp-float(lblBhoga1v)) - (float(lblBhoga1v)+self.inp)*0.00075/2) * self.ord_count
                            self.piox = -4
                            self.in_str = 0
                            self.OrgMain='n'
                            self.turnover += 1

        self.df.at[self.nf, "piox"] = self.piox
        self.df.at[self.nf, "profit"] = self.profit
        self.df.at[self.nf, "ord_count"] = self.ord_count
        self.df.at[self.nf, "in_str"] = self.in_str

        ###############################
        #  // RESET & ETC //
        ###############################

        if self.OrgMain=="b":
            self.d_OMain = 1
        elif self.OrgMain=="s":
            self.d_OMain = -1
        elif self.OrgMain == "n":
            self.d_OMain = 0
            self.ord_count = 1
            self.hit_peak = 0
            self.inp = 0
            self.nfset = 0

        self.df.at[self.nf, "d_OMain"] = self.d_OMain
        self.df.at[self.nf, "OrgMain"] = self.OrgMain
        print "OrgMain", self.OrgMain

        self.nf+=1

        if self.nf>10:
            print self.df.ix[self.nf-9:self.nf-1,['dt', 'count_s', 'cvol_t', 'cvol_s', 'sig_1', 'sig_2', 'in_str', 'OrgMain', 'inp','profit']] #, 'x1_ss',  'y1_ss'
            print '-----------'

        elap = time.time() - t_start
        self.df.at[self.nf, "elap"] = elap
        print "elap", elap

        return self.d_OMain

    def threadme(self):
        thread_plot = threading.Thread(target=self.btnPlot_Clicked, args=())
        thread_plot.start()

    def btnPlot_Clicked(self):
        global plt

        ax1 = plt.subplot(511)
        ax2 = ax1.twinx()
        ax3 = plt.subplot(512)
        ax4 = ax3.twinx()
        ax5 = plt.subplot(513)
        ax6 = ax5.twinx()
        ax7 = plt.subplot(514)
        ax8 = ax7.twinx()
        ax9 = plt.subplot(515)
        ax10 = ax9.twinx()

        # Plot range
        plot_start = 1
        plot_last = self.nf - 1

        # plot
        p1 = self.df.ix[plot_start:plot_last, "sXY"]
        ax1.plot(p1, 'r')
        p2 = self.df.ix[plot_start:plot_last, "d_OMain"]
        ax2.plot(p2, 'g')

        p3 = self.df.ix[plot_start:plot_last, "ee_s"]
        ax3.plot(p3, 'r')
        p4 = self.df.ix[plot_start:plot_last, "ee_s_ave"]
        ax4.plot(p4, 'g')

        p5 = self.df.ix[plot_start:plot_last, "apindex_s"]
        ax7.plot(p5, 'r')
        p6 = self.df.ix[plot_start:plot_last, "pindex"]
        ax6.plot(p6, 'g')

        p7 = self.df.ix[plot_start:plot_last, "profit_o"]
        ax7.plot(p7, 'r')
        p8 = self.df.ix[plot_start:plot_last, "org_in_2"]
        ax8.plot(p8, 'g')

        p9 = self.df.ix[plot_start:plot_last, "cri"]
        ax9.plot(p9, 'r')
        p10 = self.df.ix[plot_start:plot_last, "cri_r"]
        ax10.plot(p10, 'g')

        # show
        plt.legend(loc='upper left', frameon=False)
        print 'a'
        # plt.ion()
        plt.show()
        time.sleep(4)

    def btnPlot_Close(self):
        global plt
        plt.clf()

    def btnSave_Clicked(self):
        #df.to_sql("Main_DB", con, if_exists='replace', index=True) #, index_label=None, chunksize=None, dtype=None)
        ts = datetime.now().strftime("%m-%d-%H-%M")
        filename = "EDB__%s.csv" %  (ts)
        self.df.to_csv('%s' % filename)  # + time.strftime("%m-%d") + '.csv')
        print 'Saved'


def ynet(p, t, W, sw, a, b, c, d):

    if p == t:
        if sw == "Buy":
            result = (a - b + W)
        else:
            result = (a - b)

    elif p < t:
        if sw == "Buy":
            result = (a - b + c) + W
        else:
            result = (a - b + c)

    elif p > t:
        if sw == "Buy":
            result = (a - b - d) + W   #= W - b + a - d
        else:
            result = (a - b - d)

    return result

def xnet(p, t, W, sw, a, b, c, d):

    if p == t:
        if sw == "Sell":
            result = (a - b + W)
        else:
            result = (a - b)

    elif p > t:
        if sw == "Sell":
            result = (a - b + c) + W
        else:
            result = (a - b + c)

    elif p < t:
        if sw == "Sell":
            result = (a - b - d) + W
        else:
            result = (a - b - d)

    return result

