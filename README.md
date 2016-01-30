# ohw2carbon

Use this script to send sensor data reported by [Openhardwaremonitor](http://openhardwaremonitor.org/) to a [Carbon server](https://github.com/graphite-project/carbon) which is most commonly used 
a time series backend for [Graphite](http://graphite.wikidot.com/)

The nice thing about [Openhardwaremonitor](http://openhardwaremonitor.org/) is that it runs on any plattform, and thus allows you to 
monitor any host you access too. Running this script as a cron will take any data reported by OHW, removes protentially problematic characters,
and sends it to a Carbon server. This allows for example to monitor a Windows-based gaming/HTPC machine without the need of 
leaving Steam or Kodi. Make sure to have the cron interval in sync with the storage scheme in Carbon to avoid unnecessary traffic.

