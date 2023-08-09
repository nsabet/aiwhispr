# AIWhispr

## Note : We are working on a release (Version:GoldenWattle) tested on AWS,Azure with some new features.This will be available on 13 August 2023, 5 PM AEST.

## Overview
AIWhispr is a semantic search engine that  
- is easy to install,
- aims for fast semantic response to search queries,
- can ingest  multiple file types, data sources(on OS,Cloud) with simple configuration.

## Contact
contact@aiwhispr.com

## Prerequisite software, python packages 

### Download Typesense and install
AIWhispr uses Typesense to store text, corresponding vector embeddings created by the LLM.
A big Thanks!! to the Typesense team, community. 
We tried many different vector databases, testing for both high speed text and vector search.
All of them are good, but we found Typesense the easiest to work with and delivering great performance.

You can follow the instructions on 
https://typesense.org/docs/guide/install-typesense.html

### Configure Typesense for aiwhispr
Run the below setup commands [ Example is for Ubuntu Linux.]

```
sudo vi /etc/typesense/typesense-server.ini 
```
Open the configuration file for typesense server
You will see the contents similar to 

```
; Typesense Configuration

[server]

api-address = 0.0.0.0
api-port = 8108
data-dir = /var/lib/typesense
api-key = <TYPESENSE_ADMIN_API_KEY>
log-dir = /var/log/typesense
```

Store the <TYPESENSE_ADMIN_API_KEY> safely. You will need this later to setup the schema for the vector database.

Confirm that the typsesense-server is enabled
```
sudo systemctl status typesense-server.service

```
Restart the typsesense-server 
```
sudo systemctl  stop  typesense-server.service
sudo systemctl  start typesense-server.service
```
Open the Typesense-Server port on Linux firewall if you have setup a seprate machine to host typesense-server.
```
sudo ufw allow 8108
```
Check the health status of typesense-server
```
curl http://localhost:8108/health
```

install the typesense client
```
pip3 install typesense
```
### Prerequisite Python packages

###Azure
```
pip install azure-storage-blob 
pip install azure-identity
```

###SpaCy
```
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
pip install spacy-language-detection
```

###AWS
```
pip install boto3 
```

###shutil to copy local files,Document Reader which will extract text from different document types
```
pip install shutil
pip install pypdf
pip install textract
```

###LLM Model Libraries
```
pip install -U sentence-transformers
```

###Flask to run the searchService endpoint via a web interface
```
pip install flask
```

##Environment variables
You can setup the AIWHISPR_HOME_DIR environment variable 

##Security of AIWhispr config files
Configuration files for each content site is stored under $AIWHISPR_HOME_DIR/config/sites-available/
The config files that AIWhispr reads contains the access keys , so please ensure that these config files don't have public read access.Also ensure that these config files are not managed under a public source code repository.

    
## Design guidelines to keep in mind when contributing source code 
- The software should be easy to install.Installations instructions shoule be easy to read, simple to execute.
- The configuration names should recognizable for the audience (developer/system administrator/user) who will be configuring the value.    
- A semantic search engine should have fast response times for search queries. Take more time for data preparation, indexing if it helps improve the search response time.
- A semantic search engine should be able to ingest content from both on OS, cloud (e.g. Azure Blob, AWS S3 ) with simple configuration, no code changes.
- A semantic search engine should be able to ingest multiple file types. If a file type is not handled then code changes should be minimum to add additional support for a file type.
- A semantic search engine should clean the data before it submits it to the LLM for encoding. 
- A semantic search engine should be able to run in multiple levels of logging (DEBUG,CRITICAL,ERROR, INFO) so that developers, system administrators can monitor the health, setup alerts.
- Every feature will be built on community feedback.Feedback from users will define the desired outcome of the feature.


