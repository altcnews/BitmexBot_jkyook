import time
import pandas as pd
import scipy.stats as stat
from datetime import datetime
from sklearn import datasets, linear_model

which_market = 1 #(1:bitmex, 2:upbit, 3:kospi)

class Nprob:

    def __init__(self):
        # global df , nf
        self.nf=0
        self.nfset=0

        if which_market == 1:  # Bit
            self.tick = 0.5
            self.loop = 0.5
            self.count_m_act = 10
            self.count_m_deact = 5
            self.count_m_overact = 25
            self.dt_overact = self.count_m_overact
            self.cvol_t_act = 5000
            self.cvol_t_low_act = 2000
            self.cvol_s_act = 5
            self.cvol_s_low_act = 3
            self.dxy_200_medi_bottom = 250
            self.fee_rate = 0.00075 * 2
            self.profit_min_tick = 25
            self.loss_max_tick = 80
        elif which_market == 2:  # UPBIT
            self.tick = 1000
            self.loop = 1
            self.count_m_act = 10
            self.count_m_deact = 3
            self.count_m_overact = 15
            self.dt_overact = self.count_m_overact * 2
            self.cvol_t_act = 20
            self.cvol_t_low_act = 10
            self.cvol_s_act = 0.1
            self.cvol_s_low_act = 0.05
            self.dxy_200_medi_bottom = 100000
            self.fee_rate = 0.0005 * 2
            self.profit_min_tick = 10
            self.loss_max_tick = 40
        elif which_market == 3:  # Kospi
            self.tick = 0.05
            self.loop = 0.5
            self.count_m_act = 10
            self.count_m_deact = 5
            self.count_m_overact = 20
            self.dt_overact = self.count_m_overact
            self.cvol_t_act = 10000
            self.cvol_t_low_act = 3000
            self.cvol_s_act = 10
            self.cvol_s_low_act = 5
            self.dxy_200_medi_bottom = 250
            self.fee_rate = 0.00003 * 2
            self.profit_min_tick = 4
            self.loss_max_tick = 15

        self.inp=0
        self.last_o = 0
        self.profit=0
        self.startime=time.time()
        self.sig_1 = 0
        self.sig_2 = 0
        self.sig_3 = 0
        self.in_str_1 = 0
        self.in_str = 0
        self.piox = 0
        self.OrgMain='n'
        self.AvePrc = 0
        self.ExedQty = 0
        self.add_count = 1
        self.minus_count = 1
        self.turnover=0
        self.prf_able = 0
        self.prf_hit = 0
        self.sec_15 = int(15 / self.loop)  # = 75  ns, nPXY, stPXY, a~e, ee_s, bump, abump, s1, s2_s, s3, s3_m_m
        self.sec_30 = int(30 / self.loop)  # = 150  mtm, PXYm, stXY, pindex, sXY_s, ee_s_slope, s2_c_m, s3_c, s3_m_short
        self.min_1 = int(60 / self.loop)  # = 300  ststPXY, pindex2, ee_s_ave, ee_s_ox, s3_m_m, dt_main1,2, org_in_2, cri, cri_r, ee_s_cri
        self.min_3 = int(180 / self.loop) # = 900  ee_s_ave_long
        self.min_5 = int(300 / self.loop)
        print ('init Nprob', self.nf)
        a = pd.read_csv("index_mex.csv").columns.values.tolist()
        self.df = pd.DataFrame()
        self.df = pd.DataFrame(index=range(0, 1), columns=a)
        print (self.df)


    def nprob(self, price, timestamp, mt, count, cgubun_sum, cvolume_sum, volume,  lblSqty2v, lblSqty1v, lblShoga1v, lblBqty1v, lblBhoga1v, lblBqty2v): # lblShoga2v,, lblBhoga2v

        # cvolume_sum = cvolume_sum * self.cvol_adj

        t_start = time.time()
        self.df.at[self.nf, "nf"] = self.nf
        print ('nf: %d  /prc: %0.2f /in: %d /out: %0.1f /prf: %d /piox: %d  /last_o %0.2f  /turn: %d' % (self.nf, price, self.in_str, self.piox, self.prf_able, self.piox, self.last_o, self.turnover))

        if self.nf!=0 and self.nf%500==0:
            self.btnSave_Clicked()

        regr = linear_model.LinearRegression()

        ###############################
        # Raw Data
        ###############################

        self.df.at[self.nf, "price"] = price
        self.df.at[self.nf, "cgubun"] = cgubun_sum
        self.df.at[self.nf, "cvolume"] = cvolume_sum
        self.df.at[self.nf, "volume"] = volume
        self.df.at[self.nf, "y2"] = lblSqty2v
        self.df.at[self.nf, "y1"] = lblSqty1v
        self.df.at[self.nf, "py1"] = lblShoga1v
        self.df.at[self.nf, "x1"] = lblBqty1v
        self.df.at[self.nf, "px1"] = lblBhoga1v
        self.df.at[self.nf, "x2"] = lblBqty2v

        # xnet, ynet
        if self.nf < 2:
            dx1 = 0
            dy1 = 0
            cvol = cvolume_sum
        if self.nf >= 2:
            if which_market !=3:
                py1 = lblShoga1v
                px1 = lblBhoga1v
                cvol = cvolume_sum
                y1 = lblSqty1v
                x1 = lblBqty1v
                y2 = lblSqty2v
                x2 = lblBqty2v
                n1px1 = self.df.ix[self.nf - 1, "px1"]
                n1py1 = self.df.ix[self.nf - 1, "py1"]
                n1x1 = self.df.x1[self.nf - 1]
                n1x2 = self.df.x2[self.nf - 1]
                n1y1 = self.df.y1[self.nf - 1]
                n1y2 = self.df.y2[self.nf - 1]
                dx1 = xnet(px1, n1px1, cvol, cgubun_sum, x1, n1x1, x2, n1x2)
                dy1 = ynet(py1, n1py1, cvol, cgubun_sum, y1, n1y1, y2, n1y2)
            else:
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

        # dxx,dyy ave_20
        if self.nf < self.sec_30+1:
            dxx_20 = 0
            dyy_20 = 0
        if self.nf >= self.sec_30+1:
            dxx_20 = self.df.ix[self.nf - 20:self.nf - 1, "dxx"].sum()
            dyy_20 = self.df.ix[self.nf - 20:self.nf - 1, "dyy"].sum()
        self.df.at[self.nf, "dxx_20"] = dxx_20
        self.df.at[self.nf, "dyy_20"] = dyy_20

        # dxx,dyy med_20
        if self.nf < self.sec_30+1:
            dxx_20_medi = 0
            dyy_20_medi = 0
        if self.nf >= self.sec_30+1:
            dxx_20_medi = self.df.ix[self.nf - 50:self.nf - 1, "dxx_20"].median()
            dyy_20_medi = self.df.ix[self.nf - 50:self.nf - 1, "dyy_20"].median()
        self.df.at[self.nf, "dxx_20_medi"] = dxx_20_medi
        self.df.at[self.nf, "dyy_20_medi"] = dyy_20_medi
        dxy_20_medi = dxx_20_medi - dyy_20_medi
        self.df.at[self.nf, "dxy_20_medi"] = dxy_20_medi
        # print 'x_20_medi: %d   /y_20_medi: %d' % (dxx_20_medi, dyy_20_medi)

        # dxy med_200
        if self.nf < self.min_1*3/2+1:
            dxy_200_medi = 0
        if self.nf >= self.min_1*3/2+1:
            dxy_200_medi = self.df.ix[self.nf - 200:self.nf - 1, "dxy_20_medi"].median()
        self.df.at[self.nf, "dxy_200_medi"] = dxy_200_medi

        # dxy med_200_s
        if self.nf >= self.sec_30+1 and dxy_200_medi != 0:
            d_y = self.df.ix[self.nf - self.sec_30:self.nf - 1, "dxy_200_medi"]
            d_x = self.df.ix[self.nf - self.sec_30:self.nf - 1, "stime"]
            dxy_med_200_s = regr.fit(d_x.values.reshape(-1, 1), d_y.values.reshape(-1, 1)).coef_[0][0]
        else:
            dxy_med_200_s = 0
        self.df.at[self.nf, "dxy_med_200_s"] = dxy_med_200_s

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
        if self.nf == 0:
            mt = 0.5
        self.df.at[self.nf, "mt"] = mt

        # cvol_c
        if self.nf < self.sec_15+1:
            cvol_c = 0
        if self.nf >= self.sec_15+1:
            cvol_c = self.df[self.nf - 20:self.nf - 1][self.df.cvolume[self.nf - 20:self.nf - 1]>0].count()[0]
        self.df.at[self.nf, "cvol_c"] = cvol_c
        # print 'cvol_c: ', cvol_c

        # cvol_c_ave
        if self.nf < 200+1:
            cvol_c_ave = 10
        if self.nf >= 200+1:
            cvol_c_ave = (self.df.ix[self.nf - 200, "cvol_c"]+ cvol_c)/2
        self.df.at[self.nf, "cvol_c_ave"] = cvol_c_ave

        # cvol_m
        if self.nf < self.sec_15+1:
            cvol_m = 0
        if self.nf >= self.sec_15+1:
            cvol_m = self.df.ix[self.nf - self.sec_15:self.nf - 1, "cvolume"].mean()
        self.df.at[self.nf, "cvol_m"] = cvol_m

        # cvol_s
        if self.nf < self.sec_30+1:
            cvol_s = 0
        if self.nf >= self.sec_30+1:
            c_y = self.df.ix[self.nf - 9:self.nf - 1, "cvol_m"]
            c_x = self.df.ix[self.nf - 9:self.nf - 1, "stime"]
            cvol_s = regr.fit(c_x.values.reshape(-1, 1), c_y.values.reshape(-1, 1)).coef_[0][0]
        self.df.at[self.nf, "cvol_s"] = cvol_s * 3600
        # print 'cvol_s: ', cvol_s

        # cvol_s_15
        if self.nf < self.min_1+1:
            cvol_s_15 = 0
        if self.nf >= self.min_1+1:
            c_y_3 = self.df.ix[self.nf - self.sec_15:self.nf - 1, "cvol_m"]
            c_x_3 = self.df.ix[self.nf - self.sec_15:self.nf - 1, "stime"]
            cvol_s_15 = regr.fit(c_x_3.values.reshape(-1, 1), c_y_3.values.reshape(-1, 1)).coef_[0][0]
        self.df.at[self.nf, "cvol_s_15"] = cvol_s_15

        # cvol_t
        if self.nf < self.sec_15+1:
            cvol_t = 0
        if self.nf >= self.sec_15+1:
            cvol_t = cvolume_sum / mt
        self.df.at[self.nf, "cvol_t"] = cvol_t

        # sXY_s
        if self.nf >= self.sec_15+1:
            # c = range(0, 300, 5)
            ry = self.df.ix[self.nf - self.sec_15:self.nf - 1, "sXY"] #.iloc[c]
            rx = self.df.ix[self.nf - self.sec_15:self.nf - 1, "stime"] #.iloc[c]
            sXY_s = regr.fit(rx.values.reshape(-1, 1), ry.values.reshape(-1, 1)).coef_[0][0]
        else:
            sXY_s = 0
            p_value = 0
            std_err = 0
        self.df.at[self.nf, "sXY_s"] = sXY_s

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

        ###############################
        #  // PIOX //
        ###############################

        if count_m < self.count_m_overact and abs(self.piox) !=1.5 and abs(self.piox) !=2.5:
            if self.piox > 0:
                if self.piox == 1 or self.piox == 0.5:
                    if cvol_t > 0  and count_m<self.count_m_deact:
                       self.piox = 0
                if self.piox == 2:
                    if cvol_s > 0 and cvol_t > 0:
                        self.piox = 0
                if self.piox == 3:
                    if cvol_t > 0:
                       self.piox = 0
                if self.piox == 5:
                    if count_m < self.count_m_deact:
                       self.piox = 0

            if self.piox < 0:
                if self.piox == -1 or self.piox == -0.5:
                    if cvol_t < 0 and count_m<self.count_m_deact:
                       self.piox = 0
                if self.piox == -2:
                    if cvol_s < 0 and cvol_t < 0:
                        self.piox = 0
                if self.piox == -3:
                    if cvol_t < 0:
                       self.piox = 0
                if self.piox == -5:
                    if count_m < self.count_m_deact:
                       self.piox = 0

        if abs(self.piox) == 1.5 or abs(self.piox) == 2.5:
            if count_m<self.count_m_deact:
                self.piox = 0

        if self.piox == 5.5:
            if self.d_OMain == 2:
                self.piox = 0
        if self.piox == -5.5:
            if  self.d_OMain == -2:
                self.piox = 0

        ###############################
        #  // In Decision //
        ###############################

        if self.nf >  self.min_1+1:

            # After-peak
            if 1==1:
                self.sig_3 = 0
                if count_m > self.count_m_act:
                    self.sig_3 = 0.5
                    if self.in_str_1 == 0:
                        self.in_str_1 = 0.5
                if self.in_str_1 == 0.5 or self.in_str == 2 or self.piox == 2:
                    if count_m<self.count_m_deact:
                        self.sig_3 = 0
                        self.in_str_1 = 0
                    if count_m>self.count_m_deact:
                        if cvol_s < 0 and cvol_t < self.cvol_t_low_act * -1:
                            self.sig_3 = 1
                            if self.OrgMain == 'n' and self.piox==0:
                                self.in_str_1 = 1
                                self.OrgMain = "s"
                                self.nfset = self.nf
                                self.inp = float(lblBhoga1v)
                                self.last_o = float(lblBhoga1v)
                if self.piox == 2.5:
                    if self.OrgMain == 'n' and self.piox==0:
                        self.in_str_1 = 1
                        self.OrgMain = "s"
                        self.nfset = self.nf
                        self.inp = float(lblBhoga1v)
                        self.last_o = float(lblBhoga1v)

                if count_m > self.count_m_act:
                    self.sig_3 = -0.5
                    if self.in_str_1 == 0:
                        self.in_str_1 = -0.5
                if self.in_str_1 == -0.5 or self.in_str == -2 or self.piox == -2:
                    if count_m < self.count_m_deact:
                        self.sig_3 = 0
                        self.in_str_1 = 0
                    if count_m > self.count_m_deact:
                        if cvol_s > 0 and cvol_t > self.cvol_t_low_act:
                            self.sig_3 = -1
                            if self.OrgMain == 'n' and self.piox==0:
                                self.in_str_1 = -1
                                self.OrgMain = "b"
                                self.nfset = self.nf
                                self.inp = float(lblShoga1v)
                                self.last_o = float(lblShoga1v)
                if self.piox == -2.5:
                    if self.OrgMain == 'n' and self.piox==0:
                        self.in_str_1 = -1
                        self.OrgMain = "b"
                        self.nfset = self.nf
                        self.inp = float(lblShoga1v)
                        self.last_o = float(lblShoga1v)

            # Keep-going
            if 1==1:
                self.sig_2 = 0
                if count_m<self.count_m_overact and ee_s<2.5:
                    if cvol_t>self.cvol_t_act and cvol_s>self.cvol_s_act:
                            self.sig_2 = 2
                            if self.in_str == 1:
                                self.in_str = 2
                            if self.OrgMain == 'n' and self.piox==0:
                                self.in_str = 2
                                self.OrgMain = "b"
                                self.nfset = self.nf
                                self.inp = float(lblShoga1v)
                                self.last_o = float(lblShoga1v)
                    if cvol_t<self.cvol_t_act * -1 and cvol_s<self.cvol_s_act*-1:
                            self.sig_2 = -2
                            if self.in_str == -1:
                                self.in_str = -2
                            if self.OrgMain == 'n' and self.piox==0:
                                self.in_str= -2
                                self.OrgMain = "s"
                                self.nfset = self.nf
                                self.inp = float(lblBhoga1v)
                                self.last_o = float(lblBhoga1v)
                if self.piox == 1.5:
                    if self.OrgMain == 'n':
                        self.in_str = -2
                        self.OrgMain = "s"
                        self.nfset = self.nf
                        self.inp = float(lblBhoga1v)
                        self.last_o = float(lblBhoga1v)
                if self.piox == -1.5:
                    if self.OrgMain == 'n':
                        self.in_str = 2
                        self.OrgMain = "b"
                        self.nfset = self.nf
                        self.inp = float(lblShoga1v)
                        self.last_o = float(lblShoga1v)

        # Trend_In_200
        if 1==1:
            self.sig_1 = 0
            if self.nf >  self.min_1*3/2+1 :
                if self.piox != 2 and self.piox != 2.5 and ee_s<2 and count_m<self.count_m_overact:
                    if dxy_200_medi>self.dxy_200_medi_bottom * -1 and dxy_med_200_s>0 and cvol_c_ave>10 and cvol_c>10 and abs(cvol_t)<self.cvol_t_low_act:
                        self.sig_1 = 1
                        if self.OrgMain == 'n' and self.piox==0:
                            self.OrgMain = "b"
                            self.in_str = 1
                            self.nfset = self.nf
                            self.inp = float(lblShoga1v)
                            self.last_o = float(lblShoga1v)

                if self.piox != -2 and self.piox != -2.5 and ee_s<2 and count_m<self.count_m_overact:
                    if dxy_200_medi<self.dxy_200_medi_bottom and dxy_med_200_s<0 and cvol_c_ave<10 and cvol_c<10 and abs(cvol_t)<self.cvol_t_low_act:
                        self.sig_1 = -1
                        if self.OrgMain == 'n' and self.piox==0:
                            self.OrgMain = "s"
                            self.in_str = -1
                            self.nfset = self.nf
                            self.inp = float(lblBhoga1v)
                            self.last_o = float(lblBhoga1v)

        self.df.at[self.nf, "inp"] = self.inp
        self.df.at[self.nf, "in_str_1"] = self.in_str_1
        self.df.at[self.nf, "in_str"] = self.in_str
        self.df.at[self.nf, "sig_1"] = self.sig_1
        self.df.at[self.nf, "sig_2"] = self.sig_2
        self.df.at[self.nf, "sig_3"] = self.sig_3
        self.df.at[self.nf, "nfset"] = self.nfset

        ###############################
        # hit_peak setting
        ###############################

        # prf_able
        self.prf_able = 0
        profit_band = self.profit_min_tick * ee_s
        loss_band = self.loss_max_tick * ee_s
        if profit_band>self.profit_min_tick*3:
            profit_band=self.profit_min_tick*3
        if profit_band<self.profit_min_tick:
            profit_band=self.profit_min_tick
        if loss_band>self.loss_max_tick:
            loss_band=self.loss_max_tick
        if loss_band<self.loss_max_tick/2:
            loss_band=self.loss_max_tick/2
        if self.OrgMain == "b":
            if price >= self.inp + self.tick * profit_band:
                self.prf_able = 1
                self.prf_hit = 1
            if price <= self.inp - self.tick * loss_band:
                self.prf_able = -1
        if self.OrgMain == "s":
            if price <= self.inp - self.tick * profit_band:
                self.prf_able = 1
                self.prf_hit = 1
            if price >= self.inp + self.tick * loss_band:
                self.prf_able = -1
        self.df.at[self.nf, "prf_able"] = self.prf_able

        ###############################
        #  // Out Decision //
        ###############################

        # Peak_Out
        if 1 == 1:
            if self.OrgMain == "b":

                # trnd_out
                if self.in_str == 1:
                    if self.sig_1 == -1 and count_m > self.count_m_deact:
                        count_cri = self.df[self.nf - 20:self.nf - 1][self.df.dt[self.nf - 20:self.nf - 1]>self.dt_overact].count()[0]
                        if count_cri>3:
                            self.profit += ((float(lblBhoga1v) - self.inp) - (
                                float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                            self.piox = 5
                            self.in_str = 0
                            self.OrgMain = 'n'
                            self.turnover += 1
                        else:
                            if float(lblBhoga1v) > self.last_o and abs(self.ExedQty) > 1 and self.piox != 4:
                                self.minus_count += 1
                                self.piox = 4
                                self.last_o = float(lblBhoga1v)
                                self.inp = (self.inp * (abs(self.ExedQty)) - float(lblShoga1v)) / (abs(self.ExedQty) - 1)
                                print('last_o', self.last_o)
                                print('now_prc', float(lblBhoga1v))
                                print('minus_count', self.minus_count)
                    if self.sig_1 == 1 and count_m > self.count_m_deact:
                        if float(lblShoga1v) < self.last_o - self.tick*5 and self.piox != 5.5:
                            self.add_count += 1
                            self.piox = 5.5
                            self.last_o = float(lblShoga1v)
                            self.inp = (self.inp * (abs(self.ExedQty) -1) + float(lblShoga1v)) / abs(self.ExedQty)
                            print('last_o', self.last_o)
                            print('now_prc', float(lblShoga1v))
                            print('add_count', self.add_count)

                # mid peak (dxy_20 orderbook)
                if self.in_str == 1:
                    if self.prf_able == 1 and cvol_s < self.cvol_s_low_act * -1/2 and cvol_t < 0:  # or y1_ss >0:
                        self.profit += ((float(lblBhoga1v) - self.inp) - (
                            float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = 1
                        self.in_str = 0
                        self.OrgMain = 'n'
                        self.turnover += 1
                    if 1==0 and self.prf_hit == 1 and cvol_t < 0 and count_m<self.count_m_deact/2:
                        self.profit += ((float(lblBhoga1v) - self.inp) - (
                            float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = 0.5
                        self.in_str = 0
                        self.OrgMain = 'n'
                        self.turnover += 1
                    if self.sig_2 == -2:
                        self.profit += ((float(lblBhoga1v) - self.inp) - (
                            float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = 1.5
                        self.in_str = 0
                        self.OrgMain = 'n'
                        self.turnover += 10

                #  high peak
                if self.in_str == 2:
                    if cvol_s < self.cvol_s_act * -1 and cvol_t<0 and cvol_c<=17:
                        self.profit += ((float(lblBhoga1v) - self.inp) - (
                                float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = 2
                        self.in_str = 0
                        self.OrgMain = 'n'
                        self.turnover += 1
                    if self.sig_3 == 1:
                        self.profit += ((float(lblBhoga1v) - self.inp) - (
                                float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = 2.5
                        self.in_str = 0
                        self.OrgMain = 'n'
                        self.turnover += 1

                #  after - peak
                if  self.in_str_1 == -1:
                    if cvol_s < 0 and cvol_t < self.cvol_t_act * -1 / 10 :
                        self.profit += ((float(lblBhoga1v) - self.inp) - (
                                float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = 3
                        self.in_str_1 = 0
                        self.OrgMain = 'n'
                        self.turnover += 1

            elif self.OrgMain == "s":

                # trnd_out
                if self.in_str == -1:
                    if self.sig_1 == 1 and count_m > self.count_m_deact:
                        count_cri = self.df[self.nf - 20:self.nf - 1][self.df.dt[self.nf - 20:self.nf - 1]>self.dt_overact].count()[0]
                        if count_cri>3:
                            self.piox = -5
                            self.in_str = 0
                            self.OrgMain = 'n'
                            self.turnover += 1
                        else:
                            if float(lblShoga1v) < self.last_o and abs(self.ExedQty)>1 and self.piox != -4:
                                self.minus_count += 1
                                self.piox = -4
                                self.last_o = float(lblShoga1v)
                                self.inp = (self.inp * (abs(self.ExedQty)) - float(lblShoga1v)) / (abs(self.ExedQty) -1)
                                print('last_o', self.last_o)
                                print('now_prc', float(lblBhoga1v))
                                print('minus_count', self.minus_count)
                    if self.sig_1 == -1 and count_m > self.count_m_deact:
                        if float(lblBhoga1v) > self.last_o + self.tick * 5 and self.piox != -5.5:
                            self.add_count += 1
                            self.piox = -5.5
                            self.last_o = float(lblBhoga1v)
                            self.inp = (self.inp * (abs(self.ExedQty) -1) + float(lblBhoga1v)) / abs(self.ExedQty)
                            print('last_o', self.last_o)
                            print('now_prc', float(lblBhoga1v))
                            print('add_count', self.add_count)

                #  mid peak (dxy_20 orderbook)
                if self.in_str == -1:
                    if self.prf_able == 1 and cvol_s > self.cvol_s_low_act/2  and cvol_t > 0:
                        self.profit += ((self.inp - float(lblBhoga1v)) - (
                                float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = -1
                        self.in_str = 0
                        self.OrgMain = 'n'
                        self.turnover += 1
                    if 1==0 and self.prf_hit == 1 and cvol_t > 0 and count_m < self.count_m_deact / 2:
                        self.profit += ((self.inp - float(lblBhoga1v)) - (
                                float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = -0.5
                        self.in_str = 0
                        self.OrgMain = 'n'
                        self.turnover += 1
                    if self.sig_2 == 2:
                        self.profit += ((self.inp - float(lblBhoga1v)) - (
                                float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = -1.5
                        self.in_str = 0
                        self.OrgMain = 'n'
                        self.turnover += 1

                #  high peak
                if self.in_str == -2:
                    if cvol_s > self.cvol_s_act and cvol_t>0 and cvol_c>=3:
                        self.profit += ((self.inp - float(lblBhoga1v)) - (
                                float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = -2
                        self.in_str = 0
                        self.OrgMain = 'n'
                        self.turnover += 1
                    if self.sig_3 == -1:
                        self.profit += ((self.inp - float(lblBhoga1v)) - (
                                float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = -2.5
                        self.in_str = 0
                        self.OrgMain = 'n'
                        self.turnover += 1

                #  after - peak
                if  self.in_str_1 == 1:
                    if cvol_s > 0 and cvol_t > self.cvol_t_act / 10:
                        self.profit += ((self.inp - float(lblBhoga1v)) - (
                                float(lblBhoga1v) + self.inp) * self.fee_rate) * abs(self.ExedQty)
                        self.piox = -3
                        self.in_str_1 = 0
                        self.OrgMain = 'n'
                        self.turnover += 1

        self.df.at[self.nf, "piox"] = self.piox
        self.df.at[self.nf, "profit"] = self.profit
        self.df.at[self.nf, "add_count"] = self.add_count
        self.df.at[self.nf, "minus_count"] = self.minus_count
        # print 'piox = ', self.piox

        ###############################
        #  // RESET & ETC //
        ###############################

        if self.OrgMain=="b":
            self.d_OMain = 1
            # self.piox = 0
            print('add_count %d  /minus_count %d  /AvePrc %0.2f  /Profit %0.2f' % (self.add_count-1, self.minus_count-1, self.AvePrc, self.profit))
        elif self.OrgMain=="s":
            self.d_OMain = -1
            # self.piox = 0
            print('add_count %d  /minus_count %d  /AvePrc %0.2f  /Profit %0.2f' % (self.add_count-1, self.minus_count-1, self.AvePrc, self.profit))
        elif self.OrgMain == "n":
            self.d_OMain = 0
            self.add_count = 1
            self.minus_count = 1
            self.inp = 0
            self.last_o = 0
            self.AvePrc = 0
            self.ExedQty = 0
            self.nfset = 0
            self.prf_hit = 0
            print('/Profit %0.2f' %  (self.profit))

        if self.piox == 4:
            self.d_OMain = 2
            # print "d_OrgMain", self.d_OMain
        if self.piox == -4:
            self.d_OMain = -2

        if self.piox == 5.5:
            self.d_OMain = 3
            # print "d_OrgMain", self.d_OMain
        if self.piox == -5.5:
            self.d_OMain = -3
            # print "d_OrgMain", self.d_OMain

        self.df.at[self.nf, "d_OMain"] = self.d_OMain
        self.df.at[self.nf, "OrgMain"] = self.OrgMain
        # print "OrgMain", self.OrgMain

        self.nf+=1

        if self.nf>10:
            print (self.df.ix[self.nf-9:self.nf-1,['dt', 'count_m', 'cvol_t', 'cvol_s', 'cvol_c', 'dxy_200_medi', 'sig_1', 'OrgMain', 'inp']]) #
            print ('-----------')

        elap = time.time() - t_start
        self.df.at[self.nf, "elap"] = elap
        print ("elap %0.5f" % (elap))
        print ('-----------')
        return self.d_OMain

    def btnSave_Clicked(self):
        #df.to_sql("Main_DB", con, if_exists='replace', index=True) #, index_label=None, chunksize=None, dtype=None)
        ts = datetime.now().strftime("%m-%d-%H-%M")
        filename = "EDB__%s.csv" %  (ts)
        self.df.to_csv('%s' % filename)  # + time.strftime("%m-%d") + '.csv')
        # print 'Saved'

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

