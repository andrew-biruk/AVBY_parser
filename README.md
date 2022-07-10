1) Instructions to **AVBY_parser.py**

Use "parse_av_lxml" or "parse_av_bs" for parsing on LXML (XPATH) or BeautifulSoup.

Both functions return serializable array of hash tables
where each table represents unique car ad.

Query parameters must be passed manually
(see "params" variable and https://cars.av.by/filter/ for details).

Use "write_json_csv" to create JSON and CSV files in project directory.

2) Instructions to **CSVJSON_reader.py**

The file contains two functions "pretty_print" and "regular_print".

Use "pretty_print" to print CSV/JSON as well readable table.
NOTE: "PrettyTable" library is required (see https://pypi.org/project/prettytable/ for details).

Use "regular_print" to print CSV/JSON with standard methods of csv/json modules.

Before using any of these functions one must make sure csv/json file exists.
