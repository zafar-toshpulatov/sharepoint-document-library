import io
import os
import json
from datetime import datetime
import argparse
from os import listdir
from os.path import isfile, join

def open_file(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    return data

def get_file_names(upload_path):
    file_names = [f for f in listdir(upload_path) if isfile(join(upload_path, f))]
    return file_names

def load_json(path):
    with open(path) as fil:
        return json.load(fil)

# def saveAsJson(data, filePath):
#     abs_path = get_abs_path(filePath)
#     with open(abs_path, 'w') as file:
#         file.write(data)

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def parse_args(required_config_keys):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config',
        help='Config file',
        required=True)

    parser.add_argument(
        '-d', '--download_path',
        help='Local path to save downloaded files from Sharepoint')

    parser.add_argument(
        '-u', '--upload_path',
        help='Local path to upload files to Sharepoint')

    args = parser.parse_args()
    if args.config:
        setattr(args, 'config_path', args.config)
        args.config = load_json(args.config)
    if args.download_path:
        setattr(args, 'download_path', args.download_path)
        args.download_path = get_abs_path(args.download_path)
    if args.upload_path:
        setattr(args, 'upload_path', args.upload_path)
        args.upload_path = get_abs_path(args.upload_path)

    check_config(args.config, required_config_keys)

    return args


def check_config(config, required_keys):
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise Exception("Config is missing required keys: {}".format(missing_keys))



# LOGGER = singer.get_logger()
#
# class BloombergNameError(LookupError):
#     '''raise this when there's a lookup error'''
#
# def get_abs_path(path):
#     return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)
#
# def mapWSTablestoDataframe(ws):
#     mapping = {}
#     for entry, data_boundary in ws.tables.items():
#         data = ws[data_boundary]
#         content = [[cell.value for cell in ent]
#                    for ent in data
#                    ]
#         header = content[0]
#         rest = content[1:]
#         df = pd.DataFrame(rest, columns=header)
#         mapping[entry] = df
#     return mapping
#
# def getJsonData(tableName, mapping, config):
#     df = mapping[tableName].dropna(how='all', axis=1)
#     df = df.dropna(how='all', axis=0)
#     if tableName in config["transpose"]:
#         df = df.T
#         df = df.reset_index()
#         first_row = df.iloc[0]
#         df.columns = first_row.values.tolist()
#         df = df.iloc[1:]
#     json_str = df.to_json(orient='records')
#     json_data = json.loads(json_str)
#     return json_data
#
# def skipNoneColumn(json_data):
#     for record in json_data:
#         for key, val in record.items():
#             if key == "None":
#                 record.pop(key, None)
#                 break
#     return json_data
#
# def deleteFileFromLocal(path):
#     abs_path = get_abs_path(path)
#     if os.path.exists(abs_path):
#         os.remove(abs_path)
#         LOGGER.info("'{}' file is deleted from local".format(abs_path))
#
# def fixTimeStamp(records, convert_to_timestamp):
#     for record in records:
#         for key, val in convert_to_timestamp.items():
#             for timeStampCol in val:
#                 if timeStampCol in record:
#                     if type(record[timeStampCol]) is int:
#                         record[timeStampCol] = (datetime.fromtimestamp(record[timeStampCol] / 1e3)).replace(hour=00).strftime("%Y-%m-%dT%H:%M:%S")
#     return records
#
# def removeDoubleDashFromData(records):
#     for record in records:
#         for key, val in record.items():
#             if isinstance(val, str) and val == "--":
#                 record[key] = None
#     return records
#
# def convertInt2Float(records):
#     for record in records:
#         for key, val in record.items():
#             if isinstance(val, int):
#                 record[key] = float(val)
#     return records
#
# def getTargetPriceMethod(records):
#     for record in records:
#         if "Target Price Methodology" in record:
#             method = record["Target Price Methodology"]
#             return method
#     return None
#
# def getSitePath(url):
#     splitted_url = url.split("/")
#     if "sites" in splitted_url:
#         for count, val in enumerate(splitted_url):
#             if val == "sites":
#                 return "{}/{}".format(val, str(splitted_url[count+1])), "/".join(url.split("/", 6)[:6])
#     else:
#         return "", "/".join(url.split("/", 4)[:4])
#
# def getRecords(config, client, scrapeTimeStamp, email_message_data, hostname, lastUpdatedDate=False):
#     # siteName = config['site_name']
#     # documentLibrary = config['document_library']
#     exact_file_path = config['file_path']
#     fileName = config['file_name']
#
#     sitePath, docLibWebUrl = getSitePath(exact_file_path)
#     siteId, siteWebUrl = client.getSiteIdBySitePath(hostname, sitePath)
#     driveId = client.getDrivesIdByWebUrl(siteId, docLibWebUrl)
#     itemPath = exact_file_path.split(docLibWebUrl + "/")[1]
#
#     if lastUpdatedDate:
#         driveDownloadUrl, fileDetails = client.getDriveDownloadUrlByPath(driveId, itemPath, lastUpdatedDate)
#     else:
#         driveDownloadUrl, fileDetails = client.getDriveDownloadUrlByPath(driveId, itemPath)
#
#     if driveDownloadUrl:
#         filePath = 'files/' + fileName
#
#         filePath = get_abs_path(filePath)
#         with open(filePath, "rb") as f:
#             in_mem_file = io.BytesIO(f.read())
#         wb = load_workbook(in_mem_file, data_only=True)
#         sheetNames = wb.sheetnames
#
#         if "worksheet_name" in config:
#             worksheet_name = config['worksheet_name']
#             if worksheet_name.casefold() in (name.casefold() for name in sheetNames):
#                 ws = wb[worksheet_name]
#             else:
#                 raise Exception("Coundn't find specified '{}' worksheet in '{}' file".format(worksheet_name, filePath))
#         else:
#             ws = wb.active
#             worksheet_name = wb.sheetnames
#         mapping = mapWSTablestoDataframe(ws)
#         tableNames = []
#         for key, val in ws.tables.items():
#             tableNames.append(key)
#         LOGGER.info("Found tables: '{}' in '{}' worksheet".format(str(tableNames), worksheet_name))
#
#         scrapingTableNames = []
#         for tableName in tableNames:
#             json_data = getJsonData(tableName, mapping, config)
#             json_data = skipNoneColumn(json_data)
#
#             if tableName == "Company_Overview":
#                 method = getTargetPriceMethod(json_data)
#                 if method == "Per Share":
#                     scrapingTableNames = ["Company_Overview", "Excel_Bloomberg_Data", "Model_Projections", "Per_Share_Bank",
#                                           "Per_Share_XIRR", "Per_Share_Target_Price", "Quarterly_Projections_Dividends"]
#                     LOGGER.info("Target Price Method : 'Per Share'")
#                     email_message_data["Enterprise_Value_Bank"].append('')
#                     email_message_data["Enterprise_Value_XIRR"].append('')
#                     email_message_data["Enterprise_Value_Target_Price"].append('')
#                 elif method == "Enterprise Value":
#                     scrapingTableNames = ["Company_Overview", "Excel_Bloomberg_Data", "Model_Projections", "Enterprise_Value_Bank",
#                                           "Enterprise_Value_XIRR", "Enterprise_Value_Target_Price", "Quarterly_Projections_Dividends"]
#                     LOGGER.info("Target Price Method : 'Enterprise Value'")
#                     email_message_data["Per_Share_Bank"].append('')
#                     email_message_data["Per_Share_XIRR"].append('')
#                     email_message_data["Per_Share_Target_Price"].append('')
#                 else:
#                     scrapingTableNames = tableNames
#
#         dataCollection = {}
#         for scrapingTableName in scrapingTableNames:
#             json_data = getJsonData(scrapingTableName, mapping, config)
#             json_data = skipNoneColumn(json_data)
#
#             json_data, error = validateValueError(json_data)
#             email_message_data[scrapingTableName].append(error)
#
#             if json_data:
#                 if scrapingTableName in config["convert_to_timestamp"] and config["convert_to_timestamp"]:
#                     json_data = fixTimeStamp(json_data, config["convert_to_timestamp"])
#
#                 for record in json_data:
#                     record["FileName"] = fileName
#                     record["ScrapeTimeStamp"] = scrapeTimeStamp
#                     record["FileName+ScrapeTimeStamp"] = fileName + scrapeTimeStamp
#
#                 json_data = removeDoubleDashFromData(json_data)
#                 json_data = convertInt2Float(json_data)
#                 dataCollection[scrapingTableName] = json_data
#         return dataCollection, fileDetails, email_message_data
#     else:
#         return False, False, False
#
# def validateValueError(json_data):
#     validatedData = []
#     error = ''
#     errors = []
#     for record in json_data:
#         validatedRecord = {}
#         for key, val in record.items():
#             if val == "#VALUE!":
#                 validatedRecord[key] = None
#                 LOGGER.error("#VALUE! ERROR in '{}': '{}'".format(key, val))
#                 errors.append(val)
#             elif val == "#N/A Connection":
#                 validatedRecord[key] = None
#                 LOGGER.error("#N/A Connection ERROR in '{}': '{}'".format(key, val))
#                 errors.append(val)
#             elif val == "#N/A Requesting Data...":
#                 validatedRecord[key] = None
#                 LOGGER.error("##N/A Requesting Data... ERROR in '{}': '{}'".format(key, val))
#                 errors.append(val)
#             elif val == "#N/A":
#                 validatedRecord[key] = None
#                 LOGGER.error("#N/A ERROR in '{}': '{}'".format(key, val))
#                 errors.append(val)
#             elif val == "#DIV/0!":
#                 validatedRecord[key] = None
#                 LOGGER.error("#DIV/0! ERROR in '{}': '{}'".format(key, val))
#                 errors.append(val)
#             elif val == "#REF!":
#                 validatedRecord[key] = None
#                 LOGGER.error("#REF! ERROR in '{}': '{}'".format(key, val))
#                 errors.append(val)
#             elif val == "#NULL!":
#                 validatedRecord[key] = None
#                 LOGGER.error("#NULL! ERROR in '{}': '{}'".format(key, val))
#                 errors.append(val)
#             elif val == "#NAME?":
#                 validatedRecord[key] = None
#                 LOGGER.error("#NAME? ERROR in '{}': '{}'".format(key, val))
#                 errors.append(val)
#             elif "#" in str(val):
#                 validatedRecord[key] = None
#                 LOGGER.error("# ERROR in '{}': '{}'".format(key, val))
#                 errors.append(val)
#             else:
#                 validatedRecord[key] = val
#                 # TODO: swap out the value for sample values
#         validatedData.append(validatedRecord)
#         error = '; '.join(list(set(errors)))
#     return validatedData, error
#
# def validateBloombergError(json_data):
#     for record in json_data:
#         for key, val in record.items():
#             if val == "#NAME?":
#                 LOGGER.error("# BLOOMBERG VALUE ERROR in '{}': '{}'".format(key, val))
#                 return True
#     return False
#
# def get_error_message_data(email_message_data):
#     error_message_data = {"File name": [], "Scrape status": [], "System error": [], "Company_Overview": [],
#                           "Excel_Bloomberg_Data": [], "Model_Projections": [], "Enterprise_Value_Bank": [],
#                           "Enterprise_Value_XIRR": [], "Enterprise_Value_Target_Price": [], "Per_Share_Bank": [],
#                           "Per_Share_XIRR": [], "Per_Share_Target_Price": [], "Quarterly_Projections_Dividends": [],
#                           "File path": []}
#     for num, _ in enumerate(email_message_data["Company_Overview"]):
#         if email_message_data["System error"][num] or email_message_data["Company_Overview"][num] or email_message_data["Excel_Bloomberg_Data"][num] or \
#                 email_message_data["Model_Projections"][num] or email_message_data["Enterprise_Value_Bank"][num] or \
#                 email_message_data["Enterprise_Value_XIRR"][num] or email_message_data["Enterprise_Value_Target_Price"][num] or \
#                 email_message_data["Per_Share_Bank"][num] or email_message_data["Per_Share_XIRR"][num] or \
#                 email_message_data["Per_Share_Target_Price"][num] or email_message_data["Quarterly_Projections_Dividends"][num]:
#             error_message_data["File name"].append(email_message_data["File name"][num])
#             error_message_data["Scrape status"].append(email_message_data["Scrape status"][num])
#             error_message_data["System error"].append(email_message_data["System error"][num])
#             error_message_data["Company_Overview"].append(email_message_data["Company_Overview"][num])
#             error_message_data["Excel_Bloomberg_Data"].append(email_message_data["Excel_Bloomberg_Data"][num])
#             error_message_data["Model_Projections"].append(email_message_data["Model_Projections"][num])
#             error_message_data["Enterprise_Value_Bank"].append(email_message_data["Enterprise_Value_Bank"][num])
#             error_message_data["Enterprise_Value_XIRR"].append(email_message_data["Enterprise_Value_XIRR"][num])
#             error_message_data["Enterprise_Value_Target_Price"].append(email_message_data["Enterprise_Value_Target_Price"][num])
#             error_message_data["Per_Share_Bank"].append(email_message_data["Per_Share_Bank"][num])
#             error_message_data["Per_Share_XIRR"].append(email_message_data["Per_Share_XIRR"][num])
#             error_message_data["Per_Share_Target_Price"].append(email_message_data["Per_Share_Target_Price"][num])
#             error_message_data["Quarterly_Projections_Dividends"].append(email_message_data["Quarterly_Projections_Dividends"][num])
#             error_message_data["File path"].append('<a href="{0}">{0}</a>'.format(email_message_data["File path"][num]))
#
#     return error_message_data
#
#
# STYLE = """<style>
#                 table {
#                   font-family: arial, sans-serif;
#                   border-collapse: collapse;
#                   width: 100%;
#                 }
#
#                 td, th {
#                   border: 1px solid #dddddd;
#                   text-align: left;
#                   padding: 8px;
#                 }
#
#                 tr:nth-child(even) {
#                   background-color: #dddddd;
#                 }
#             </style>"""
#
# CURRENT_EST_DATE = datetime.now(pytz.timezone('US/Eastern')).strftime("%m-%d-%Y")
#
# def make_html_message(error_message_data):
#     html_table = '<table><tr><th>' + '</th><th>'.join(error_message_data.keys()) + '</th></tr>'
#     for row in zip(*error_message_data.values()):
#         html_table += '<tr><td>' + '</td><td>'.join(row) + '</td></tr>'
#     html_table += '</table>'
#
#     html_message = """<!DOCTYPE html>
#                     <html>
#                         <head>
#                             {}
#                         </head>
#                         <body>
#                             <h2>Overnight scrape status for {}</h2>
#                             <h3>Existing Error Types of the Scraped Tables:</h3>
#                             {}
#                         </body>
#                     </html>""".format(STYLE, CURRENT_EST_DATE, html_table)
#     return html_message
#
# def successful_html_message():
#     html_message = """<!DOCTYPE html>
#                         <html>
#                             <head>
#                                 {}
#                             </head>
#                             <body>
#                                 <h2>Overnight scrape status for {}</h2>
#                                 <h3>No errors detected in model scraping!</h3>
#                             </body>
#                         </html>""".format(STYLE, CURRENT_EST_DATE)
#     return html_message
#
# def isMessageExist(error_message_data):
#     for value in error_message_data.values():
#         if value:
#             return True
#     return False