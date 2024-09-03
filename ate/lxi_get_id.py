# Before using this script install packages:
# - VXI-11          pip install python-vxi11
# - Matplotlib      pip install matplotlib

import vxi11
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
from datetime import datetime

# Define spectrum plot settings

PLOT_SIZE_X = 12
PLOT_SIZE_Y = 9

PLOT_NUM_PTS = 601

PLOT_0_X_MIN = 49.75
PLOT_0_X_MAX = 50.25
PLOT_0_X_MINOR_STEP = 0.050
PLOT_0_X_MAJOR_STEP = 0.050

PLOT_0_Y_MIN = -100
PLOT_0_Y_MAX = 0
PLOT_0_Y_MINOR_STEP = 5
PLOT_0_Y_MAJOR_STEP = 10

t0, t1, t2, t3, t4 = 0, 0, 0, 0, 0

def main(t0, t1, t2, t3, t4):
	t0 = datetime.now()
	
	device_ip = "192.168.20.187" 
	device_tp = vxi11.Instrument(device_ip)
	device_id = device_tp.ask("*IDN?")
	device_id = device_id.split(',')
	if device_id[1] == 'DG4102':
		pass
	elif device_id[1] == 'DP832':
		pass
	elif device_id[1] == 'DSA815':
		device_id = ' '.join(device_id[:2])
		print("Device ID :", device_id)
		dsa815 = device_tp

	try:
		t1 = datetime.now()
		print("Connection establishment: ", t1 - t0)
		
		trace = dsa815.ask(":TRACE:DATA? TRACE1")
		
		#lic = dsa815.ask(":SYSTem:LKEY RAJ9JBBN3AWWUSFPJAZG73GDTC5A")
		#lic = dsa815.ask(":SYSTem:LKEY? 0002")		
		#print(lic)
		
		t2 = datetime.now()
		print("Trace data acquisition: ", t2 - t1)
		
		trace = trace.split(', ')

		# Remove "#900000914" at first element
		trace_0 = trace[0]
		trace[0] = trace_0[12:]

		trc = []
		for i in trace:
			trc.append(float(i))
		#trace = float(trace)

		t3 = datetime.now()
		print("Trace data processing: ", t3 - t2)

		plot_spectrum(trc, t3)

	except KeyboardInterrupt:
		pass

def plot_spectrum(trace, t3):
	x = []
	freq_delta = (PLOT_0_X_MAX - PLOT_0_X_MIN) / (len(trace) - 1)
	for i in range(len(trace)):
		x.append(PLOT_0_X_MIN + i*freq_delta)

	#fig, (ax0) = plt.subplots(1, 1, figsize=(PLOT_SIZE_X, PLOT_SIZE_Y), constrained_layout=true)
	fig, (ax0) = plt.subplots(1, 1, figsize=(PLOT_SIZE_X, PLOT_SIZE_Y))

	# Plot FFT Spectrum
	ax0.clear()
	#ax0.set_xlabel("Freq [MHz]", fontsize=14)        
	#ax0.set_ylabel("Amplitude [dBm]", fontsize=14)
	ax0.grid(which="major", linestyle="--", color="gray", linewidth=0.5)
	ax0.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)
	ax0.xaxis.set_minor_locator(MultipleLocator(PLOT_0_X_MINOR_STEP))
	ax0.xaxis.set_major_locator(MultipleLocator(PLOT_0_X_MAJOR_STEP))
	#ax0.yaxis.set_minor_locator(MultipleLocator(PLOT_0_Y_MINOR_STEP))
	ax0.yaxis.set_major_locator(MultipleLocator(PLOT_0_Y_MAJOR_STEP))
	ax0.tick_params(which='major', length=0, width=0.5, labelsize='large')
	ax0.tick_params(which='minor', length=0, width=0.5)

	ax0.plot(x, trace, label="T1 Normal", color='#00008B', linewidth=2, alpha=0.75) # RGB Color Deep Blue-Violet
	#ax0.plot(x, y2, label="ADC2", color='#99004C', linewidth=2, alpha=0.75) # RGB Color Coral Red
	ax0.legend(loc='upper right', fontsize=14)
	ax0.set_xlim(PLOT_0_X_MIN, PLOT_0_X_MAX)
	ax0.set_ylim(PLOT_0_Y_MIN, PLOT_0_Y_MAX)

	ax0.axes.xaxis.set_ticks([])
    
	ax0.text(49.75,1, 'Ref 0 dBm', fontsize='large')
	ax0.text(49.98,1, 'Att 10 dB', fontsize='large')
	ax0.text(50.16,1, 'Preamp: ON', fontsize='large')
	ax0.text(49.75,-104, 'Center Freq    50.000 MHz', fontsize='large')
	ax0.text(50.16,-104, 'Span 500 kHz', fontsize='large')
	ax0.text(49.75,-108, 'RBW 10 kHz', fontsize='large')
	ax0.text(49.97,-108, 'VBW 10 kHz', fontsize='large')
	ax0.text(50.16,-108, 'Sweep Time 10 ms', fontsize='large')

	plt.savefig(fname="dsa815_plot.png", format='png', dpi=300)

	plt.show()


if __name__ == '__main__':
	main(t0, t1, t2, t3, t4)
