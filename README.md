# sharepoint-document-library

This is python script that allows to download files from Sharepoint document library into local directory and upload new files or replace existing files to Sharepoint.

- The code was tested with Python `3.7.7`

## Quick Start

1. Install
    
    Create new virtual environment and activate it:
    ```
    > python3 -m venv ~/.virtualenvs/sharepoint-document-library
    > source ~/.virtualenvs/sharepoint-document-library/bin/activate
    ```

    Clone this repository, and then install it.
    ```
   > git clone https://github.com/RFAInc/sharepoint-document-library.git
   > cd sharepoint-document-library
   > python install setup.py
   > deactivate
    ```
    
2. Create `config.json` file for script and put the following.
    ```
    {
      "tenant_name": "rfalab.com",
      "client_id": "******************",
      "client_secret": "*******************",
      "grant_type": "client_credentials",
      "scope": "https://graph.microsoft.com/.default",
      "site_name": "ExternalDev",
      "document_library": "TestdocsName"
    }
    ```
    Full list of options in `config.json`:
    
    | Property                            | Type    | Required?  | Description                                                   |
    |-------------------------------------|---------|------------|---------------------------------------------------------------|
    | tenant_name                         | String  | Yes        | Directory Tenant (id). You can get it after creating an Enterprise Application on Azure. [for more details](https://towardsdatascience.com/querying-microsoft-graph-api-with-python-269118e8180c)          |
    | client_id                           | String  | Yes        | Application (client) Id. You can get it after creating an Enterprise Application on Azure. [for more details](https://towardsdatascience.com/querying-microsoft-graph-api-with-python-269118e8180c)          |
    | client_secret                       | String  | Yes        | The client secret.          |
    | grant_type                          | String  | Yes        | The grant type.          |
    | scope                               | String  | Yes        | The default scope for graph API         |
    | site_name                           | String  | Yes        | The site name in SharePoint          |
    | document_library                    | String  | Yes        | The document library name in SharePoint site         |

3. Run the script for downloading files from Sharepoint into local directory:
	```
    ~/.virtualenvs/sharepoint-document-library/bin/sharepoint-document-library --config config.json --download_path /path/to/directory/
    ```
4. Run the script for uploading files from local directory into Sharepoint:
	```
    ~/.virtualenvs/sharepoint-document-library/bin/sharepoint-document-library --config config.json --upload_path /path/to/directory/
    ```
