

def nprob(price, cgubun_sum, cvolume_sum, volume,  lblSqty2v, lblShoga2v, lblSqty1v, lblShoga1v, lblBqty1v, lblBhoga1v, lblBqty2v, lblBhoga2v):
    global nf, df

    # trd_off
    if nf < 3:
        trdoff = 0
    if nf >= 3:
        trdoff = int(volume) - int(df.ix[nf - 1, "volume"])
    df.at[nf, "trdoff"] = trdoff

    # xnet, ynet
    if nf < 2:
        dx1 = 0
        dy1 = 0
        cvol = int(cvolume_sum)
    if nf >= 2:
        py1 = float(lblShoga1v)
        px1 = float(lblBhoga1v)
        cvol = int(cvolume_sum)
        y1 = int(lblSqty1v)
        x1 = int(lblBqty1v)
        y2 = int(lblSqty2v)
        x2 = int(lblBqty2v)
        n1px1 = float(df.ix[nf - 1, "px1"])
        n1py1 = float(df.ix[nf - 1, "py1"])
        n1x1 = int(df.x1[nf - 1])
        n1x2 = int(df.x2[nf - 1])
        n1y1 = int(df.y1[nf - 1])
        n1y2 = int(df.y2[nf - 1])
        dx1 = xnet(px1, n1px1, cvol, cgubun_sum, x1, n1x1, x2, n1x2)
        dy1 = ynet(py1, n1py1, cvol, cgubun_sum, y1, n1y1, y2, n1y2)

    df.at[nf, "dy1"] = dy1
    df.at[nf, "dx1"] = dx1

    # dxx, dyy, dxy
    if cgubun_sum == "+":
        wx = 0
        wy = cvol
        cgu = 1
    elif cgubun_sum == "-":
        wx = cvol
        wy = 0
        cgu = -1
    else:
        wx = 0
        wy = 0
        print("gubun error @ ", nf)

    dxx = dx1 + wy
    dyy = dy1 + wx
    dxy = dxx - dyy
    df.at[nf, "dxx"] = dxx
    df.at[nf, "dyy"] = dyy
    df.at[nf, "dxy"] = dxy

    # sX, sY, sXY
    if nf == 0:
        sX = 0
        sY = 0
        sXY = 0
    else:
        sX = df.ix[nf - 1, "sX"] + dxx
        sY = df.ix[nf - 1, "sY"] + dyy
        sXY = df.ix[nf - 1, "sXY"] + dxy

    df.at[nf, "sX"] = sX
    df.at[nf, "sY"] = sY
    df.at[nf, "sXY"] = sXY

    # sXY_max_min
    if nf >= 505:
        sXY_series=df.ix[nf - 500:nf - 1, "sXY"]
        idmax_sXY = sXY_series.values.argmax()+nf-500
        idmin_sXY = sXY_series.values.argmin()+nf-500
        # print('sXY_id', idmax_sXY, idmin_sXY)
        if idmax_sXY > idmin_sXY:
            sXY_m = (5 * df.ix[idmax_sXY, "sXY"] + df.ix[idmin_sXY, "sXY"]) / 6
        else:
            sXY_m = (df.ix[idmax_sXY, "sXY"] + 5 * df.ix[idmin_sXY, "sXY"]) / 6
    else:
        sXY_m = 0

    df.at[nf, "sXY_m"] = sXY_m

    # sXY_ox
    if nf >= 505:

        d_sXY=df.ix[idmax_sXY, "sXY"] - df.ix[idmin_sXY, "sXY"]
        df.at[nf, "dXY"] = d_sXY

        if d_sXY>1700:
            if sXY > sXY_m:
                sXY_ox = 1
            else:
                sXY_ox = 0
        else:
            sXY_ox = 0.5
    else:
        sXY_ox = 0.5
    df.at[nf, "sXY_ox"] = sXY_ox

    # sXY_bns
    if nf >= 525:
        # if sXY_bns==0:
        if df.ix[nf - 100:nf - 1, "sXY_ox"].sum() >= 80:
            sXY_bns = 1
        # elif sXY_bns==1:
        elif df.ix[nf - 100:nf - 1, "sXY_ox"].sum() < 20:
            sXY_bns = 0
    # else:
        else:
            sXY_bns = 0.5
    else:
        sXY_bns=0.5
    df.at[nf, "sXY_bns"] = sXY_bns

    # maxp,minp,maxxy,minxy
    if OrgMain != "n" and nfset < nf and nfset != 0:
        if maxxy==0:
            maxxy=sXY
        else:
            if maxxy<sXY:
                maxxy = sXY
        if minxy==0:
            minxy=sXY
        else:
            if minxy>sXY:
                minxy = sXY
    else:
        maxxy = 0
        minxy = 0

    #stime
    if nf == 0:
        startime = nowtime
        chktime = nowtime
        diff=0
        print("startime", startime)
    df.at[nf, "stime"] = nowtime

    # dt
    if nf < 2:
        dt = 0
    if nf >= 2:
        dt = nowtime - df.ix[nf - 1, "stime"]
    # df_inst.ix[nf, "dt"] = dt
    df.at[nf, "dt"] = dt

    # mt
    if nf < 15:
        mtv = 0
    if nf >= 15:
        mtv = df.ix[nf - 10:nf - 1, "dt"].mean()
    df.at[nf, "mt"] = mtv

    # mtm
    if nf < 102:
        mtm = 0
        mtm_t = 0
    if nf >= 102:
        mtm = df.ix[nf - 100:nf - 1, "dt"].mean()
    df.at[nf, "mtm"] = mtm

    # ns
    lastime = nowtime - 20

    if nowtime <= startime + 21:
        ns = 0
    if nowtime > startime + 21:
        if nf >= 1005:
            dfs = df[nf - 1000:nf - 1]
        else:
            dfs = df[0:nf - 1]
        try:
            ns = max(dfs[(dfs['stime'] <= lastime)].index.tolist())
        except:
            ns = nf-1 #int(mean(df.ix[nf-1, "ns"], nf-1))

    df.at[nf, "ns"] = ns

    # nsf
    if ns == 0:
        nsf = 0
    if ns != 0:
        nsf = nf - ns
    df.at[nf, "nsf"] = nsf


    # Wilcoxon Test

    if ns != 0 & ns != (nf - 7) & nf > 20:
        y1_sX = df.ix[ns:nf - 1, "sX"]
        y2_sX = df.ix[nf - 7:nf - 1, "sX"]
        try:
            if y1_sX.equals(y2_sX) == 1:
                wc_sX = 50
            else:  # if y1_sX.equals(y2_sX)!=1:
                u, wc_sX = stat.mannwhitneyu(y1_sX, y2_sX)
                if y2_sX.mean() >= y1_sX.mean():
                    wc_sX = 50 + (0.5 - wc_sX) * 100
                else:
                    wc_sX = 50 - (0.5 - wc_sX) * 100
        except:
            wc_sX = 50

        y1_sY = df.ix[ns:nf - 1, "sY"]
        y2_sY = df.ix[nf - 7:nf - 1, "sY"]
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

        y1_sXY = df.ix[ns:nf - 1, "sXY"]
        y2_sXY = df.ix[nf - 7:nf - 1, "sXY"]
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

        if nf>355:
            y1_sXY_l = df.ix[nf - 350:nf - 1, "sXY"]
            y2_sXY_l = df.ix[nf-50:nf - 1, "sXY"]
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

    df.at[nf, "PX"] = wc_sX
    df.at[nf, "PY"] = wc_sY
    df.at[nf, "PXY"] = wc_sXY
    df.at[nf, "PXY_l"] = wc_sXY_l

    # PXYm
    if nf >= 102:
        PXYm = df.ix[nf - 30:nf - 1, "PXY"].mean()
    else:
        PXYm = 0
    df.at[nf, "PXYm"] = PXYm

    # nPX, nPY
    if nf < 50:
        nPX = 0
        nPY = 0
    if nf >= 50:
        nPX = float(3*df.ix[nf - 30:nf - 1, "x1"].mean() + df.ix[nf - 30:nf - 1, "x2"].mean()) / 4
        nPY = float(3*df.ix[nf - 30:nf - 1, "y1"].mean() + df.ix[nf - 30:nf - 1, "y2"].mean()) / 4

    nPXY = float(nPX + nPY) / 2
    df.at[nf, "nPXY"] = nPXY

    # stXY
    if nf < 55:
        stXY = 0
    if nf >= 55:
        stXY = df.ix[nf - 50:nf - 1, "sXY"].std()
    df.at[nf, "stXY"] = stXY

    # stPXY
    if nf >= 102 and ns < nf - 1:
        stPXY = df.ix[ns:nf - 1, "PXY"].std()
    else:
        stPXY = 0
    df.at[nf, "stPXY"] = stPXY

    # ststPXY
    if nf >= 602:
        ststPXY = df.ix[nf - 500:nf - 1, "stPXY"].std()
    else:
        ststPXY = 0
    df.at[nf, "ststPXY"] = ststPXY

    # PINDEX
    if nf < 102:
        pi1 = 0
        pi2 = 0
        pindex = 0
    if nf >= 102:
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

    df.at[nf, "pindex"] = pindex

    # PINDEX2
    if nf < 102:
        pindex2 = 0
    if nf >= 102:
        pindex2 = df.ix[nf - 100:nf - 1, "pindex"].mean()
    df.at[nf, "pindex2"] = pindex2

# Extension
    if 1== 1:

        # BUMP

        # aa
        if nf >= 55:
            aa = (df.ix[nf - 5:nf - 1, "stXY"].mean() / float(150) ) ** 0.5
        else:
            aa = 1
        df.at[nf, "aa_trd"] = aa

        # bb
        if nf >= 55:
            bb = float(lblBhoga1v) / 10000
        else:
            bb = 1
        df.at[nf, "bb_prc"] = bb

        # cc
        cc=1
        if nf >= 55 and df.ix[nf - 1, "pindex"]!=0:
            c1 = df.ix[nf - 20:nf - 1, "pindex"].mean()
            if c1 >= 50:
                cc = (1 + 2 * (c1 - 50) / float(50)) ** 0.5
            if c1 < 50:
                cc = (1 - 2 * (c1 - 50) / float(50)) ** 0.5
        else:
            cc = 1
        df.at[nf, "cc_pid"] = cc

        # dd
        if nf >= 55 and stPXY != 0:
            d1 = stPXY
            if d1 <= 50:
                dd = 1 + stat.norm.ppf((100 - d1) / float(100)) ** 0.6
            if d1 > 50:
                dd = 1 + stat.norm.ppf((100 - 49.999) / float(100)) ** 0.6
        else:
            dd = 1
        df.at[nf, "dd_sWC"] = dd

        # ee
        if nf >= 55:
            # e1 = mtv
            if mtv <= 0.5:
                ee_mt = 1 + stat.norm.ppf(1*(1 - mtv) / float(1)) ** 1
            if mtv > 0.5:
                ee_mt = 1
        else:
            ee_mt = 1
        df.at[nf, "ee_mt"] = ee_mt

        c1 = range(0, 750, 50)
        c2 = range(0, 3000, 100)

        # ee_s
        if nf >= 255:
            ee_s = df.ix[nf - 200:nf, "ee_mt"].mean()
        else:
            ee_s = 1
        df.at[nf, "ee_s"] = ee_s

        # ee_s_ave
        if nf >= 1200:
            ee_s_ave = df.ix[nf - 750:nf, "ee_s"].iloc[c1].mean()
        else:
            ee_s_ave = 1
        df.at[nf, "ee_s_ave"] = ee_s_ave

        # ee_s_ave_long
        if nf >= 3200:
            ee_s_ave_long = df.ix[nf - 3000:nf, "ee_s"].iloc[c2].mean()
        else:
            ee_s_ave_long = 1
        df.at[nf, "ee_s_ave_long"] = ee_s_ave_long

        # ee_s_max_min
        if nf >= 825:
            ee_s_series=df.ix[nf - 500:nf-1, "ee_s"]
            idmax = ee_s_series.values.argmax()+nf-500
            idmin = ee_s_series.values.argmin()+nf-500
            if idmax>idmin:
                ee_s_m = (3*df.ix[idmax, "ee_s"]+df.ix[idmin, "ee_s"])/4
            else:
                ee_s_m = (df.ix[idmax, "ee_s"] + 3*df.ix[idmin, "ee_s"]) / 4
        else:
            ee_s_m = 1
        df.at[nf, "ee_s_m"] = ee_s_m

        # ee_s slope(mtv-slope * -1 conversion)
        if nf >= 755:
            ee_s_y = df.ix[nf - 500:nf - 1, "ee_s_ave"]
            ee_s_x = df.ix[nf - 500:nf - 1, "nf"]
            ee_s_slope = regr.fit(ee_s_y.reshape(-1, 1), ee_s_x.reshape(-1, 1)).coef_[0][0]
        else:
            ee_s_slope=0
        df.at[nf, "ee_s_slope"] = ee_s_slope

        # ee_s_ox
        if nf >= 525:
            ee_s_ox = 0
            if ee_s_slope>0:
                    if ee_s > ee_s_m and ee_s>1.6:
                        ee_s_ox = 1
                    if ee_s>2 and ee_s_m>2:
                        ee_s_ox = 1
        else:
            ee_s_ox = 0
        df.at[nf, "ee_s_ox"] = ee_s_ox

        # bum_sum
        if nf >= 50:
            bump = 1 * (abs(aa * bb * cc * dd * ee_mt)) ** 0.5
        else:
            bump = 0
        df.at[nf, "bump"] = bump

        # bumpm
        if nf >= 50:
            bumpm = df.ix[nf - 40:nf, "bump"].mean()
        else:
            bumpm = 0
        df.at[nf, "bumpm"] = bumpm

        # abump
        if nf >= 50:
            abump = 20 * (bump / float(20) + 0.2 * stPXY / float(100)) / 1.2
        else:
            abump = 0
        df.at[nf, "abump"] = abump

        # abumpm
        if nf >= 50:
            abumpm = df.ix[nf - 40:nf, "abump"].mean()
        else:
            abumpm = 0
        df.at[nf, "abumpm"] = abumpm

        # apindex
        if nf >= 505:
            c = range(0, 500, 5)
            #print("ap-c",c)
            ry = df.ix[nf - 500:nf - 1, "sXY"].iloc[c]
            rx = df.ix[nf - 500:nf - 1, "stime"].iloc[c]
            slope = regr.fit(rx.reshape(-1, 1), ry.reshape(-1, 1)).coef_[0][0]
        else:
            slope = 0
            p_value = 0
            std_err = 0
        df.at[nf, "apindex_s"] = slope

    # s1
    if nf >= 50:
        if nfset < nf and nfset != 0:
            s1 = sXY - df.ix[nfset, "sXY"]
        else:
            s1 = 0
    else:
        s1 = 0
    df.at[nf, "s1"] = s1

    # s2_s
    if nf >= 50:
        if ns < nf-2:
            s2_s = 3.873 * df.ix[ns:nf, "sXY"].std() / float(nPXY)
        else:
            s2_s = df.ix[nf-1, "s2_s"]
    else:
        s2_s = 0
    df.at[nf, "s2_s"] = s2_s

    # s2_s_mean
    if nf >= 150: # and ns < nf-2:
        s2_s_m = df.ix[nf - 100:nf, "s2_s"].mean()
    else:
        s2_s_m = 0
    df.at[nf, "s2_s"] = s2_s

    # s3_x, s3_y
    span = 30
    if nf >= 105:
        s3_x = df.ix[nf - span:nf-1, "dx1"].mean() - df.ix[nf - span:nf-1, "dyy"].mean() + df.ix[nf - span:nf-1, "dy1"].mean()
        s3_y = df.ix[nf - span:nf-1, "dy1"].mean() - df.ix[nf - span:nf-1, "dxx"].mean() + df.ix[nf - span:nf-1, "dx1"].mean()
    else:
        s3_x = 0
        s3_y = 0
    df.at[nf, "s3_x"] = s3_x
    df.at[nf, "s3_y"] = s3_y

    # s3
    if nf >= 105:
        s3 = s3_x - s3_y
    else:
        s3 = 0
    df.at[nf, "s3"] = s3

    #s3_m_m
    if nf >= 305:
        s3_m_m = (df.ix[nf - 100:nf - 1, "s3"].max() + df.ix[nf - 100:nf - 1, "s3"].min()) / 2
    else:
        s3_m_m=0
    df.at[nf, "s3_m_m"] = s3_m_m

    #s3_mean
    if nf >= 305:
        s3_m= df.ix[nf - 300:nf-1, "s3"].mean()
    else:
        s3_m=0
    df.at[nf, "s3_m"] = s3_m

    #s3_mean_short
    if nf >= 155:
        s3_m_short = df.ix[nf - 50:nf - 1, "s3"].mean()
    else:
        s3_m_short=0
    df.at[nf, "s3_m_short"] = s3_m_short

    # s7
    elst=1

    if nPXY != 0:
        if OrgMain == "b":
            s7 = 4 + df.ix[nf - 1, "s1"] * elst / float(nPY) + stXY * adj_s2 / float(nPY)
        elif OrgMain == "s":
            s7 = 4 - df.ix[nf - 1, "s1"] * elst / float(nPX) - stXY * adj_s2 / float(nPX)
        elif OrgMain == "n":
            s7 = 4 + stXY / float(nPXY)
    else:
        s7 = 0
    df.at[nf, "s7"] = s7

    ###############################

    # hit_peak setting
    if dome_ab == 0:
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

        # DT 진입여부
        if nf > 250 :
            dt_main_1=0
            if s3>6.7 and slope>-1:
                dt_main_1= 1
            if s3<-4.5 and slope<-0.5:
                dt_main_1= -1
        else:
            dt_main_1 = 0
        df.at[nf, "dt_main_1"] = dt_main_1

        if nf > 250 :
            dt_main_2 = 0
            if slope > 0 and s3 > 0 and dt < 0.15:
                dt_main_2 = 1
            if slope < 0 and s3 < 0 and dt < 0.15:
                dt_main_2 = -1
        else:
            dt_main_2 = 0
        df.at[nf, "dt_main_2"] = dt_main_2

        # dt_sum
        if nf > 500:
            dt_sum_1 = df.ix[nf - 250:nf-1, "dt_main_1"].mean()
        else:
            dt_sum_1=0
        df.at[nf, "dt_sum_1"] = dt_sum_1

        if nf > 500:
            dt_sum_2 = df.ix[nf - 250:nf-1, "dt_main_2"].mean()
        else:
            dt_sum_2=0
        df.at[nf, "dt_sum_2"] = dt_sum_2

        # dt_median
        if nf > 300:
            dt_med_1 = (df.ix[nf - 50:nf-1, "dt_main_1"].max()+df.ix[nf - 50:nf-1, "dt_main_1"].min())/2
        else:
            dt_med_1=0
        df.at[nf, "dt_med_1"] = dt_med_1

        if nf > 300:
            dt_med_2 = (df.ix[nf - 50:nf - 1, "dt_main_2"].max() + df.ix[nf - 50:nf - 1, "dt_main_2"].min()) / 2
        else:
            dt_med_2=0
        df.at[nf, "dt_med_2"] = dt_med_2

        ###############################
        #  IN Strategy
        if nf > 250 and s3_m != 0:
            print ('s2_s, dt, wc_sXY_l, wc_sXY, s3_x, s3_y :', round(s2_s,2), round(dt,2), round(wc_sXY_l,2), round(wc_sXY,2), round(s3_x,2), round(s3_y,2))
            if s2_s > 0.5 and dt < 1:
                if wc_sXY_l > 40 and wc_sXY>99 and s3_x > 3+s3_x_ and s3_y < 0:
                    org_in_2 = 1
                    OrgMain2 = "b"
                    inversion = 1
                if wc_sXY_l < 60  and wc_sXY<1 and s3_y > 3+s3_y_ and s3_x < 0:
                    org_in_2 = -1
                    OrgMain2 = "s"
                    inversion = 1
            # Out Signal
            print ('cri, cri_r, s3_m, s3_m_short :', round(cri,2), round(cri_r,2), round(s3_m,2), round(s3_m_short,2))
            if cri > 0 and cri_r > 1 and s3_m > 0 and s3_m_short > 0:
                if org_in_2 == 1:
                    org_in_2 = 3
                    org_in_2_nf = nf
                    OrgMain2 = "so"
                elif org_in_2 != 1:
                    org_in_2 = 2
                    OrgMain2 = "so"
            if cri < 0 and cri_r < 1 and s3_m < 0 and s3_m_short < 0:
                if org_in_2 == -1:
                    org_in_2 = -3
                    org_in_2_nf = nf
                    OrgMain2 = "bo"
                elif org_in_2 != -1:
                    org_in_2 = -2
                    OrgMain2 = "bo"
        else:
            OrgMain2 = "n"
            inversion =0

        if org_in_2 == 1 or org_in_2 == 3:
            cri = cri + 1 #df.ix[nf - 100:nf - 1, "org_in_2"].sum()
        if org_in_2 == -1 or org_in_2 == -3:
            cri = cri - 1
        if cri>5:
            cri=5
        if cri<-5:
            cri=-5

        #cri_r
        if nf > 250:

            if ee_s>=1.8 and ee_s<2.2:
                len_cri_r = int(500 + (ee_s-1.8) * 1250)
            if ee_s>=2.2:
                len_cri_r = 1000
            if ee_s<1.8:
                len_cri_r = 500

            df_r = df.ix[nf - min(nf,len_cri_r):nf - 1, "org_in_2"]
            df_r_y = df_r[df_r < 0].count()
            df_r_x = df_r[df_r > 0].count()
            if df_r_y!=0:
                cri_r = float(df_r_x)/df_r_y
                if cri_r>2:
                    cri_r=2
            else:
                if df_r_x!=0:
                    cri_r=2
                else:
                    cri_r=1
        else:
            cri_r=1

        # cri_r touch
        if OrgMain == "b" and cri_r>=2-0.1:
            touch_cri=1
        if OrgMain == "s" and cri_r<=0+0.1:
            touch_cri=-1

        df.at[nf, "cri"] = cri
        df.at[nf, "cri_r"] = cri_r

        # ee_s * cri
        if nf>=222:
            cri_ee_s = cri * ee_s
        else:
            cri_ee_s = 0

        df.at[nf, "cri_ee_s"] = cri_ee_s

        # 모멘텀 발생시 순방향 진입 후 모멘텀 소멸시 반대 포지션 진입 전략
        if nf > 250 and s3_m != 0:
            if  s2_s_m>2 and s3_m>0:
                org_in_3 = 1
                OrgMain3 = "b"
            if  s2_s_m>2 and s3_m<0:
                org_in_3 = -1
                OrgMain3 = "s"
        else:
            OrgMain3 = "n"


        # 진입 종합
        if nf > 250 :
            if ee_s > 1.7 and ee_s_ave > 1.4 and ee_s >= ee_s_ave:
                if slope > 2.5 and dt_sum_2 > 0:
                    if cri_r > 1 and cri > -3 and df.ix[nf - 1, "cri"] >= df.ix[nf - 2, "cri"]:
                        OrgMain = "b"
                if slope < -2.5 and dt_sum_2 < 0:
                    if cri_r < 1 and cri < 3 and df.ix[nf - 1, "cri"] <= df.ix[nf - 2, "cri"]:
                        OrgMain = "s"

            if ee_s > 1.8 and ee_s_m > 1.5 and ee_s_slope > 0:
                if cri_r > 0.5 and df.ix[nf - 1, "cri_r"] >= df.ix[nf - 2, "cri_r"]:
                    if cri > -3 and df.ix[nf - 1, "apindex_s"] >= df.ix[nf - 3, "apindex_s"]:
                        if ee_s_ave > 1.5 and ee_s > ee_s_m:
                            if sXY_bns == 1:
                                OrgMain = "b"
                if cri_r < 1.5 and df.ix[nf - 1, "cri_r"] <= df.ix[nf - 2, "cri_r"]:
                    if cri < 3 and df.ix[nf - 1, "apindex_s"] <= df.ix[nf - 3, "apindex_s"]:
                        if ee_s_ave > 1.5 and ee_s > ee_s_m:
                            if sXY_bns == 0:
                                OrgMain = "s"
        if 1 == 0:
            if ee_s > 1.8 and ee_s_m > 1.5 and ee_s_slope > 0:
                if cri_r >= 1.8 and cri == 5:
                    OrgMain = "b"
                if cri_r <= 0.2 and cri == -5:
                    OrgMain = "s"
            df.at[nf, "org_in_2"] = org_in_2
            df.at[nf, "org_in_3"] = org_in_3

        # 진출가능여부(수익상태) 및 히트여부
        prf_able = 0
        if OrgMain == "b" and nfset != 0 and nfset < nf:
            ex.lbl_Inp_o.setText(str(inp_o))
            inst_p= 4+(o1px1 - inp_o)/float(tick_o)
            ex.lbl_NowProfit_o.setText(str("%0.3f" % (o1px1 - inp_o)))
            if dome_ab==1:
                if o1px1 >= inp_o + tick_o * 2:
                    prf_able = 1
                else:
                    prf_able = 0
            elif dome_ab==0 or dome_ab==2:
                if o1px1 >= inp_o + tick_o *4:
                    prf_able = 1
            if o1px1 < inp_o - tick_o * 6:
                prf_able = -1





def ynet(nowp, t, W, sw, a, b, c, d):

    if nowp == t:
        if sw == "+":
            result = (a - b + W)
        else:
            result = (a - b)

    elif nowp < t:
        if sw == "+":
            result = (a - b + c) + W
        else:
            result = (a - b + c)

    elif nowp > t:
        if sw == "+":
            result = (a - b - d) + W #= W - b + a - d
        else:
            result = (a - b - d)

    return result

def xnet(nowp, t, W, sw, a, b, c, d):

    if nowp == t:
        if sw == "-":
            result = (a - b + W)
        else:
            result = (a - b)

    elif nowp > t:
        if sw == "-":
            result = (a - b + c) + W
        else:
            result = (a - b + c)

    elif nowp < t:
        if sw == "-":
            result = (a - b - d) + W #W - b + a - d
        else:
            result = (a - b - d)

    return result

