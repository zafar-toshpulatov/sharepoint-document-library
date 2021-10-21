from sharepoint_document_library.utils import parse_args
from sharepoint_document_library.client import SharePointClient
import logging
from sharepoint_document_library import utils

logging.basicConfig(level = logging.INFO)

REQUIRED_CONFIG_KEYS = [
    'tenant_name',
    'client_id',
    'client_secret',
    'grant_type',
    'scope',
    'site_name'
]

def download_files(client, config, download_path):
    document_library = config.get('document_library', None)
    site_name = config['site_name']
    if document_library:
        site_id, _ = client.getSiteId(site_name)
        drive_id, drive_web_url = client.getDrivesId(site_id, document_library)
        file_items_info, folder_items_info = client.getFileAndFolderItems(site_id, drive_id)
        for file_item_info in file_items_info:
            url = file_item_info["@microsoft.graph.downloadUrl"]
            name = file_item_info["name"]
            file_path = download_path + '/' + name
            file_size = file_item_info["size"]
            client.download_file(url, filename=file_path, file_size=file_size)
            logging.info("'{}' file is downloaded".format(file_path))

    else:
        # TODO: if document library is not specified, get files from all document libraries
        pass

def upload_files(client, config, upload_path, file_name="file3.png"):
    file_names = utils.get_file_names(upload_path)
    document_library = config.get('document_library', None)
    site_name = config['site_name']
    if document_library:
        site_id, _ = client.getSiteId(site_name)
        drive_id, drive_web_url = client.getDrivesId(site_id, document_library)
        file_items_info, folder_items_info = client.getFileAndFolderItems(site_id, drive_id)
        for file_name in file_names:
            for file_item_info in file_items_info:
                if file_item_info["name"] == file_name:
                    item_id = file_item_info["id"]
                    data = utils.open_file(upload_path + file_name)
                    result_item = client.upload_file(drive_id, data, itemId=item_id)
                    logging.info("'{}' existing file is replaced".format(upload_path + file_name))
                    break
            else:
                parent_id = file_item_info["parentReference"]["id"]
                data = utils.open_file(upload_path + file_name)
                result_item = client.upload_file(drive_id, data, parentID=parent_id, filename=file_name)
                logging.info("'{}' new file is uploaded".format(upload_path + file_name))
    # TODO: Implement upload for folders
    # TODO: Implement upload for bigger files (>4mb)

def main():
    parsed_args = parse_args(REQUIRED_CONFIG_KEYS)

    with SharePointClient(parsed_args.config) as client:

        if parsed_args.download_path:
            download_path = parsed_args.download_path
            download_files(client=client,
                           config=parsed_args.config,
                           download_path = download_path)

        elif parsed_args.upload_path:
            upload_path = parsed_args.upload_path

            upload_files(client=client,
                         config=parsed_args.config,
                         upload_path = upload_path)

if __name__ == '__main__':
    main()