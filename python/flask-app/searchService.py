from unittest import result
from flask import Flask,redirect, url_for, request
import os
import sys
import json
import math
import string
import re
import logging
import getopt
import configparser
from importlib import import_module

curr_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(curr_dir)
os.getcwd()

sys.path.insert(1, os.path.abspath(os.path.join(curr_dir, os.pardir)))
sys.path.append("../base-classes")
sys.path.append("../llm-service")
sys.path.append("../vectordb")
sys.path.append("../common-functions")
sys.path.append("../common-objects")
from aiwhisprBaseClasses import baseLlmService, vectorDb 

import logging
logging.basicConfig(level = logging.DEBUG,format = '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')


class searchHandler:
   model:baseLlmService
   vector_db:vectorDb
   limit_hits=25
   content_site_name:str
   src_path:str
   src_path_for_results:str
   logger=logging.getLogger(__name__)

   def setup(self,llm_service_module:str, vectordb_module:str, model_family:str, model_name:str, llm_service_api_key:str, vectordb_hostname:str, vectordb_portnumber:str,vectordb_key:str, content_site_name:str,src_path:str,src_path_for_results:str):
      llmServiceMgr = import_module(llm_service_module)
      vectorDbMgr = import_module(vectordb_module)

      self.vector_db = vectorDbMgr.createVectorDb(vectordb_hostname = vectordb_hostname,
                                          vectordb_portnumber = vectordb_portnumber,
                                          vectordb_key = vectordb_key,
                                          content_site_name = content_site_name,
                                          src_path = src_path,
                                          src_path_for_results = src_path_for_results)

      self.vector_db.connect()
      self.content_site_name = content_site_name
      self.src_path = src_path
      self.src_path_for_results = src_path_for_results

      self.model= llmServiceMgr.createLlmService(model_family = model_family,model_name = model_name, llm_service_api_key = llm_service_api_key )
      self.model.connect()

   def search(self,input_query:str, result_format:str): 

      output_format = result_format      
      self.logger.debug("result format: %s", result_format)
      if output_format not in ['html','json']:
         self.logger.debug("cannot handle this result format type")
      
      self.logger.debug("get vector embedding for text:{%s}",input_query)
      query_embedding_vector =  self.model.encode(input_query)
      query_embedding_vector_as_list = query_embedding_vector
      vector_as_string = ' '. join(str(e) for e in query_embedding_vector_as_list)
      self.logger.debug("vector embedding:{%s}",vector_as_string)
      search_results = self.vector_db.search(self.content_site_name,query_embedding_vector_as_list, self.limit_hits)

      #print(search_results)

      no_of_semantic_hits = search_results['results'][0]['found']
      i = 0
      display_html = ''
      display_json = []

      while i < no_of_semantic_hits:
         chunk_map_record = search_results['results'][0]['hits'][i]['document']
         content_site_name = chunk_map_record['content_site_name']
         record_id = chunk_map_record['id']
         content_path = chunk_map_record['content_path']
         src_path = chunk_map_record['src_path']
         src_path_for_results = chunk_map_record['src_path_for_results']
         text_chunk = chunk_map_record['text_chunk']
            

         if output_format == 'html':
            display_url = src_path_for_results + '/' + content_path
            if len(text_chunk) <= 200:
               display_text_chunk = text_chunk
            else:
               display_text_chunk = text_chunk[:197] + '...'
            display_html = display_html + '<a href="' + display_url + '">' + content_path + '</a><br>'
            display_html = display_html + '<div><p>' + display_text_chunk + '</p></div><br>'
            
         if output_format == 'json':
            json_record = {} #Dict
            json_record['content_path'] = content_path
            json_record['id'] = record_id
            json_record['content_site_name'] = content_site_name
            json_record['src_path'] = src_path
            json_record['src_path_for_results'] = src_path_for_results
            json_record['text_chunk'] = text_chunk
            ##Add this dict record in the list
            display_json.append(json_record)
      
         i = i + 1 

      #Return based on result_format
      if output_format == 'json':
         return { 'results': display_json} #Return as dict
      else:
         return display_html
           
         

mySearchHandler = []

def setup(argv):
    configfile=''
    opts, args = getopt.getopt(argv,"hC:",["configfile="])
    for opt, arg in opts:
        if opt == '-h':
            print('vectorEncodingService.py -C <vector_encoding_config_file>' )
            sys.exit()
        elif opt in ("-C", "--configfile"):
            configfile = arg
    #interpolation is set to None to allow reading special symbols like %
    config =  configparser.ConfigParser(interpolation=None)
    config.read(configfile)

    #Read the content site configs
    content_site_name = config.get('content-site','sitename')
    src_path = config.get('content-site','srcpath')
    src_path_for_results = config.get('content-site','displaypath')
    ##VectorDB Service
    vectordb_hostname = config.get('vectordb', 'api-address')
    vectordb_portnumber = config.get('vectordb', 'api-port')
    vectordb_key = config.get('vectordb', 'api-key')
    vectordb_module = config.get('vectordb','vectorDbModule')
    ##LLM Service
    model_family =config.get('llm-service','model-family')
    model_name = config.get('llm-service','model-name')
    llm_service_module = config.get('llm-service', 'llmServiceModule')
    llm_service_api_key = config.get('llm-service', 'llm-service-api-key')
    mySearchHandler[0].setup(llm_service_module, vectordb_module, model_family, model_name, llm_service_api_key, vectordb_hostname, vectordb_portnumber,vectordb_key, content_site_name,src_path,src_path_for_results)

app = Flask(__name__)

@app.route('/')
def say_hello():
   return '<center>Welcome. Your local vector embedding service is up</center>'

#This is the search function that does a semantic vector search
@app.route('/search',methods = ['POST', 'GET'])
def semantic_search():

   if request.method == 'POST':
      input_query = request.form['query']
      result_format = request.form['resultformat']
   else:
      input_query = request.args.get('query')
      result_format = request.args.get('resultformat')
      print("Result Format: " + result_format)
   return mySearchHandler[0].search(input_query, result_format)



### END OF FUNCTION SEARCH

if __name__ == '__main__':
   mySearchHandler.append(searchHandler())
   setup(sys.argv[1:])
   app.run(debug=True,host='127.0.0.1', port=5002)

