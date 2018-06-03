import glob
import os
import sys
import time
import bisect
from datetime import datetime

import pandas as pd
from matplotlib import ticker, dates
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import timedelta
import dashboard

import matplotlib.dates as mdates
import mpl_toolkits.axes_grid1
from PyQt4.phonon import Phonon

from pyqtgraph.Qt import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import matplotlib

matplotlib.use("TkAgg")


class App(QtGui.QMainWindow, dashboard.Ui_Dashboard):
    TICK_INVERVAL = 180
    DATE_FORMAT_MS = '%d-%m-%Y %H:%M:%S:%f'
    DATE_FORMAT_MS_FOR_LABELED = '%Y-%m-%d %H:%M:%S.%f'
    DATE_FORMAT = '%d-%m-%Y %H:%M:%S'
    DATE_FORMAT_FILE = '%Y-%m-%d-%H-%M-%S'
    DATE_FORMAT_LCD = '%H:%M:%S'
    SECONDS_ON_PLOT = 20 * 1000 / 20
    FORWARD_SECONDS = 5 * 1000
    ACC_DATA_PATH = "C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\sensors\\raw_data_*"
    GPS_DATA_PATH = "C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\sensors\\gps_data_*"
    EVENTS_DATA_PATH = "C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\sensors\\events*"
    EVENTS_FROM_RAW_DATA = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\events_from_raw_data_test"
    EVENTS_FROM_LABELED_DATA = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\events_from_labeled_data_test"
    ACC_DATA_PATH = "C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized\\raw_data_*"
    GPS_DATA_PATH = "C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized\\gps_data_*"
    EVENTS_DATA_PATH = "C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized\\events*"

    def custom_plots(self):
        self.myFig_x, self.ax_x = plt.subplots()
        self.canvas_x = FigureCanvas(self.myFig_x)
        self.verticalLayout.addWidget(self.canvas_x)
        self.myFig_y, self.ax_y = plt.subplots()
        self.canvas_y = FigureCanvas(self.myFig_y)
        self.verticalLayout.addWidget(self.canvas_y)
        self.myFig_z, self.ax_z = plt.subplots()
        self.canvas_z = FigureCanvas(self.myFig_z)
        self.verticalLayout.addWidget(self.canvas_z)
        self.ax_z.xaxis.set_major_locator(dates.SecondLocator())
        self.ax_z.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax_x.xaxis.set_major_locator(dates.SecondLocator())
        self.ax_x.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax_y.xaxis.set_major_locator(dates.SecondLocator())
        self.ax_y.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        for label in self.ax_x.get_xticklabels() + self.ax_x.get_yticklabels():
            label.set_fontsize(8)
        for label in self.ax_y.get_xticklabels() + self.ax_y.get_yticklabels():
            label.set_fontsize(8)
        for label in self.ax_z.get_xticklabels() + self.ax_z.get_yticklabels():
            label.set_fontsize(8)
        self.myFig_x.autofmt_xdate()
        self.myFig_y.autofmt_xdate()
        self.myFig_z.autofmt_xdate()
        self.line_x, = self.ax_x.plot([], [], label="axis x",  color="brown")
        self.line_y, = self.ax_y.plot([], [], label="axis y", color="red")
        self.line_z, = self.ax_z.plot([], [], label="axis z", color="green")
        self.ax_x.set_ylabel("axis x [m/s^2]", fontsize=8)
        self.ax_y.set_ylabel("axis y [m/s^2]", fontsize=8)
        self.ax_z.set_ylabel("axis z [m/s^2]", fontsize=8)
        cid1 = self.myFig_x.canvas.mpl_connect('button_press_event', self.onclick)
        cid2 = self.myFig_y.canvas.mpl_connect('button_press_event', self.onclick)
        cid3 = self.myFig_z.canvas.mpl_connect('button_press_event', self.onclick)
        self.ax_x.grid()
        self.ax_y.grid()
        self.ax_z.grid()

    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)
        self.seekSlider.setMediaObject(self.videoPlayer.mediaObject())
        self.custom_plots()
        self.seekSlider.setMediaObject(self.videoPlayer.mediaObject())
        self.videoPlayer.mediaObject().setTickInterval(App.TICK_INVERVAL)
        self.videoPlayer.mediaObject().tick.connect(self.tock)
        self.volumeSlider.setAudioOutput(self.videoPlayer.audioOutput())
        self.start_video.clicked.connect(self.playClicked)
        self.fast_backward.clicked.connect(self.fast_backward_handler)
        self.fast_forward.clicked.connect(self.fast_forward_handler)
        self.file_browser_button.clicked.connect(self.file_browser_handler)
        self.tag_data.clicked.connect(self.save_labeled_data)
        self.listWidget.itemClicked.connect(self.goto_event)
        self.checkBox.stateChanged.connect(self.handle_show_speed)
        self.begin_point_rb.setChecked(True)
        self.begin_point_value = None
        self.end_point_value = None
        self.show_speed = False

    def handle_show_speed(self, int):
        if self.checkBox.isChecked():
            self.show_speed = True
            self.ax_y.set_ylim(self.speed.min(), self.speed.max())
            self.ax_y.set_ylabel("speed [km/h]", fontsize=8)
        else:
            self.show_speed = False
            self.ax_y.set_ylim(self.y_arr.min(), self.y_arr.max())
            self.ax_y.set_ylabel("axis y [m/s^2]", fontsize=8)

    def save_labeled_data(self):
        # print self.data.index[self.data['time']==self.begin_point_value]
        start_index = self.data_temp['time'].searchsorted(self.begin_point_value)
        # print start_index
        # print self.data_temp['time'][start_index]
        end_index = self.data_temp['time'].searchsorted(self.end_point_value)
        acc_data_to_be_saved = self.data_temp[start_index[0]:end_index[0]]
        filename = unicode(self.tags.currentText()) + "_" + self.date_created_str + "_" + str(
            self.data_temp["time"][start_index[0]])
        filename = filename.replace(" ", "_").split('.')[0]
        filename = filename.replace(":", "_")
        print "ACCELEROMETER LABELED FILENAME: ", filename
        acc_data_to_be_saved.to_csv("C:\Users\kuba\Desktop\praca magisterska\sensor data\\DONOTTOUCH\\test_data\\" + filename + ".csv",
                                    header=True, index=False)
        gps_start_index = self.gps_data_temp['time'].searchsorted(self.begin_point_value)
        # print "GPS start index", gps_start_index
        # print self.gps_data_temp['time'][gps_start_index]
        gps_end_index = self.gps_data_temp['time'].searchsorted(self.end_point_value)
        gps_data_to_be_saved = self.gps_data_temp[gps_start_index[0]:gps_end_index[0]]
        # print unicode(self.tags.currentText())
        filename = unicode(self.tags.currentText()) + "_gps_" + str(self.data_temp["time"][start_index[0]])
        filename = filename.replace(" ", "_").split('.')[0]
        filename = filename.replace(":", "_")
        gps_data_to_be_saved.to_csv("C:\Users\kuba\Desktop\praca magisterska\sensor data\\DONOTTOUCH\\test_data\\" + filename + ".csv",
                                    header=True, index=False)
        print "GPS LABELED FILENAME: ", filename

    def onclick(self, event):
        if self.begin_point_rb.isChecked():
            self.begin_point_value = mdates.num2date(event.xdata)
            print self.begin_point_value
            self.start_point.setText('time=%s\n value=%f' %
                                     (self.begin_point_value.strftime(App.DATE_FORMAT_MS), event.ydata))
        elif self.end_point_rb.isChecked():
            self.end_point_value = mdates.num2date(event.xdata)
            self.end_point.setText('time=%s\n value=%f' %
                                   (self.end_point_value.strftime(App.DATE_FORMAT_MS), event.ydata))

    def fast_backward_handler(self):
        if self.videoPlayer.mediaObject().state() != Phonon.LoadingState:
            curr_time = self.videoPlayer.mediaObject().currentTime()
            self.videoPlayer.mediaObject().seek(curr_time - App.FORWARD_SECONDS)

    def fast_forward_handler(self):
        if self.videoPlayer.mediaObject().state() != Phonon.LoadingState:
            curr_time = self.videoPlayer.mediaObject().currentTime()
            self.videoPlayer.mediaObject().seek(curr_time + App.FORWARD_SECONDS)

    def file_browser_handler(self):
        directory = QtGui.QFileDialog.getOpenFileName(self,
                                                      "Pick a folder")
        # date_created = datetime.fromtimestamp(os.path.getctime(directory)).strftime(App.DATE_FORMAT)
        self.date_created_str = str(directory.split("_")[-1][:-4])
        print "VIDEO CREATED:", self.date_created_str
        self.current_file_display.setTextColor(QtGui.QColor('blue'))
        self.current_file_display.setText(os.path.basename(str(directory)))
        self.date_created.setTextColor(QtGui.QColor('blue'))
        self.date_created.setText(self.date_created_str)
        self.videoPlayer.load(Phonon.MediaSource(directory))
        self.data_file = self.get_valid_data_file(self.date_created_str, App.ACC_DATA_PATH)
        self.gps_data_file = self.get_valid_data_file(self.date_created_str, App.GPS_DATA_PATH)
        self.events_data_file = self.get_valid_data_file(self.date_created_str, App.EVENTS_DATA_PATH)
        self.data_file_display.setTextColor(QtGui.QColor('blue'))
        if self.show_events.isChecked():
            self.load_events_from_files(self.data_file)
            self.load_labeled_events_from_files(self.data_file)
        self.data_file_display.setText(os.path.basename(str(self.data_file)))
        self.load_acc_data_from_files(self.date_created_str, self.data_file)
        self.load_gps_data_from_files(self.date_created_str, self.gps_data_file)
        self.show_events_f(self.events_data_file)

    def load_events_from_files(self, date_file):
        """
        :param video_date_created: str
        :param date_file: path to file with sensor data
        :return: index
        """
        self.temp = [-1]
        self.prev_event = -1
        self.y_axis_for_events = np.linspace(-5, 5, 15)
        self.y_axis_for_events = np.append(self.y_axis_for_events, self.y_axis_for_events)
        self.y_axis_for_events_gps = np.linspace(0, 100, 1000)
        self.y_axis_for_events_gps = np.append(self.y_axis_for_events_gps, self.y_axis_for_events_gps)
        self.events_from_raw_file_df = pd.read_csv(
            os.path.join(App.EVENTS_FROM_RAW_DATA, "events_" + os.path.basename(date_file)))
        self.events_from_raw_file_df["start"] = [datetime.strptime(TIME, App.DATE_FORMAT_MS) for TIME in
                                                 self.events_from_raw_file_df['start']]
        self.events_from_raw_file_df["stop"] = [datetime.strptime(TIME, App.DATE_FORMAT_MS) for TIME in
                                                self.events_from_raw_file_df['stop']]

    def load_labeled_events_from_files(self, date_file):
        """
        :param video_date_created: str
        :param date_file: path to file with sensor data
        :return: index
        """
        self.temp_labeled = [-1]
        self.prev_event_labeled = -1
        self.y_axis_for_events_labeled = np.linspace(-3, 3, 4)
        self.y_axis_for_events_labeled = np.append(self.y_axis_for_events_labeled, self.y_axis_for_events_labeled)
        self.y_axis_for_events_gps_labeled = np.linspace(0, 100, 10)
        self.y_axis_for_events_gps_labeled = np.append(self.y_axis_for_events_gps_labeled,
                                                       self.y_axis_for_events_gps_labeled)
        self.events_from_labeled_file_df = pd.read_csv(
            os.path.join(App.EVENTS_FROM_LABELED_DATA, "events_" + os.path.basename(date_file)))
        print self.events_from_labeled_file_df.head(20)
        self.events_from_labeled_file_df = self.events_from_labeled_file_df.sort_values(by=["start"])
        self.events_from_labeled_file_df = self.events_from_labeled_file_df.reset_index(drop=True)
        self.events_from_labeled_file_df["start"] = [datetime.strptime(TIME, App.DATE_FORMAT_MS_FOR_LABELED) for TIME in
                                                 self.events_from_labeled_file_df['start']]
        self.events_from_labeled_file_df["stop"] = [datetime.strptime(TIME, App.DATE_FORMAT_MS_FOR_LABELED) for TIME in
                                                self.events_from_labeled_file_df['stop']]


        print self.events_from_labeled_file_df.head(20)

    def load_acc_data_from_files(self, video_date_created, date_file):
        """
        :param video_date_created: str
        :param date_file: path to file with sensor data
        :return: index
        """
        self.video_datetime_obj = datetime.strptime(video_date_created, App.DATE_FORMAT_FILE)
        # self.video_timestamp = time.mktime(self.video_datetime_obj.timetuple()) * 1000
        self.data = pd.read_csv(date_file, sep=";", names=["time", "x", "y", "z"])
        self.data_temp = self.data.copy()
        self.data_temp["time"] = [datetime.strptime(TIME, App.DATE_FORMAT_MS) for TIME in self.data['time']]
        self.time_arr = [datetime.strptime(TIME, App.DATE_FORMAT_MS) for TIME in self.data['time']]
        self.x_arr = np.array(self.data["x"])
        self.y_arr = np.array(self.data["y"])
        self.z_arr = np.array(self.data["z"])
        self.datafile_size = len(self.x_arr)

    def show_events_f(self, events_data_file):
        self.events_df = pd.read_csv(events_data_file, sep=";", names=["time", "event"])
        self.listWidget.clear()
        for index, row in self.events_df.iterrows():
            item = QtGui.QListWidgetItem("{0} {1}".format(*row))
            self.listWidget.addItem(item)

    def load_gps_data_from_files(self, video_date_created, date_file):
        """
        :param video_date_created: str
        :param date_file: path to file with sensor data
        :return: index
        """
        self.gps_data = pd.read_csv(date_file, sep=";", names=["time", "latitude", "longitude", "speed"])
        self.gps_data_temp = self.gps_data.copy()
        self.gps_data_temp["time"] = [datetime.strptime(TIME, App.DATE_FORMAT_MS) for TIME in
                                      self.gps_data_temp['time']]
        self.gps_time_arr = [datetime.strptime(TIME, App.DATE_FORMAT_MS) for TIME in self.gps_data['time']]
        self.gps_latitude = np.array(self.gps_data["latitude"])
        self.gps_longitude = np.array(self.gps_data["longitude"])
        self.speed = np.array(self.gps_data["speed"])
        self.ax_x.set_ylim(self.x_arr.min() - 1, self.x_arr.max() + 1)
        self.ax_y.set_ylim(self.y_arr.min() - 1, self.y_arr.max() + 1)
        self.ax_z.set_ylim(self.z_arr.min() - 1, self.z_arr.max() + 1)

    def get_valid_data_file(self, video_date, path):
        video_date_time = datetime.strptime(video_date, App.DATE_FORMAT_FILE)
        files = sorted(glob.glob(path))
        current_file = files[0]
        for file in files:
            print file
            sensors_date_time = datetime.strptime(current_file.split(("_"))[-1], App.DATE_FORMAT_FILE + '.csv')
            if abs(sensors_date_time - video_date_time) < timedelta(minutes=20):
                print "FOUND DATAFILE: ", current_file
                return current_file
            else:
                current_file = file
        return current_file

    def goto_event(self, item):
        event_time = str(item.text()).split(" ")[:2]
        event_time = " ".join(event_time)
        print event_time
        event_datetime_obj = datetime.strptime(event_time, App.DATE_FORMAT_MS)
        difference = event_datetime_obj - self.video_datetime_obj
        miliseconds_offset = difference.total_seconds() * 1000
        self.videoPlayer.mediaObject().seek(miliseconds_offset)

    def tock(self, t):
        # now = datetime.now()
        fulldate = self.video_datetime_obj + timedelta(milliseconds=t) + timedelta(milliseconds=200)
        i = self.data_temp['time'].searchsorted(fulldate)
        i = i[0]
        i_speed = 0
        if self.show_speed:
            i_speed = self.gps_data_temp['time'].searchsorted(fulldate)
            i_speed = i_speed[0]
        self.lcd_video_time.display(fulldate.strftime(App.DATE_FORMAT_LCD))
        self.lcd_data_time.display(datetime.strftime(self.data_temp['time'][i], App.DATE_FORMAT_LCD))

        if i < App.SECONDS_ON_PLOT:
            self.ax_x.set_xlim(self.time_arr[0], self.time_arr[App.SECONDS_ON_PLOT])
            self.line_x.set_data(self.time_arr[0:i], self.x_arr[0:i])
            if self.show_speed:
                self.ax_y.set_xlim(self.gps_time_arr[0], self.gps_time_arr[App.SECONDS_ON_PLOT])
                self.line_y.set_data(self.gps_time_arr[0:i_speed], self.speed[0:i_speed])
            else:
                self.ax_y.set_xlim(self.time_arr[0], self.time_arr[App.SECONDS_ON_PLOT])
                self.line_y.set_data(self.time_arr[0:i], self.y_arr[0:i])
            self.ax_z.set_xlim(self.time_arr[0], self.time_arr[App.SECONDS_ON_PLOT])
            self.line_z.set_data(self.time_arr[0:i], self.z_arr[0:i])
            for label in self.ax_x.get_xticklabels():
                label.set_fontsize(8)
            for label in self.ax_y.get_xticklabels():
                label.set_fontsize(8)
            for label in self.ax_z.get_xticklabels():
                label.set_fontsize(8)
        elif i >= self.datafile_size:
            pass
        else:
            self.ax_x.set_xlim(self.time_arr[i - App.SECONDS_ON_PLOT], self.time_arr[i])
            self.line_x.set_data(self.time_arr[i - App.SECONDS_ON_PLOT:i], self.x_arr[i - App.SECONDS_ON_PLOT:i])
            if self.show_speed:
                self.ax_y.set_xlim(self.gps_time_arr[i_speed - App.SECONDS_ON_PLOT], self.gps_time_arr[i_speed])
                self.line_y.set_data(self.gps_time_arr[i_speed - App.SECONDS_ON_PLOT:i_speed],
                                     self.speed[i_speed - App.SECONDS_ON_PLOT:i_speed])
            else:
                self.ax_y.set_xlim(self.time_arr[i - App.SECONDS_ON_PLOT], self.time_arr[i])
                self.line_y.set_data(self.time_arr[i - App.SECONDS_ON_PLOT:i], self.y_arr[i - App.SECONDS_ON_PLOT:i])
            self.ax_z.set_xlim(self.time_arr[i - App.SECONDS_ON_PLOT], self.time_arr[i])
            self.line_z.set_data(self.time_arr[i - App.SECONDS_ON_PLOT:i], self.z_arr[i - App.SECONDS_ON_PLOT:i])
            for label in self.ax_x.get_xticklabels():
                label.set_fontsize(8)
            for label in self.ax_y.get_xticklabels():
                label.set_fontsize(8)
            for label in self.ax_z.get_xticklabels():
                label.set_fontsize(8)
        if self.show_events.isChecked():
            i_event = self.events_from_raw_file_df['start'].searchsorted(self.data_temp['time'][i])[0]
            if self.temp[0] != self.events_from_raw_file_df["start"][i_event]: #and self.prev_event!=self.events_from_raw_file_df["event"][i_event]:
                self.prev_event = self.events_from_raw_file_df["event"][i_event]
                self.temp = [self.events_from_raw_file_df["start"][i_event] for i in range(15)]
                self.temp.extend([self.events_from_raw_file_df["stop"][i_event] for i in range(15)])
                self.ax_x.plot(self.temp, self.y_axis_for_events, '|', lineWidth= 10)
                self.ax_z.plot(self.temp, self.y_axis_for_events, '|', lineWidth=10)
                if self.show_speed:
                    self.temp = [self.events_from_raw_file_df["start"][i_event] for i in range(1000)]
                    self.temp.extend([self.events_from_raw_file_df["stop"][i_event] for i in range(1000)])
                    self.ax_y.plot(self.temp, self.y_axis_for_events_gps, '|', lineWidth= 10)
                else:
                    self.ax_y.plot(self.temp, self.y_axis_for_events + 9.5, '|', lineWidth= 10)

                self.ax_x.annotate(self.events_from_raw_file_df["event"][i_event].replace('0xb3', 'l'),
                                   xy=(self.events_from_raw_file_df["start"][i_event], 3.5),
                                   xycoords='data',
                                   xytext=(25, 7), textcoords='offset points', fontsize=9,
                                   arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
                # self.line_event.set_data(self.temp, self.y_axis_for_events)
            self.curr_event.setText(self.events_from_raw_file_df["event"][i_event])
            i_event_labeled = self.events_from_labeled_file_df['start'].searchsorted(self.data_temp['time'][i])[0]
            if self.temp_labeled[0] != self.events_from_labeled_file_df["start"][i_event_labeled]:
                self.prev_event_labeled = self.events_from_labeled_file_df["event"][i_event_labeled]
                self.temp_labeled = [self.events_from_labeled_file_df["start"][i_event_labeled] for i in range(4)]
                self.temp_labeled.extend([self.events_from_labeled_file_df["stop"][i_event_labeled] for i in range(4)])
                self.ax_x.plot(self.temp_labeled, self.y_axis_for_events_labeled, '*')
                self.ax_z.plot(self.temp_labeled, self.y_axis_for_events_labeled, '*')
                if self.show_speed:
                    self.temp_labeled = [self.events_from_labeled_file_df["start"][i_event_labeled] for i in range(10)]
                    self.temp_labeled.extend([self.events_from_labeled_file_df["stop"][i_event_labeled] for i in range(10)])
                    self.ax_y.plot(self.temp_labeled, self.y_axis_for_events_gps_labeled, '*')
                else:
                    self.ax_y.plot(self.temp_labeled, self.y_axis_for_events_labeled + 9.5, '*')

                self.ax_z.annotate(self.events_from_labeled_file_df["event"][i_event_labeled],
                                   xy=(self.events_from_labeled_file_df["start"][i_event_labeled], 3.5),
                                   xycoords='data',
                                   xytext=(25, 7), textcoords='offset points', fontsize=9,
                                   arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
                # self.line_event.set_data(self.temp, self.y_axis_for_events)

        self.canvas_x.draw()
        self.canvas_y.draw()
        self.canvas_z.draw()


    # curr_time = self.videoPlayer.mediaObject().currentTime()
    # curr_time = datetime.fromtimestamp(curr_time/1000).strftime("%H:%M:%S")
    # self.video_time_display.display(curr_time)
    # print "TICK EXECUDED: ", datetime.now() - now

    def playClicked(self):
        if self.videoPlayer.mediaObject().state() == Phonon.PlayingState:
            self.videoPlayer.pause()
        else:
            self.videoPlayer.play()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())
