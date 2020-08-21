#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from sonarqube.config import (
    API_MEASURES_COMPONENT_ENDPOINT,
    API_MEASURES_COMPONENT_TREE_ENDPOINT,
    API_MEASURES_SEARCH_HISTORY_ENDPOINT
)


class SonarQubeMeasure:
    default_metricKeys = 'code_smells,bugs,vulnerabilities,new_bugs,new_vulnerabilities,\
new_code_smells,coverage,new_coverage'

    def __init__(self, sonarqube):
        self.sonarqube = sonarqube

    def get_measures_component(self, component, branch, additionalFields=None, metricKeys=None):
        """
        Return component with specified measures.
        :param metricKeys:Comma-separated list of metric keys. such as: ncloc,complexity,violations
        :param component: Component key
        :param branch:
        :param additionalFields: Comma-separated list of additional fields that can be returned in the response.
          such as: metrics,periods
        :return:
        """
        params = {
            'metricKeys': metricKeys or self.default_metricKeys,
            'component': component,
            'branch': branch
        }
        if additionalFields:
            params['additionalFields'] = additionalFields

        resp = self.sonarqube.make_call('get', API_MEASURES_COMPONENT_ENDPOINT, **params)
        data = resp.json()
        return data

    def get_measures_component_tree(self, component_key, metricKeys=None, **kwargs):
        """
        Navigate through components based on the chosen strategy with specified measures. The baseComponentId or
        the component parameter must be provided.
        :param component_key: Component key.
        :param metricKeys: Comma-separated list of metric keys. such as: ncloc,complexity,violations
        :param kwargs:
        additionalFields: Comma-separated list of additional fields that can be returned in the response.
          such as: metrics,periods
        asc: Ascending sort
        metricPeriodSort: Sort measures by leak period or not ?. The 's' parameter must contain the 'metricPeriod' value
        metricSort: Metric key to sort by. The 's' parameter must contain the 'metric' or 'metricPeriod' value.
          It must be part of the 'metricKeys' parameter
        metricSortFilter: Filter components. Sort must be on a metric. Possible values are:
          * all: return all components
          * withMeasuresOnly: filter out components that do not have a measure on the sorted metric
        p: 1-based page number, default value is 1
        ps: Page size. Must be greater than 0 and less or equal than 500, default value is 100
        q: Limit search to:
          * component names that contain the supplied string
          * component keys that are exactly the same as the supplied string
        qualifiers:Comma-separated list of component qualifiers. Filter the results with
        the specified qualifiers. Possible values are:
        * BRC - Sub-projects
        * DIR - Directories
        * FIL - Files
        * TRK - Projects
        * UTS - Test Files
        s: Comma-separated list of sort fields,such as: name, path, qualifier, metric, metricPeriod.
          and default value is name
        strategy: Strategy to search for base component descendants:
          * children: return the children components of the base component. Grandchildren components are not returned
          * all: return all the descendants components of the base component. Grandchildren are returned.
          * leaves: return all the descendant components (files, in general) which don't have other children.
            They are the leaves of the component tree.
        :return:
        """
        params = {
            'component': component_key,
            'metricKeys': metricKeys or self.default_metricKeys,
        }
        if kwargs:
            self.sonarqube.copy_dict(params, kwargs)

        page_num = 1
        page_size = 1
        total = 2

        while page_num * page_size < total:
            resp = self.sonarqube.make_call('get', API_MEASURES_COMPONENT_TREE_ENDPOINT, **params)
            response = resp.json()

            page_num = response['paging']['pageIndex']
            page_size = response['paging']['pageSize']
            total = response['paging']['total']

            params['p'] = page_num + 1

            for component in response['components']:
                yield component

    def get_measures_history(self, component, branch, metrics=None, from_date=None, to_date=None):
        """
        Search measures history of a component
        :param component:
        :param branch:
        :param metrics: Comma-separated list of metric keys.such as: ncloc,coverage,new_violations
        :param from_date: Filter measures created after the given date (inclusive).
          Either a date (server timezone) or datetime can be provided
        :param to_date: Filter measures created before the given date (inclusive).
          Either a date (server timezone) or datetime can be provided
        :return:
        """
        params = {
            'metrics': metrics or self.default_metricKeys,
            'component': component,
            'branch': branch
        }

        if from_date:
            params['from'] = from_date

        if to_date:
            params['to'] = to_date

        page_num = 1
        page_size = 1
        total = 2

        while page_num * page_size < total:
            resp = self.sonarqube.make_call('get', API_MEASURES_SEARCH_HISTORY_ENDPOINT, **params)
            response = resp.json()

            page_num = response['paging']['pageIndex']
            page_size = response['paging']['pageSize']
            total = response['paging']['total']

            params['p'] = page_num + 1

            for measure in response['measures']:
                yield measure
