1) Instructions to **AVBY_parser.py**

The file contains two functions "parse_av_lxml" and "parse_av_bs" for parsing
with LXML (XPATH) and BeautifulSoup respectively. It's up to user which one to choose
(based on tests performed by author the 1st is quite faster).

Both parsing functions return serializable array of hash tables
where each table represents unique car ad. The parser goes through
all pages on which search results are represented.

Query parameters must be passed manually (see "params" variable) and might also
be altered to filter by other parameters (see https://cars.av.by/filter for details).

In addition, the file contains "write_json_csv" function which produces
JSON and CSV files (both pops up in project directory).

2) Instructions to **CSVJSON_reader.py**

The file contains two functions "pretty_print" and "regular_print".

1st one prints CSV/JSON file to command line in form of well readable table.
NOTE: "PrettyTable" library must be installed via pip for successful call
       (see https://pypi.org/project/prettytable/ for details).

2nd one prints CSV/JSON file using standard methods of csv/json modules

Before using any of these functions one must make sure that csv/json file
a functon is being called on exist.
