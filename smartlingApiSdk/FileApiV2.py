#!/usr/bin/python
# -*- coding: utf-8 -*-


''' Copyright 2012 Smartling, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this work except in compliance with the License.
 * You may obtain a copy of the License in the LICENSE file, or at:
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

#FileApi class implementation

from HttpClient import HttpClient
from MultipartPostHandler import MultipartPostHandler
from Constants import Uri, Params, ReqMethod
from ApiResponse import ApiResponse
from AuthClient import AuthClient
from UrlV2Helper import UrlV2Helper


"""
Upload File - /files-api/v2/projects/{projectId}/file (POST)
Download Original File - /files-api/v2/projects/{projectId}/file (GET)
Download Translated File - Single Locale - /files-api/v2/projects/{projectId}/locales/{localeId}/file (GET)
Download Translated Files - Multiple Locales as .ZIP - /files-api/v2/projects/{projectId}/files/zip (GET)
Download Translated File - All Locales as .ZIP - /files-api/v2/projects/{projectId}/locales/all/file/zip (GET)
Download Translated File - All Locales in one File - CSV - /files-api/v2/projects/{projectId}/locales/all/file (GET)
List Files - /files-api/v2/projects/{projectId}/files/list (GET)
List File Types - /files-api/v2/projects/{projectId}/file-types (GET)
Status - All Locales - /files-api/v2/projects/{projectId}/file/status (GET)
Status - Single Locale / Extended Response - /files-api/v2/projects/{projectId}/locales/{localeId}/file/status (GET)
Rename - /files-api/v2/projects/{projectId}/file/rename (POST)
Delete - /files-api/v2/projects/{projectId}/file/delete (POST)
Last Modified (by locale) - /files-api/v2/projects/{projectId}/locales/{localeId}/file/last-modified (GET)
Last Modified (all locales) - /files-api/v2/projects/{projectId}/file/last-modified (GET)
Import Translations - /files-api/v2/projects/{projectId}/locales/{localeId}/file/import (POST or PUT)
List Authorized Locales - /files-api/v2/projects/{projectId}/file/authorized-locales (GET)
Authorize - /files-api/v2/projects/{projectId}/file/authorized-locales (PUT / POST)
Unauthorize - /files-api/v2/projects/{projectId}/file/authorized-locales (DELETE)
Get Translations - /files-api/v2/projects/{projectId}/locales/{localeId}/file/get-translations (POST)
"""

class FileApiV2:
    """ basic class implementing low-level api calls """
    response_as_string = False

    def __init__(self, host, userIdentifier, userSecret, projectId, proxySettings=None):
        self.host = host
        self.userIdentifier = userIdentifier
        self.userSecret = userSecret
        self.projectId = projectId
        self.proxySettings = proxySettings
        self.httpClient = HttpClient(host, proxySettings)
        self.authClient = AuthClient(userIdentifier, userSecret, proxySettings)
        self.urlHelper = UrlV2Helper(self.projectId)

    def uploadMultipart(self, uri, params, response_as_string=False):
        if params.has_key(Params.FILE_PATH):
            params[Params.FILE] = open(params[Params.FILE_PATH], 'rb')
            del params[Params.FILE_PATH]  # no need in extra field in POST

        authHeader = self.getAuthHeader()  
        response_data, status_code = self.getHttpResponseAndStatus(ReqMethod.POST ,uri, params, MultipartPostHandler, extraHeaders = authHeader)
        response_data = response_data.strip()
        if self.response_as_string or response_as_string:
            return response_data, status_code
        return ApiResponse(response_data, status_code), status_code
  
    def getHttpResponseAndStatus(self, method, uri, params, handler=None, extraHeaders = None):
        return self.httpClient.getHttpResponseAndStatus(method, uri, params, handler, extraHeaders = extraHeaders)
  
    def getAuthHeader(self):
        token = self.authClient.getToken()
        if token is None:
            raise "Error getting token"
            
        return {"Authorization" : "Bearer "+ token} 
   
    def command_raw(self, method, uri, params):
        authHeader = self.getAuthHeader()
        return self.getHttpResponseAndStatus(method, uri, params, extraHeaders = authHeader)

    def command(self, method, uri, params):
        data, code = self.command_raw(method, uri, params)
        if self.response_as_string:
            return data, code
        return  ApiResponse(data, code), code


#-----------------------------------------------------------------------------------

    def commandGet(self, fileUri, locale, **kw):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/Download-File/Single-Locale/ """
        kw[Params.FILE_URI] = fileUri
 
        if Params.RETRIEVAL_TYPE in kw and not kw[Params.RETRIEVAL_TYPE] in Params.allowedRetrievalTypes:
            raise "Not allowed value `%s` for parameter:%s try one of %s" % (kw[Params.RETRIEVAL_TYPE],
                                                                             Params.RETRIEVAL_TYPE,
                                                                             Params.allowedRetrievalTypes)
        url = self.urlHelper.getUrl(self.urlHelper.GET, localeId=locale)
        return self.command_raw(ReqMethod.GET, url, kw)


    def commandGetMultipleLocalesAsZip(self, fileUri, localeIds, **kw):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/Download-File/Multiple-Locales/ """
        kw[Params.FILE_URIS] = fileUri
        kw[Params.LOCALE_IDS] = localeIds
 
        if Params.RETRIEVAL_TYPE in kw and not kw[Params.RETRIEVAL_TYPE] in Params.allowedRetrievalTypes:
            raise "Not allowed value `%s` for parameter:%s try one of %s" % (kw[Params.RETRIEVAL_TYPE],
                                                                             Params.RETRIEVAL_TYPE,
                                                                             Params.allowedRetrievalTypes)
        
        
        return self.command_raw(ReqMethod.GET, self.urlHelper.getUrl(self.urlHelper.GET_MULTIPLE_LOCALES), kw)

 
 
 
    def commandGetAllLocalesZip(self, fileUri, **kw):
         """ http://docs.smartling.com/pages/API/v2/FileAPI/Download-File/All-Locales """
         kw[Params.FILE_URI] = fileUri
  
         if Params.RETRIEVAL_TYPE in kw and not kw[Params.RETRIEVAL_TYPE] in Params.allowedRetrievalTypes:
             raise "Not allowed value `%s` for parameter:%s try one of %s" % (kw[Params.RETRIEVAL_TYPE],
                                                                              Params.RETRIEVAL_TYPE,
                                                                              Params.allowedRetrievalTypes)

         url = self.urlHelper.getUrl(self.urlHelper.GET_ALL_LOCALES_ZIP)
         
         return self.command_raw(ReqMethod.GET, url, kw)
        

    def commandGetAllLocalesCsv(self, fileUri, **kw):
         """  http://docs.smartling.com/pages/API/v2/FileAPI/Download-File/All-Locales-CSV """
         kw[Params.FILE_URI] = fileUri
  
         if Params.RETRIEVAL_TYPE in kw and not kw[Params.RETRIEVAL_TYPE] in Params.allowedRetrievalTypes:
             raise "Not allowed value `%s` for parameter:%s try one of %s" % (kw[Params.RETRIEVAL_TYPE],
                                                                              Params.RETRIEVAL_TYPE,
                                                                              Params.allowedRetrievalTypes)

         url = self.urlHelper.getUrl(self.urlHelper.GET_ALL_LOCALES_CSV)
         return self.command_raw(ReqMethod.GET, url, kw)


    def commandGetOriginal(self, fileUri):
         """  http://docs.smartling.com/pages/API/v2/FileAPI/Download-File/Original-File/ """
         kw = {}
         kw[Params.FILE_URI] = fileUri
  
         url = self.urlHelper.getUrl(self.urlHelper.GET_ORIGINAL)
         return self.command_raw(ReqMethod.GET, url, kw)            

    def commandList(self, **kw):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/List/ """
        url = self.urlHelper.getUrl(self.urlHelper.LIST_FILES)
        return self.command(ReqMethod.GET, url, kw)
        
    def commandListFileTypes(self, **kw):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/List-File-Types/ """
        return self.command(ReqMethod.GET, self.urlHelper.getUrl(self.urlHelper.LIST_FILE_TYPES), kw)


    def commandUpload(self, uploadData):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/Upload-File/ """
        params = {
                    Params.FILE_URI: uploadData.uri or uploadData.name,
                    Params.FILE_TYPE: uploadData.type,
                    Params.FILE_PATH: uploadData.path + uploadData.name
                  }

        if (uploadData.callbackUrl):
            params[Params.CALLBACK_URL] = uploadData.callbackUrl

        if (uploadData.directives):
            for index, directive in enumerate(uploadData.directives):
                params[directive.sl_prefix + directive.name] = directive.value
                
        if (uploadData.localesToApprove):
            for index, locale in enumerate(uploadData.localesToApprove):
                params['{0}[{1}]'.format(Params.LOCALES_TO_APPROVE, index)] = locale

        url = self.urlHelper.getUrl(self.urlHelper.UPLOAD)
        return self.uploadMultipart(url, params)
        
    def commandProjectDetails(self):    
        """ http://docs.smartling.com/pages/API/v2/Projects/Project-Details/ """
        kw = {}
        url = self.urlHelper.getUrl(self.urlHelper.PROJECT_DETAILS)
        return self.command(ReqMethod.GET, url, kw)
        
    def commandProjects(self, accountUid):    
        """ http://docs.smartling.com/pages/API/v2/Projects/List-Projects/ """
        kw = {}
        url = self.urlHelper.getUrl(self.urlHelper.PROJECTS, accountUid = accountUid)
        return self.command(ReqMethod.GET, url, kw)
        

    def commandDelete(self, fileUri, **kw):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/Delete/ """
        kw[Params.FILE_URI] = fileUri
        uri = self.urlHelper.getUrl(self.urlHelper.DELETE)

        return self.command(ReqMethod.POST, uri, kw)
        
    def commandStatus(self, fileUri):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/Status/All-Locales/ """
        kw = {}
        kw[Params.FILE_URI] = fileUri
        url = self.urlHelper.getUrl(self.urlHelper.STATUS_ALL)
        return self.command(ReqMethod.GET, url, kw)
        
    def commandStatusLocale(self, fileUri, localeId):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/Status/Single-Locale/ """
        kw = {}
        kw[Params.FILE_URI] = fileUri
        url = self.urlHelper.getUrl(self.urlHelper.STATUS_LOCALE, localeId = localeId)
        return self.command(ReqMethod.GET, url, kw)     
            
    def commandRename(self, fileUri, newFileUrl):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/Rename/ """
        kw = {}
        kw[Params.FILE_URI] = fileUri
        kw[Params.FILE_URI_NEW] = newFileUrl
        url = self.urlHelper.getUrl(self.urlHelper.RENAME)
        return self.command(ReqMethod.POST, url, kw)

    def commandLastModified(self, fileUri, localeId, **kw):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/Last-Modified/Single-Locale/ """
        kw[Params.FILE_URI] = fileUri
        url = self.urlHelper.getUrl(self.urlHelper.LAST_MODIFIED, localeId = localeId)
        return self.command(ReqMethod.GET, url, kw) 

    def commandLastModifiedAll(self, fileUri, **kw):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/Last-Modified/All-Locales/ """
        kw[Params.FILE_URI] = fileUri
        url = self.urlHelper.getUrl(self.urlHelper.LAST_MODIFIED_ALL)
        return self.command(ReqMethod.GET, url, kw) 

    def commandImport(self, uploadData, localeId, **kw):
        kw[Params.FILE_URI]  = uploadData.uri
        kw[Params.FILE_TYPE] = uploadData.type
        kw[Params.FILE_PATH] = uploadData.path + uploadData.name
        kw["file"] = uploadData.path + uploadData.name + ";type=text/plain"

        url = self.urlHelper.getUrl(self.urlHelper.IMPORT, localeId = localeId)
        return self.uploadMultipart(url, kw)

    def commandListAuthorizedLocales(self, fileUri):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/Authorize-Content/List-Authorized-Locales/ """
        kw = {}
        kw[Params.FILE_URI] = fileUri
        url = self.urlHelper.getUrl(self.urlHelper.LIST_AUTHORIZED_LOCALES)
        return self.command(ReqMethod.GET, url, kw) 

    def commandAuthorize(self, fileUri, localeIds):
        """ http://docs.smartling.com/pages/API/v2/FileAPI/Authorize-Content/Authorize/ """
        kw = {}
        kw[Params.FILE_URI] = fileUri
        kw[Params.LOCALE_IDS_BRACKET] = ",".join(localeIds)
        url = self.urlHelper.getUrl(self.urlHelper.AUTHORIZE)
        return self.command(ReqMethod.POST, url, kw)
        
    def commandUnauthorize(self, fileUri, localeIds):
        """  http://docs.smartling.com/pages/API/v2/FileAPI/Authorize-Content/Unauthorize/ """
        kw = {}
        kw[Params.FILE_URI] = fileUri
        kw[Params.LOCALE_IDS_BRACKET] = ",".join(localeIds)
        url = self.urlHelper.getUrl(self.urlHelper.UNAUTHORIZE)
        return self.command(ReqMethod.DELETE, url, kw)
        
    def commandGetTranslations(self, uploadData, localeId, **kw):
        """  http://docs.smartling.com/pages/API/v2/FileAPI/Get-Translations/ """
        kw[Params.FILE_URI]  = uploadData.uri
        kw[Params.FILE_PATH] = uploadData.path + uploadData.name
        kw["file"] = uploadData.path + uploadData.name + ";type=text/plain"

        url = self.urlHelper.getUrl(self.urlHelper.GET_TRANSLATIONS, localeId = localeId)
        return self.uploadMultipart(url, kw, response_as_string=True)       
       