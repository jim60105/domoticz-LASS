# Domoticz Python Plugins for LASS(Location Aware Sensing System)
<h1>Setup</h1>
1.	Put the "LASS" directory under<code>[domoticz_installed_directory]/plugins/</code>
	For example: <code>/opt/domoticz/plugins/LASS/plugin.py</code>

2.	Restart Domoticz

3.	Add Hardware like below:

	> Enabled: (Checked)<br>
	> Name: MyLASS (Or whatever you want)<br>
	> Type: LASS - Location Aware Sensing System<br>
	> Data Timeout: Disabled<br>
	> LASS_ID: (Find it here: [g0v](https://airmap.g0v.asper.tw/list). Support LASS LASS4U LASSMAPS Edimax.)<br>
	> Update Rate(Min): 10<br>

4.	Then you should see it in the UTILITY page.

<h1>Notice</h1>
Please set Data Timeout to Disabled! It won't work as expected!