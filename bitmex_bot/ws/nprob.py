import time
import pandas as pd
import scipy.stats as stat
from sklearn import datasets, linear_model
import matplotlib.pyplot as plt

class Nprob:

    def __init__(self):
        # global df , nf
        self.nf=1
        self.nfset=0
        self.startime=time.time()
        self.OrgMain='n'
        self.cri=0
        self.cri_r=0
        # print 'init Nprob', self.nf
        # a = pd.read_csv("index_bot.csv").columns.values.tolist()
        # self.df = pd.DataFrame()
        # self.df = pd.DataFrame(index=range(0, 1), columns=a)
        # print self.df

    def nprob(self, price, timestamp, mt, cgubun_sum, cvolume_sum, volume,  lblSqty2v, lblShoga2v, lblSqty1v, lblShoga1v, lblBqty1v, lblBhoga1v, lblBqty2v, lblBhoga2v):
        # global nf, df, nfset, OrgMain, nowtime

        print 'nf : ', self.nf
        nowtime=time.time()

        # if self.nf==250:
        #     self.btnPlot_Clicked()

        regr = linear_model.LinearRegression()

        self.df.at[self.nf, "price"] = price
        self.df.at[self.nf, "cgubun"] = cgubun_sum
        self.df.at[self.nf, "cvolume"] = cvolume_sum
        self.df.at[self.nf, "volume"] = volume
        self.df.at[self.nf, "y2"] = int(lblSqty2v)
        self.df.at[self.nf, "py2"] = float(lblShoga2v)
        self.df.at[self.nf, "y1"] = int(lblSqty1v)
        self.df.at[self.nf, "py1"] = float(lblShoga1v)
        self.df.at[self.nf, "x1"] = int(lblBqty1v)
        self.df.at[self.nf, "px1"] = float(lblBhoga1v)
        self.df.at[self.nf, "x2"] = int(lblBqty2v)
        self.df.at[self.nf, "px2"] = float(lblBhoga2v)

        # trd_off
        if self.nf < 3:
            trdoff = 0
        if self.nf >= 3:
            trdoff = int(volume) - int(self.df.ix[self.nf - 1, "volume"])
        self.df.at[self.nf, "trdoff"] = trdoff

        # xnet, ynet
        if self.nf < 2:
            dx1 = 0
            dy1 = 0
            cvol = int(cvolume_sum)
        if self.nf >= 2:
            print 'cvolume_sum', cvolume_sum
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
            # print dx1,dy1

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
        if self.nf == 1:
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
        # print('sXY', sXY)

        # sXY_max_min
        # if self.nf >= 505:
        #     sXY_series=self.df.ix[self.nf - 500:self.nf - 1, "sXY"]
        #     idmax_sXY = sXY_series.values.argmax()+self.nf-500
        #     idmin_sXY = sXY_series.values.argmin()+self.nf-500
        #     # print('sXY_id', idmax_sXY, idmin_sXY)
        #     if idmax_sXY > idmin_sXY:
        #         sXY_m = (5 * self.df.ix[idmax_sXY, "sXY"] + self.df.ix[idmin_sXY, "sXY"]) / 6
        #     else:
        #         sXY_m = (self.df.ix[idmax_sXY, "sXY"] + 5 * self.df.ix[idmin_sXY, "sXY"]) / 6
        # else:
        #     sXY_m = 0
        #
        # self.df.at[self.nf, "sXY_m"] = sXY_m

        # # sXY_ox
        # if self.nf >= 505:
        #
        #     d_sXY=self.df.ix[idmax_sXY, "sXY"] - self.df.ix[idmin_sXY, "sXY"]
        #     self.df.at[self.nf, "dXY"] = d_sXY
        #
        #     if d_sXY>1700:
        #         if sXY > sXY_m:
        #             sXY_ox = 1
        #         else:
        #             sXY_ox = 0
        #     else:
        #         sXY_ox = 0.5
        # else:
        #     sXY_ox = 0.5
        # self.df.at[self.nf, "sXY_ox"] = sXY_ox
        #
        # # sXY_bns
        # if self.nf >= 525:
        #     # if sXY_bns==0:
        #     if self.df.ix[self.nf - 100:self.nf - 1, "sXY_ox"].sum() >= 80:
        #         sXY_bns = 1
        #     elif self.df.ix[self.nf - 100:self.nf - 1, "sXY_ox"].sum() < 20:
        #         sXY_bns = 0
        #     else:
        #         sXY_bns = 0.5
        # else:
        #     sXY_bns=0.5
        # self.df.at[self.nf, "sXY_bns"] = sXY_bns

        #stime
        if self.nf == 1:
            print("startime", self.startime)
        self.df.at[self.nf, "stime"] = timestamp #nowtime
        # print 'stime', timestamp/1000

        # dt
        if self.nf < 2:
            dt = 0
        if self.nf >= 2:
            dt = (timestamp - self.df.ix[self.nf - 1, "stime"])/1000
            if dt==0:
                dt = 0.5
        self.df.at[self.nf, "dt"] = dt
        print 'dt', dt

        # mt
        if 1==0:
            if self.nf < 15:
                mtv = 0
            if self.nf >= 15:
                mtv = self.df.ix[self.nf - 10:self.nf - 1, "dt"].mean()
            self.df.at[self.nf, "mt"] = mtv
        if 1==1:
            self.df.at[self.nf, "mt"] = mt

        # mtm
        if self.nf < 102:
            mtm = 0
        if self.nf >= 102:
            mtm = self.df.ix[self.nf - 100:self.nf - 1, "dt"].mean()
        self.df.at[self.nf, "mtm"] = mtm

        # ns
        lastime = nowtime - 20

        if nowtime <= self.startime + 21:
            ns = 0
        if nowtime > self.startime + 21:
            if self.nf >= 1005:
                dfs = self.df[self.nf - 1000:self.nf - 1]
            else:
                dfs = self.df[0:self.nf - 1]
            try:
                ns = max(dfs[(dfs['stime'] <= lastime)].index.tolist())
            except:
                ns = self.nf-1

        self.df.at[self.nf, "ns"] = ns

        # nsf
        if ns == 0:
            nsf = 0
        if ns != 0:
            nsf = self.nf - ns
        self.df.at[self.nf, "nsf"] = nsf


        # Wilcoxon Test

        if ns != 0 & ns != (self.nf - 7) & self.nf > 20:
            y1_sX = self.df.ix[ns:self.nf - 1, "sX"]
            y2_sX = self.df.ix[self.nf - 7:self.nf - 1, "sX"]
            try:
                if y1_sX.equals(y2_sX) == 1:
                    wc_sX = 50
                else:
                    u, wc_sX = stat.mannwhitfneyu(y1_sX, y2_sX)
                    if y2_sX.mean() >= y1_sX.mean():
                        wc_sX = 50 + (0.5 - wc_sX) * 100
                    else:
                        wc_sX = 50 - (0.5 - wc_sX) * 100
            except:
                wc_sX = 50

            y1_sY = self.df.ix[ns:self.nf - 1, "sY"]
            y2_sY = self.df.ix[self.nf - 7:self.nf - 1, "sY"]
            try:
                if y1_sY.equals(y2_sY) == 1:
                    wc_sY = 50
                else:  # if y1_sY.equals(y2_sY)!=1:
                    u, wc_sY = stat.mannwhitneyu(y1_sY, y2_sY)
                    if y2_sY.mean() >= y1_sY.mean():
                        wc_sY = 50 + (0.5 - wc_sY) * 100
                    else:
                        wc_sY = 50 - (0.5 - wc_sY) * 100
            except:
                wc_sY = 50

            y1_sXY = self.df.ix[ns:self.nf - 1, "sXY"]
            y2_sXY = self.df.ix[self.nf - 7:self.nf - 1, "sXY"]
            try:
                if y1_sXY.equals(y2_sXY) == 1:
                    wc_sXY = 50
                else:  # if y1_sXY.equals(y2_sXY)!=1:
                    u, wc_sXY = stat.mannwhitneyu(y1_sXY, y2_sXY)
                    if y2_sXY.mean() >= y1_sXY.mean():
                        wc_sXY = 50 + (0.5 - wc_sXY) * 100
                    else:
                        wc_sXY = 50 - (0.5 - wc_sXY) * 100
            except:
                wc_sXY = 50

            if self.nf>355:
                y1_sXY_l = self.df.ix[self.nf - 350:self.nf - 1, "sXY"]
                y2_sXY_l = self.df.ix[self.nf-50:self.nf - 1, "sXY"]
                try:
                    if y1_sXY_l.equals(y2_sXY_l) == 1:
                        wc_sXY_l = 50
                    else:  # if y1_sXY.equals(y2_sXY)!=1:
                        u, wc_sXY_l = stat.mannwhitneyu(y1_sXY_l, y2_sXY_l)
                        if y2_sXY_l.mean() >= y1_sXY_l.mean():
                            wc_sXY_l = 50 + (0.5 - wc_sXY_l) * 100
                        else:
                            wc_sXY_l = 50 - (0.5 - wc_sXY_l) * 100
                except:
                    wc_sXY_l = 50
            else:
                wc_sXY_l = 50

        else:
            wc_sX = 50
            wc_sY = 50
            wc_sXY = 50
            wc_sXY_l = 50

        self.df.at[self.nf, "PX"] = wc_sX
        self.df.at[self.nf, "PY"] = wc_sY
        self.df.at[self.nf, "PXY"] = wc_sXY
        self.df.at[self.nf, "PXY_l"] = wc_sXY_l

        # PXYm
        if self.nf >= 102:
            PXYm = self.df.ix[self.nf - 30:self.nf - 1, "PXY"].mean()
        else:
            PXYm = 0
        self.df.at[self.nf, "PXYm"] = PXYm

        # nPX, nPY
        if self.nf < 50:
            nPX = 0
            nPY = 0
        if self.nf >= 50:
            nPX = float(3*self.df.ix[self.nf - 30:self.nf - 1, "x1"].mean() + self.df.ix[self.nf - 30:self.nf - 1, "x2"].mean()) / 4
            nPY = float(3*self.df.ix[self.nf - 30:self.nf - 1, "y1"].mean() + self.df.ix[self.nf - 30:self.nf - 1, "y2"].mean()) / 4

        nPXY = float(nPX + nPY) / 2
        self.df.at[self.nf, "nPXY"] = nPXY

        # stXY
        if self.nf < 55:
            stXY = 0
        if self.nf >= 55:
            stXY = self.df.ix[self.nf - 50:self.nf - 1, "sXY"].std()
        self.df.at[self.nf, "stXY"] = stXY

        # stPXY
        if self.nf >= 102 and ns < self.nf - 1:
            stPXY = self.df.ix[ns:self.nf - 1, "PXY"].std()
        else:
            stPXY = 0
        self.df.at[self.nf, "stPXY"] = stPXY

        # ststPXY
        if self.nf >= 602:
            ststPXY = self.df.ix[self.nf - 500:self.nf - 1, "stPXY"].std()
        else:
            ststPXY = 0
        self.df.at[self.nf, "ststPXY"] = ststPXY

        # PINDEX
        if self.nf < 102:
            pi1 = 0
            pi2 = 0
            pindex = 0
        if self.nf >= 102:
            try:
                pi1 = float(wc_sXY - 50) / 50
                if stPXY != 0:
                    pi2 =  float(stat.norm.ppf((100 - stPXY) / 100)) / 2.5
                else:
                    pi2 = 1
                try:
                    normxy = stat.norm.ppf( float(wc_sXY) / 100)
                except:
                    normxy = 0
                try:
                    normx = stat.norm.ppf(float(wc_sX) / 100)
                except:
                    normx = 0
                try:
                    normy = stat.norm.ppf(float(wc_sY) / 100)
                except:
                    normy = 0
                pindex = 50 + 50 * normxy / float(2.5) * abs(normx - normy) / float(5) + 12.5 * pi1 * pi2
            except:
                pindex = 50

        self.df.at[self.nf, "pindex"] = pindex

        # PINDEX2
        if self.nf < 102:
            pindex2 = 0
        if self.nf >= 102:
            pindex2 = self.df.ix[self.nf - 100:self.nf - 1, "pindex"].mean()
        self.df.at[self.nf, "pindex2"] = pindex2

    # Extension
        if 1== 1:

            # BUMP

            # aa
            if self.nf >= 55:
                aa = (self.df.ix[self.nf - 5:self.nf - 1, "stXY"].mean() / float(150) ) ** 0.5
            else:
                aa = 1
            self.df.at[self.nf, "aa_trd"] = aa

            # bb
            if self.nf >= 55:
                bb = float(lblBhoga1v) / 10000
            else:
                bb = 1
            self.df.at[self.nf, "bb_prc"] = bb

            # cc
            cc=1
            if self.nf >= 55 and self.df.ix[self.nf - 1, "pindex"]!=0:
                c1 = self.df.ix[self.nf - 20:self.nf - 1, "pindex"].mean()
                if c1 >= 50:
                    cc = (1 + 2 * (c1 - 50) / float(50)) ** 0.5
                if c1 < 50:
                    cc = (1 - 2 * (c1 - 50) / float(50)) ** 0.5
            else:
                cc = 1
            self.df.at[self.nf, "cc_pid"] = cc

            # dd
            if self.nf >= 55 and stPXY != 0:
                d1 = stPXY
                if d1 <= 50:
                    dd = 1 + stat.norm.ppf((100 - d1) / float(100)) ** 0.6
                if d1 > 50:
                    dd = 1 + stat.norm.ppf((100 - 49.999) / float(100)) ** 0.6
            else:
                dd = 1
            self.df.at[self.nf, "dd_sWC"] = dd

            # ee
            if self.nf >= 55:
                # e1 = mtv
                if mtv <= 0.5:
                    ee_mt = 1 + stat.norm.ppf(1*(1000 - mtv) / float(1)) ** 1
                if mtv > 0.5:
                    ee_mt = 1
            else:
                ee_mt = 1
            self.df.at[self.nf, "ee_mt"] = ee_mt

            c1 = range(0, 750, 50)
            c2 = range(0, 3000, 100)

            # ee_s
            if self.nf >= 255:
                ee_s = self.df.ix[self.nf - 200:self.nf, "ee_mt"].mean()
            else:
                ee_s = 1
            self.df.at[self.nf, "ee_s"] = ee_s

            # ee_s_ave
            if self.nf >= 1200:
                ee_s_ave = self.df.ix[self.nf - 750:self.nf, "ee_s"].iloc[c1].mean()
            else:
                ee_s_ave = 1
            self.df.at[self.nf, "ee_s_ave"] = ee_s_ave

            # ee_s_ave_long
            if self.nf >= 3200:
                ee_s_ave_long = self.df.ix[self.nf - 3000:self.nf, "ee_s"].iloc[c2].mean()
            else:
                ee_s_ave_long = 1
            self.df.at[self.nf, "ee_s_ave_long"] = ee_s_ave_long

            # ee_s_max_min
            if self.nf >= 825:
                ee_s_series=self.df.ix[self.nf - 500:self.nf-1, "ee_s"]
                idmax = ee_s_series.values.argmax()+self.nf-500
                idmin = ee_s_series.values.argmin()+self.nf-500
                if idmax>idmin:
                    ee_s_m = (3*self.df.ix[idmax, "ee_s"]+self.df.ix[idmin, "ee_s"])/4
                else:
                    ee_s_m = (self.df.ix[idmax, "ee_s"] + 3*self.df.ix[idmin, "ee_s"]) / 4
            else:
                ee_s_m = 1
            self.df.at[self.nf, "ee_s_m"] = ee_s_m

            # ee_s slope(mtv-slope * -1 conversion)
            if self.nf >= 515:
                ee_s_y = self.df.ix[self.nf - 500:self.nf - 1, "ee_s"]
                ee_s_x = self.df.ix[self.nf - 500:self.nf - 1, "nf"]
                print ee_s_y
                ee_s_slope = regr.fit(ee_s_y.values.reshape(-1, 1), ee_s_x.values.reshape(-1, 1)).coef_[0][0]
                print ee_s_slope
            else:
                ee_s_slope=0
            self.df.at[self.nf, "ee_s_slope"] = ee_s_slope

            # ee_s_ox
            if self.nf >= 525:
                ee_s_ox = 0
                if ee_s_slope>0:
                        if ee_s > ee_s_m and ee_s>1.6:
                            ee_s_ox = 1
                        if ee_s>2 and ee_s_m>2:
                            ee_s_ox = 1
            else:
                ee_s_ox = 0
            self.df.at[self.nf, "ee_s_ox"] = ee_s_ox

            # bum_sum
            if self.nf >= 50:
                bump = 1 * (abs(aa * bb * cc * dd * ee_mt)) ** 0.5
            else:
                bump = 0
            self.df.at[self.nf, "bump"] = bump

            # bumpm
            if self.nf >= 50:
                bumpm = self.df.ix[self.nf - 40:self.nf, "bump"].mean()
            else:
                bumpm = 0
            self.df.at[self.nf, "bumpm"] = bumpm

            # abump
            if self.nf >= 50:
                abump = 20 * (bump / float(20) + 0.2 * stPXY / float(100)) / 1.2
            else:
                abump = 0
            self.df.at[self.nf, "abump"] = abump

            # abumpm
            if self.nf >= 50:
                abumpm = self.df.ix[self.nf - 40:self.nf, "abump"].mean()
            else:
                abumpm = 0
            self.df.at[self.nf, "abumpm"] = abumpm

            # apindex
            if self.nf >= 505:
                c = range(0, 500, 5)
                ry = self.df.ix[self.nf - 500:self.nf - 1, "sXY"].iloc[c]
                rx = self.df.ix[self.nf - 500:self.nf - 1, "stime"].iloc[c]
                slope = regr.fit(rx.values.reshape(-1, 1), ry.values.reshape(-1, 1)).coef_[0][0]
            else:
                slope = 0
                p_value = 0
                std_err = 0
            self.df.at[self.nf, "apindex_s"] = slope

        # s1
        if self.nf >= 50:
            if self.nfset < self.nf and self.nfset != 0:
                s1 = sXY - self.df.ix[self.nfset, "sXY"]
            else:
                s1 = 0
        else:
            s1 = 0
        self.df.at[self.nf, "s1"] = s1

        # s2_s
        if self.nf >= 50:
            if ns < self.nf-2:
                s2_s = 3.873 * self.df.ix[ns:self.nf, "sXY"].std() / float(nPXY)
            else:
                s2_s = self.df.ix[self.nf-1, "s2_s"]
        else:
            s2_s = 0
        self.df.at[self.nf, "s2_s"] = s2_s

        # s2_s_mean
        if self.nf >= 150: # and ns < self.nf-2:
            s2_s_m = self.df.ix[self.nf - 100:self.nf, "s2_s"].mean()
        else:
            s2_s_m = 0
        self.df.at[self.nf, "s2_s"] = s2_s

        # s3_x, s3_y
        span = 30
        if self.nf >= 105:
            s3_x = self.df.ix[self.nf - span:self.nf-1, "dx1"].mean() - self.df.ix[self.nf - span:self.nf-1, "dyy"].mean() + self.df.ix[self.nf - span:self.nf-1, "dy1"].mean()
            s3_y = self.df.ix[self.nf - span:self.nf-1, "dy1"].mean() - self.df.ix[self.nf - span:self.nf-1, "dxx"].mean() + self.df.ix[self.nf - span:self.nf-1, "dx1"].mean()
        else:
            s3_x = 0
            s3_y = 0
        self.df.at[self.nf, "s3_x"] = s3_x
        self.df.at[self.nf, "s3_y"] = s3_y

        # s3
        if self.nf >= 105:
            s3 = s3_x - s3_y
        else:
            s3 = 0
        self.df.at[self.nf, "s3"] = s3

        #s3_m_m
        if self.nf >= 305:
            s3_m_m = (self.df.ix[self.nf - 100:self.nf - 1, "s3"].max() + self.df.ix[self.nf - 100:self.nf - 1, "s3"].min()) / 2
        else:
            s3_m_m=0
        self.df.at[self.nf, "s3_m_m"] = s3_m_m

        #s3_mean
        if self.nf >= 305:
            s3_m= self.df.ix[self.nf - 300:self.nf-1, "s3"].mean()
        else:
            s3_m=0
        self.df.at[self.nf, "s3_m"] = s3_m

        #s3_mean_short
        if self.nf >= 155:
            s3_m_short = self.df.ix[self.nf - 50:self.nf - 1, "s3"].mean()
        else:
            s3_m_short=0
        self.df.at[self.nf, "s3_m_short"] = s3_m_short

        # s7
        elst=1
        if PXYm >= 60:
            adj_s2 = 1
        elif PXYm <= 40:
            adj_s2 = -1
        else:
            adj_s2 = 0
        if nPXY != 0:
            if self.OrgMain == "b":
                s7 = 4 + self.df.ix[self.nf - 1, "s1"] * elst / float(nPY) + stXY * adj_s2 / float(nPY)
            elif self.OrgMain == "s":
                s7 = 4 - self.df.ix[self.nf - 1, "s1"] * elst / float(nPX) - stXY * adj_s2 / float(nPX)
            elif self.OrgMain == "n":
                s7 = 4 + stXY / float(nPXY)
        else:
            s7 = 0
        self.df.at[self.nf, "s7"] = s7

        ###############################

        # hit_peak setting
        pi1_ = 10
        s3m_ = 3  # (s3_m)
        s3_ = 10  # (s3)
        s2sm_ = 3
        ees_ = 0
        s3_x_ = 2
        s3_y_ = 2

        org_in_1 = 0
        org_in_2 = 0
        org_in_3 = 0

        # dt_main
        if self.nf > 250 :
            dt_main_1=0
            if s3>6.7 and slope>-1:
                dt_main_1= 1
            if s3<-4.5 and slope<-0.5:
                dt_main_1= -1
        else:
            dt_main_1 = 0
        self.df.at[self.nf, "dt_main_1"] = dt_main_1

        if self.nf > 250 :
            dt_main_2 = 0
            if slope > 0 and s3 > 0 and dt < 0.15:
                dt_main_2 = 1
            if slope < 0 and s3 < 0 and dt < 0.15:
                dt_main_2 = -1
        else:
            dt_main_2 = 0
        self.df.at[self.nf, "dt_main_2"] = dt_main_2

        # dt_sum
        if self.nf > 500:
            dt_sum_1 = self.df.ix[self.nf - 250:self.nf-1, "dt_main_1"].mean()
        else:
            dt_sum_1=0
        self.df.at[self.nf, "dt_sum_1"] = dt_sum_1

        if self.nf > 500:
            dt_sum_2 = self.df.ix[self.nf - 250:self.nf-1, "dt_main_2"].mean()
        else:
            dt_sum_2=0
        self.df.at[self.nf, "dt_sum_2"] = dt_sum_2

        ###############################
        #  IN Strategy
        if  self.nf<250:
            self.cri=0
            self.cri_r=1

        if self.nf > 250 and s3_m != 0:
            print ('s2_s, dt, wc_sXY_l, wc_sXY, s3_x, s3_y :', round(s2_s,2), round(dt,2), round(wc_sXY_l,2), round(wc_sXY,2), round(s3_x,2), round(s3_y,2))
            if s2_s > 0.5 and dt < 1:
                if wc_sXY_l > 40 and wc_sXY>99 and s3_x > 3+s3_x_ and s3_y < 0:
                    org_in_2 = 1
                if wc_sXY_l < 60  and wc_sXY<1 and s3_y > 3+s3_y_ and s3_x < 0:
                    org_in_2 = -1
            # Out Signal
            print ('cri, cri_r, s3_m, s3_m_short :', round(self.cri,2), round(self.cri_r,2), round(s3_m,2), round(s3_m_short,2))
            if self.cri > 0 and self.cri_r > 1 and s3_m > 0 and s3_m_short > 0:
                if org_in_2 == 1:
                    org_in_2 = 3
                elif org_in_2 != 1:
                    org_in_2 = 2
            if self.cri < 0 and self.cri_r < 1 and s3_m < 0 and s3_m_short < 0:
                if org_in_2 == -1:
                    org_in_2 = -3
                elif org_in_2 != -1:
                    org_in_2 = -2

        if org_in_2 == 1 or org_in_2 == 3:
            self.cri = self.cri + 1
        if org_in_2 == -1 or org_in_2 == -3:
            self.cri = self.cri - 1
        if self.cri>5:
            self.cri=5
        if self.cri<-5:
            self.cri=-5

        #cri_r
        if self.nf > 250:

            if ee_s>=1.8 and ee_s<2.2:
                len_cri_r = int(500 + (ee_s-1.8) * 1250)
            if ee_s>=2.2:
                len_cri_r = 1000
            if ee_s<1.8:
                len_cri_r = 500

            df_r = self.df.ix[self.nf - min(self.nf,len_cri_r):self.nf - 1, "org_in_2"]
            df_r_y = df_r[df_r < 0].count()
            df_r_x = df_r[df_r > 0].count()
            if df_r_y!=0:
                self.cri_r = float(df_r_x)/df_r_y
                if self.cri_r>2:
                    self.cri_r=2
            else:
                if df_r_x!=0:
                    self.cri_r=2
                else:
                    self.cri_r=1
        else:
            self.cri_r=1

        self.df.at[self.nf, "cri"] = self.cri
        self.df.at[self.nf, "cri_r"] = self.cri_r

        # ee_s * cri
        if self.nf>=222:
            cri_ee_s = self.cri * ee_s
        else:
            cri_ee_s = 0
        self.df.at[self.nf, "cri_ee_s"] = cri_ee_s

        # In Decision
        if self.nf > 250 :
            if ee_s > 1.7 and ee_s_ave > 1.4 and ee_s >= ee_s_ave:
                if slope > 2.5 and dt_sum_2 > 0:
                    if self.cri_r > 1 and self.cri > -3 and self.df.ix[self.nf - 1, "cri"] >= self.df.ix[self.nf - 2, "cri"]:
                        self.OrgMain = "b"
                if slope < -2.5 and dt_sum_2 < 0:
                    if self.cri_r < 1 and self.cri < 3 and self.df.ix[self.nf - 1, "cri"] <= self.df.ix[self.nf - 2, "cri"]:
                        self.OrgMain = "s"

            if ee_s > 1.8 and ee_s_m > 1.5 and ee_s_slope > 0:
                if self.cri_r > 0.5 and self.df.ix[self.nf - 1, "cri_r"] >= self.df.ix[self.nf - 2, "cri_r"]:
                    if self.cri > -3 and self.df.ix[self.nf - 1, "apindex_s"] >= self.df.ix[self.nf - 3, "apindex_s"]:
                        if ee_s_ave > 1.5 and ee_s > ee_s_m:
                            # if sXY_bns == 1:
                            self.OrgMain = "b"
                if self.cri_r < 1.5 and self.df.ix[self.nf - 1, "cri_r"] <= self.df.ix[self.nf - 2, "cri_r"]:
                    if self.cri < 3 and self.df.ix[self.nf - 1, "apindex_s"] <= self.df.ix[self.nf - 3, "apindex_s"]:
                        if ee_s_ave > 1.5 and ee_s > ee_s_m:
                            # if sXY_bns == 0:
                            self.OrgMain = "s"
        if 1 == 0:
            if ee_s > 1.8 and ee_s_m > 1.5 and ee_s_slope > 0:
                if self.cri_r >= 1.8 and self.cri == 5:
                    self.OrgMain = "b"
                if self.cri_r <= 0.2 and self.cri == -5:
                    self.OrgMain = "s"
            self.df.at[self.nf, "org_in_2"] = org_in_2
            self.df.at[self.nf, "org_in_3"] = org_in_3

            # # prf_able
            # prf_able = 0
            # if self.OrgMain == "b" and self.nfset != 0 and self.nfset < self.nf:
            #     inst_p= 4+(o1px1 - inp_o)/float(tick_o)
            #         if o1px1 >= inp_o + tick_o * 2:
            #             prf_able = 1
            #         else:
            #             prf_able = 0

        self.nf+=1
        if self.nf>10:
            print self.df.ix[self.nf-9:self.nf-1,['dt', 'mt', 'cvolume', 'pindex', 'apindex_s', 'ee_s','bumpm','s3']]


    def btnPlot_Clicked(self):
        # global df, nf, a, file_loaded

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
        plt.show()


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
            result = (a - b - d) + W #= W - b + a - d
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

