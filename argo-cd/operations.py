"""
Copyright start
MIT License
Copyright (c) 2024 Fortinet Inc
Copyright end
"""

import requests, json
from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('argo-cd')


class ArgoCD(object):
    def __init__(self, config, *args, **kwargs):
        self.api_token = config.get('api_token')
        url = config.get('server_url').strip('/')
        if not url.startswith('https://') and not url.startswith('http://'):
            self.url = 'https://{0}/api/v1'.format(url)
        else:
            self.url = url + '/api/v1'
        self.verify_ssl = config.get('verify_ssl')

    def make_rest_call(self, endpoint, method, data=None, params=None):
        try:
            url = self.url + endpoint
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.api_token
            }
            logger.debug("Endpoint {0}".format(url))
            response = requests.request(method, url, data=data, params=params,
                                        headers=headers, verify=self.verify_ssl)
            logger.debug("response_content {0}:{1}".format(response.status_code, response.content))
            if response.ok or response.status_code == 204:
                logger.info('Successfully got response for url {0}'.format(url))
                if 'json' in str(response.headers):
                    return response.json()
                else:
                    return response
            else:
                logger.error("{0}".format(response.status_code))
                raise ConnectorError("{0}:{1}".format(response.status_code, response.text))
        except requests.exceptions.SSLError:
            raise ConnectorError('SSL certificate validation failed')
        except requests.exceptions.ConnectTimeout:
            raise ConnectorError('The request timed out while trying to connect to the server')
        except requests.exceptions.ReadTimeout:
            raise ConnectorError(
                'The server did not send any data in the allotted amount of time')
        except requests.exceptions.ConnectionError:
            raise ConnectorError('Invalid Credentials')
        except Exception as err:
            raise ConnectorError(str(err))


def check_payload(payload):
    updated_payload = {}
    for key, value in payload.items():
        if isinstance(value, dict):
            nested = check_payload(value)
            if len(nested.keys()) > 0:
                updated_payload[key] = nested
        elif value != '' and value is not None:
            updated_payload[key] = value
    return updated_payload


def create_application(config, params):
    try:
        cd = ArgoCD(config)
        endpoint = '/applications'
        payload = {
            "metadata": {
                "name": params.get('name')
            },
            "spec": {
                "source": params.get('source'),
                "destination": params.get('destination')
            }
        }
        spec = params.get('spec')
        if spec:
            payload['spec'].update(spec)
        metadata = params.get('metadata')
        if metadata:
            payload['metadata'].update(metadata)
        operation = params.get('operation')
        if operation:
            payload.update({'operation': operation})
        additional_properties = params.get('additional_properties')
        if additional_properties:
            payload.update(additional_properties)
        payload = check_payload(payload)
        logger.debug("Payload {0}".format(payload))
        response = cd.make_rest_call(endpoint, 'POST', data=json.dumps(payload))
        return response
    except Exception as err:
        raise ConnectorError(str(err))


def get_applications(config, params):
    try:
        cd = ArgoCD(config)
        endpoint = '/applications'
        query_params = {
            "name": params.get('name'),
            "projects": params.get('projects')
        }
        additional_fields = params.get('additional_fields')
        if additional_fields:
            query_params.update(additional_fields)
        query_params = {k: v for k, v in query_params.items() if v is not None and v != ''}
        logger.debug("Query Parameters {0}".format(query_params))
        response = cd.make_rest_call(endpoint, 'GET', params=query_params)
        return response
    except Exception as err:
        raise ConnectorError(str(err))


def get_application_by_name(config, params):
    try:
        cd = ArgoCD(config)
        endpoint = '/applications/{0}'.format(params.get('name'))
        response = cd.make_rest_call(endpoint, 'GET')
        return response
    except Exception as err:
        raise ConnectorError(str(err))


def update_application(config, params):
    try:
        cd = ArgoCD(config)
        endpoint = '/applications/{0}'.format(params.get('name'))
        payload = {
            "metadata": {
                "name": params.get('name')
            },
            "spec": {
                "source": params.get('source'),
                "destination": params.get('destination')
            }
        }
        spec = params.get('spec')
        if spec:
            payload['spec'].update(spec)
        metadata = params.get('metadata')
        if metadata:
            payload['metadata'].update(metadata)
        operation = params.get('operation')
        if operation:
            payload.update({'operation': operation})
        additional_properties = params.get('additional_properties')
        if additional_properties:
            payload.update(additional_properties)
        payload = check_payload(payload)
        logger.debug("Payload {0}".format(payload))
        response = cd.make_rest_call(endpoint, 'PUT', data=json.dumps(payload))
        return response
    except Exception as err:
        raise ConnectorError(str(err))


def delete_application(config, params):
    try:
        cd = ArgoCD(config)
        endpoint = '/applications/{0}'.format(params.get('name'))
        response = cd.make_rest_call(endpoint, 'DELETE')
        return {"message": "Successfully deleted application: {0}".format(params.get('name'))}
    except Exception as err:
        raise ConnectorError(str(err))


def get_clusters(config, params):
    try:
        cd = ArgoCD(config)
        endpoint = '/clusters'
        query_params = {
            "server": params.get('server'),
            "name": params.get('name')
        }
        query_params = {k: v for k, v in query_params.items() if v is not None and v != ''}
        logger.debug("Query Parameters {0}".format(query_params))
        response = cd.make_rest_call(endpoint, 'GET', params=query_params)
        return response
    except Exception as err:
        raise ConnectorError(str(err))


def check_health(config):
    try:
        response = get_applications(config, params={'additional_properties': ''})
        if response:
            return True
    except Exception as err:
        logger.info(str(err))
        raise ConnectorError(str(err))


operations = {
    'create_application': create_application,
    'get_applications': get_applications,
    'get_application_by_name': get_application_by_name,
    'update_application': update_application,
    'delete_application': delete_application,
    'get_clusters': get_clusters
}
