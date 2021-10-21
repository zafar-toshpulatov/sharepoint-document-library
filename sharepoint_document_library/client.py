import requests
from datetime import datetime
import tqdm
from urllib.parse import unquote
from sharepoint_document_library.utils import get_abs_path
import logging

logging.basicConfig(level = logging.INFO)

class SharepointError(Exception):
    pass


class BadRequest(SharepointError):
    pass


class InvalidAuthenticationToken(SharepointError):
    pass


class Forbidden(SharepointError):
    pass


class NotFound(SharepointError):
    pass


class Conflict(SharepointError):
    pass


class InternalServiceError(SharepointError):
    pass


ERROR_CODE_EXCEPTION_MAPPING = {
    400: BadRequest,
    401: InvalidAuthenticationToken,
    403: Forbidden,
    404: NotFound,
    409: Conflict,
    500: InternalServiceError}


def get_exception_for_error_code(status_code):
    return ERROR_CODE_EXCEPTION_MAPPING.get(status_code, SharepointError)


def raise_for_error(response):
    try:
        response.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError) as error:
        try:
            content_length = len(response.content)
            if content_length == 0:
                return
            response_json = response.json()
            status_code = response.status_code
            message = 'RESPONSE: {}'.format(response_json)
            ex = get_exception_for_error_code(status_code)
            raise ex(message)
        except (ValueError, TypeError):
            raise SharepointError(error)


class SharePointClient:
    def __init__(self, config):
        self.tenant_name = config['tenant_name']
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.grant_type = config['grant_type']
        self.scope = config['scope']

        self.tokenUrl = "https://login.microsoftonline.com/{}/oauth2/v2.0/token".format(self.tenant_name)
        self.tokenData = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": self.grant_type,
            "scope": self.scope
        }
        self.baseUrl = "https://graph.microsoft.com/v1.0"
        self.session = requests.Session()
        self.accessToken = self.getAccessToken()
        self.headers = {"content-type": "application/json", "Authorization": "Bearer " + self.accessToken}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def getAccessToken(self):
        response = self.session.post(self.tokenUrl, data=self.tokenData)
        if response.status_code != 200:
            logging.error('Error status_code = {}'.format(response.status_code))
            raise_for_error(response)
        else:
            self.accessToken = response.json()["access_token"]
            self.headers = {"content-type": "application/json", "Authorization": "Bearer " + self.accessToken}
            return self.accessToken

    def renewAccessToken(self):
        self.accessToken = self.getAccessToken()
        self.headers = {"content-type": "application/json", "Authorization": "Bearer " + self.accessToken}

    def getSiteId(self, siteName):
        url = self.baseUrl + "/sites?$select=siteCollection,webUrl,id,name"
        success = False
        retry = 1
        while not success:
            try:
                response = self.session.get(url, headers=self.headers)
            except:
                logging.error('Connection Error. Trying to reconnect.')
                self.renewAccessToken()
            else:
                if response.status_code != 200:
                    logging.error('Error status_code = {}. Trying to renew access token.'.format(response.status_code))
                    self.renewAccessToken()
                    retry += 1
                    if retry > 4:
                        raise_for_error(response)
                else:
                    success = True
                    values = response.json()["value"]
                    for value in values:
                        if "name" in value:
                            if siteName == value["name"]:
                                return value["id"], value["siteCollection"]["hostname"]
                    raise Exception("Coundn't find specified '{}' site in sharepoint".format(siteName))

    def getSiteIdBySitePath(self, hostname, sitePath):
        url = self.baseUrl + "/sites/{}:/{}".format(hostname, sitePath)
        success = False
        retry = 1
        while not success:
            try:
                response = self.session.get(url, headers=self.headers)
            except:
                logging.error('Connection Error. Trying to reconnect.')
                self.renewAccessToken()
            else:
                if response.status_code != 200:
                    logging.error('Error status_code = {}. Trying to renew access token.'.format(response.status_code))
                    self.renewAccessToken()
                    retry += 1
                    if retry > 4:
                        raise_for_error(response)
                else:
                    success = True
                    data = response.json()
                    if "id" in data and "webUrl" in data:
                        return data["id"], data["webUrl"]
                    raise Exception("Coundn't get site id or web url for '{}' site".format(sitePath))

    def getDrivesId(self, siteId, documentLibrary):
        url = self.baseUrl + "/sites/" + siteId + "/drives"
        success = False
        retry = 1
        while not success:
            try:
                response = self.session.get(url, headers=self.headers)
            except:
                logging.error('Connection Error. Trying to reconnect.')
                self.renewAccessToken()
            else:
                if response.status_code != 200:
                    logging.error('Error status_code = {}. Trying to renew access token.'.format(response.status_code))
                    self.renewAccessToken()
                    retry += 1
                    if retry > 4:
                        raise_for_error(response)
                else:
                    success = True
                    values = response.json()["value"]
                    for value in values:
                        if "name" in value:
                            if documentLibrary == value["name"]:
                                return value["id"], value["webUrl"]
                    raise Exception("Coundn't find specified '{}' documentLibrary in sharepoint for site '{}'".format(
                        documentLibrary, siteId))

    def getDrivesIdByWebUrl(self, siteId, webUrl):
        url = self.baseUrl + "/sites/" + siteId + "/drives"
        success = False
        retry = 1
        while not success:
            try:
                response = self.session.get(url, headers=self.headers)
            except:
                logging.error('Connection Error. Trying to reconnect.')
                self.renewAccessToken()
            else:
                if response.status_code != 200:
                    logging.error('Error status_code = {}. Trying to renew access token.'.format(response.status_code))
                    self.renewAccessToken()
                    retry += 1
                    if retry > 4:
                        raise_for_error(response)
                else:
                    success = True
                    values = response.json()["value"]
                    for value in values:
                        if "webUrl" in value:
                            if webUrl == unquote(value["webUrl"]):
                                return value["id"]
                    raise Exception("Coundn't find '{}' documentLibrary for site '{}'".format(webUrl, siteId))

    def getDriveDownloadUrl(self, siteId, driveId, fileName, lastUpdatedDate=False):
        url = self.baseUrl + "/sites/" + siteId + "/drives/" + driveId + "/root/children"
        success = False
        while not success:
            try:
                response = self.session.get(url, headers=self.headers)
            except:
                logging.error('Connection Error. Trying to reconnect.')
                self.renewAccessToken()
            else:
                if response.status_code != 200:
                    logging.error('Error status_code = {}. Trying to renew access token.'.format(response.status_code))
                    self.renewAccessToken()
                    # raise_for_error(response)
                else:
                    success = True
                    fileExist = False
                    values = response.json()["value"]
                    for value in values:
                        if "name" in value:
                            if fileName == value["name"]:
                                fileExist = True
                                if lastUpdatedDate:
                                    if lastUpdatedDate < datetime.strptime(value["lastModifiedDateTime"],
                                                                           "%Y-%m-%dT%H:%M:%SZ"):
                                        driveDownloadUrl = value["@microsoft.graph.downloadUrl"]
                                        return driveDownloadUrl
                                else:
                                    driveDownloadUrl = value["@microsoft.graph.downloadUrl"]
                                    return driveDownloadUrl
                    if not fileExist:
                        raise Exception(
                            "Coundn't find specified '{}' file for drive {} of site '{}' in sharepoint".format(fileName,
                                                                                                               driveId,
                                                                                                               siteId))
                    return False

    def getDriveDownloadUrlByPath(self, driveId, itemPath, lastUpdatedDate=False):
        url = self.baseUrl + "/drives/" + driveId + "/root:/{}".format(itemPath)
        success = False
        retry = 1
        while not success:
            try:
                response = self.session.get(url, headers=self.headers)
            except:
                logging.error('Connection Error. Trying to reconnect.')
                self.renewAccessToken()
            else:
                if response.status_code != 200:
                    logging.error(
                        "Error status_code = {}. Coundn't find '{}' file in sharepoint or another error. Trying to renew access token.".format(
                            response.status_code, itemPath))
                    self.renewAccessToken()
                    retry += 1
                    if retry > 4:
                        raise_for_error(response)
                else:
                    success = True
                    fileExist = False
                    data = response.json()
                    if "@microsoft.graph.downloadUrl" in data:
                        fileExist = True
                        if lastUpdatedDate:
                            if lastUpdatedDate < datetime.strptime(data["lastModifiedDateTime"], "%Y-%m-%dT%H:%M:%SZ"):
                                driveDownloadUrl = data["@microsoft.graph.downloadUrl"]
                                fileDetails = {
                                    "FileCreatedDate": data["createdDateTime"],
                                    "FileModifieDate": data["lastModifiedDateTime"],
                                    "FileCreatedBy": data["createdBy"]["user"]["displayName"],
                                    "FileModifiedBy": data["lastModifiedBy"]["user"]["displayName"]
                                }
                                return driveDownloadUrl, fileDetails
                        else:
                            driveDownloadUrl = data["@microsoft.graph.downloadUrl"]
                            fileDetails = {
                                "FileCreatedDate": data["createdDateTime"],
                                "FileModifiedDate": data["lastModifiedDateTime"],
                                "FileCreatedBy": data["createdBy"]["user"]["displayName"],
                                "FileModifiedBy": data["lastModifiedBy"]["user"]["displayName"]
                            }
                            return driveDownloadUrl, fileDetails
                    if not fileExist:
                        raise Exception("Coundn't find '{}' file in sharepoint".format(itemPath))
                    return False

    def getFileAndFolderItems(self, siteId, driveId, lastUpdatedDate=False):
        url = self.baseUrl + "/sites/" + siteId + "/drives/" + driveId + "/root/children"
        success = False
        fileItemsInfo = []
        folderItemsInfo = []
        while not success:
            try:
                response = self.session.get(url, headers=self.headers)
            except:
                logging.error('Connection Error. Trying to reconnect.')
                self.renewAccessToken()
            else:
                if response.status_code != 200:
                    logging.error('Error status_code = {}. Trying to renew access token.'.format(response.status_code))
                    self.renewAccessToken()
                    # raise_for_error(response)
                else:
                    success = True
                    values = response.json()["value"]
                    for value in values:
                        if "file" in value:
                            fileItemsInfo.append(value)
                        elif "folder" in value:
                            folderItemsInfo.append(value)
        return fileItemsInfo, folderItemsInfo


    def getLists(self, siteId):
        url = self.baseUrl + "/sites/" + siteId + "/lists"
        success = False
        while not success:
            try:
                response = self.session.get(url, headers={"content-type": "application/json",
                                                          "Authorization": "Bearer " + self.accessToken})
            except:
                logging.error('Connection Error. Trying to reconnect.')
                self.renewAccessToken()
            else:
                if response.status_code != 200:
                    logging.error('Error status_code = {}. Trying to renew access token.'.format(response.status_code))
                    self.renewAccessToken()
                    # raise_for_error(response)
                else:
                    success = True
                    logging.info("Received lists")
                    return response.json()["value"]

    def getItems(self, siteId, listName):
        listValues = self.getLists(siteId)
        listId = None
        for listValue in listValues:
            if listValue["name"] == listName:
                listId = listValue["id"]
                break

        if listId:
            urlItems = self.baseUrl + "/sites/" + siteId + "/lists/" + listId + "/items?expand=fields"
            success = False
            totalItems = []
            while not success:
                try:
                    resultItems = self.session.get(urlItems, headers={"content-type": "application/json",
                                                                      "Authorization": "Bearer " + self.accessToken})
                except:
                    logging.error('Connection Error. Trying to reconnect.')
                    self.renewAccessToken()
                else:
                    if resultItems.status_code != 200:
                        logging.error(
                            'Error status_code = {}. Trying to renew access token.'.format(resultItems.status_code))
                        self.renewAccessToken()
                        # raise_for_error(response)
                    else:
                        data = resultItems.json()
                        if "@odata.nextLink" in data:
                            urlItems = data["@odata.nextLink"]
                            success = False
                        else:
                            success = True
                        items = data["value"]
                        totalItems = totalItems + items
            return totalItems
        else:
            raise Exception("Coundn't find specified list '{}' in site".format(listName))

    def download_file(self, url, filename=False, verbose=False, file_size=None):
        """ Download file with progressbar """
        local_filename = get_abs_path(filename)
        success = False
        while not success:
            try:
                r = self.session.get(url, stream=True)
                if r.status_code != 200:
                    success = False
                    logging.info("Response status code is not 200 while downloading the file, trying again")

                elif r.status_code == 200:
                    if not file_size:
                        file_size = int(r.headers['Content-Length'])
                    chunk = 1
                    chunk_size = 1024
                    num_bars = int(file_size / chunk_size)
                    if verbose:
                        logging.info(dict(file_size=file_size))
                        logging.info(dict(num_bars=num_bars))

                    with open(local_filename, 'wb') as fp:
                        for chunk in tqdm.tqdm(
                                r.iter_content(chunk_size=chunk_size)
                                , total=num_bars
                                , unit='KB'
                                , desc=local_filename
                                , leave=True  # progressbar stays
                        ):
                            fp.write(chunk)
                    success = True
                    return True
            except:
                success = True
                logging.info("Exception has occured while downloading the file, trying again")
        return False

    def upload_file(self, driveId, data, itemId = '', parentID = '', filename = ''):
        if itemId:
            url = self.baseUrl + "/drives/" + driveId + "/items/" + itemId + "/content"
        elif parentID:
            url = self.baseUrl + "/drives/" + driveId + "/items/" + parentID + ":/" + filename + ":/content"
        else:
            raise Exception("Could not find itemId or parentId for uploading file")
        success = False
        retry = 1
        result = {}
        while not success:
            try:
                response = self.session.put(url,
                        headers={"Content-Type": "text/plain", "Authorization": "Bearer " + self.accessToken},
                        data=data)
            except:
                logging.error('Connection Error. Trying to reconnect.')
                self.renewAccessToken()
            else:
                if response.status_code == 401:
                    logging.error('Error status_code = {}. Trying to renew access token.'.format(response.status_code))
                    self.renewAccessToken()
                elif response.status_code == 200 or response.status_code == 201:
                    success = True
                    result = response.json()
                else:
                    logging.error('Error status_code = {}.'.format(response.status_code))
                    # self.renewAccessToken()
                    raise_for_error(response)
        return result