ZenLogbook
========
ZenLogbook arose out of a desire to release the automated backend tracking process behind [Hashlette.com](http://hashlette.com/) as open source. The requirement was thus: track specific miner performance over time. It's a bit of a headache to do this manually, as you have to constantly login to ZenPortal and manually copy/enter information into a spreadsheet or sqldatabase. The process itself isn't just cumbersome, it's also open to the natural errors that creep into any data entry task. ZenLogbook was created to solve this problem. It parses all "device payout" entries from a user specified time.

It's not exactly easy to parse the data from ZenPortal, as GAW uses a socket.io connection to update information. This created further headaches as I always had to ensure proper handshakes and what not. Naturally, one could solve this problem in java, but I've been playing with python more lately, and doing it via the DOM is perhaps easier to maintain from a code perspective.

## Notes about the script

This is not most efficient code in terms of length or performance. This was written with structure as perhaps the highest priority. Instead of directly calling webpage elements, we crawl the DOM to find nested values and elements. The benefit of this approach is that it's highly scaleable and the underlying code is more flexible when GAW makes changes to the web interface.

This is a highly iterative approach to scraping. We first find all entries on the Latest Activity page. Then we start iterating through them one by one. If it's a "device payout" type entry, we start parsing all the information. (Note that there are three possible formats that GAW provides, but the script parses each layout dynamically. See moredetail.md file for additional information.)

This continues onto previous pages until the script halts on the user specified date (see settings section below). Everything is stored in a large multidimensional array which is then passed to to the ezodf lib to write to an .ods file. If you wish to store data into an sqlite, csv, or other format, script will easily support whatever output provided there's an existing python lib and you make a few changes to the included write function.

## Settings

The Zenminer_logbook_settings.py file contains the following:
```python
SPREADSHEETNAME = 'zenminer_logbook.ods'
STOPDATE = 'update' #options are yesterday and update
SPREADSHEET_KEY={'date': 'A', 'devicename': 'B', 'devicetype':'C', 'power':'D', 'BTCpayout':'E', 'HPpayout':'F', 'fee':'G', 'firstpool': 'I', 'firstpool_actual':'J', 'secondpool':'K', 'secondpool_actual':'H'}
```

The SPREADSHEET_KEY is a python dict that is case sensitive. This provides the correct column mappings to the spreadsheet. The spreadsheet must be created prior to running ZenLogbook. It will not automatically create file for you. The 'update' function provides a lookup on the date entered into the A column at the highest row. It's important that you resort the spreadsheet so that the dates are ascending (newest date are last) to prevent duplicate entires.

## Requirements
  
* Python bindings for Selenium
* Selenium server
 * JRE 1.6 or newer
  
## Installation instructions

Will be added soon.

## License

Copyright Caleb Ku 2014. Distributed under the MIT License. (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
