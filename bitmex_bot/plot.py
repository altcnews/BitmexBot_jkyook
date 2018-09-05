import pandas as pd
import matplotlib.pyplot as plt
import Tkinter as Tk
from tkFileDialog import askopenfilename


# # import tkinter.filedialog
# from tkinter import filedialog
# import tkinter as tk
#
ax1 = plt.subplot(611)
ax2 = ax1.twinx()
ax3 = plt.subplot(612)
ax4 = ax3.twinx()
ax5 = plt.subplot(613)
ax6 = ax5.twinx()
ax7 = plt.subplot(614)
ax8 = ax7.twinx()
ax9 = plt.subplot(615)
ax10 = ax9.twinx()
ax11 = plt.subplot(616)
ax12 = ax11.twinx()
#/
file_loaded = 0

root = Tk.Tk()
root.withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
print(filename)
dfp = pd.read_csv(filename)  # [205:]
start_data_index = dfp[dfp.ns != 0].index[0]
dfp = dfp.ix[start_data_index:]
file_loaded += 1
df = dfp

# Plot range
plot_start = 1
if file_loaded >= 1:
    plot_last = dfp.shape[0] - 1


# plot
p1 = df.ix[plot_start:plot_last, "price"]
ax1.plot(p1, 'r')
p2 = df.ix[plot_start:plot_last, "d_OMain"]
ax2.plot(p2, 'g')
p3 = df.ix[plot_start:plot_last, "profit"]
ax3.plot(p3, 'r')
p4 = df.ix[plot_start:plot_last, "dxy_200_medi"]
ax4.plot(p4, 'g')
p5 = df.ix[plot_start:plot_last, "in_str"]
ax5.plot(p5, 'r')
p6 = df.ix[plot_start:plot_last, "piox"]
ax6.plot(p6, 'g')
p7 = df.ix[plot_start:plot_last, "cvol_s"]
ax7.plot(p7, 'r')
p8 = df.ix[plot_start:plot_last, "cvol_t"]
ax8.plot(p8, 'g')
p9 = df.ix[plot_start:plot_last, "dt"]
ax9.plot(p9, 'r')
p10 = df.ix[plot_start:plot_last, "count_m"]
ax10.plot(p10, 'g')
# p11 = df.ix[plot_start:plot_last, "sig_2"]
# ax11.plot(p11, 'r')
# p12 = df.ix[plot_start:plot_last, "sig_3"]
# ax12.plot(p12, 'g')

# if p3_t != "None":
#     p3 = df.ix[plot_start:plot_last, p3_t]
#     ax3.plot(p3, 'r')
# if p4_t != "None":
#     p4 = df.ix[plot_start:plot_last, p4_t]
#     ax4.plot(p4, 'g')

# if p11_t != "None":
#     p11 = df.ix[plot_start:plot_last, p11_t]
#     ax11.plot(p11, 'r')
# if p12_t != "None":
#     p12 = df.ix[plot_start:plot_last, p12_t]
#     ax12.plot(p12, 'g')

# show
# plt.plot(p1, 'r', p2, 'g', p3, 'b', p4, 'k')
plt.legend(loc='upper left', frameon=False)
plt.show()