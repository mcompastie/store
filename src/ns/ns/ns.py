# -*- coding: utf-8 -*-

#  Copyright (c) 2017 SHIELD, UBIWHERE
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SHIELD, UBIWHERE nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# This work has been performed in the framework of the SHIELD project,
# funded by the European Commission under Grant number 700199 through the
# Horizon 2020 program. The authors would like to acknowledge the contributions
# of their colleagues of the SHIELD partner consortium (www.shield-h2020.eu).


import logging

import os
import yaml
from shutil import rmtree
from storeutils import tar_package, exceptions
from tempfile import gettempdir, mkdtemp
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

PKG_MISSING_FILE = 'No package provided'
PKG_NOT_TARGZ = 'Package is not a valid .tar.gz file'
PKG_NOT_SHIELD = 'Package does not comply with the SHIELD format'


class NsMissingPackage(exceptions.ExceptionMessage):
    """Network Service package not provided."""


class NsWrongPackageFormat(exceptions.ExceptionMessage):
    """Network Service package file is not in .tar.gz format."""


class NsPackageCompliance(exceptions.ExceptionMessage):
    """Network Service package contents do not comply with the definition."""


class NsHelper:
    def __init__(self, vnsfo, logger=None):
        self.logger = logger or logging.getLogger(__name__)

        # Maintenance friendly.
        self._missing_package = NsMissingPackage(PKG_MISSING_FILE)
        self._wrong_package_format = NsWrongPackageFormat(PKG_NOT_TARGZ)
        self._package_compliance = NsPackageCompliance(PKG_NOT_SHIELD)

        self.vnsfo = vnsfo

    def onboard_ns(self, tenant_id, ns_package):
        """
        Registers a Network Service into the Store and onboards it with the Orchestrator.

        The SHIELD manifest is checked for integrity and compliance. Metadata is stored for the catalogue and the actual
        manifest file is stored as binary so it can be provided for attestation purposes (thus ensuring
        tamper-proofing).

        :param tenant_id: the tenant identifier to onboard the Network Service.
        :param ns_package: the package to onboard (as files MultiDict field from
        http://werkzeug.pocoo.org/docs/0.12/wrappers/#werkzeug.wrappers.BaseRequest).

        :return:    the manifest file as a FileStorage stream (
        http://werkzeug.pocoo.org/docs/0.12/datastructures/#werkzeug.datastructures.FileStorage).
                    the package metadata as a dictionary.
        """

        self.logger.info("Onboard Network Service from package '%s'", ns_package.filename)

        # Ensure it's a SHIELD Network Service package.
        extracted_package_path, manifest_path = self._extract_package(ns_package)

        # Get the SHIELD manifest data.
        with open(manifest_path, 'r') as stream:
            manifest = dict(yaml.safe_load(stream))
            self.logger.debug('SHIELD manifest\n%s', manifest)

        self.logger.debug('shield package: %s', os.listdir(extracted_package_path))
        self.logger.debug('osm package: %s | path: %s', manifest['manifest:ns']['package'],
                          os.path.join(extracted_package_path, manifest['manifest:ns'][
                              'package']))

        # Onboard the Network Service into the actual Orchestrator.
        # NOTE: any exception raised by the vNSFO must be handled by the caller, hence no try/catch here.
        onboarded_package = self.vnsfo.onboard_ns(tenant_id,
                                                  os.path.join(extracted_package_path,
                                                               manifest['manifest:ns']['package']),
                                                  manifest['manifest:ns']['descriptor'])

        # Provide the manifest as a file stream.
        stream = open(manifest_path, 'rb')
        manifest_fs = FileStorage(stream)

        # Build the Network Service package metadata.
        package_data = dict()
        package_data['state'] = 'sandboxed'
        package_data['manifest'] = manifest
        package_data['descriptor'] = onboarded_package['descriptor']

        if os.path.isdir(extracted_package_path):
            rmtree(extracted_package_path)

        return manifest_fs, package_data

    def _extract_package(self, package_file):
        """
        Ensures the Network Service package is compliant. The package is stored locally so it's contents can be
        processed.

        :param package_file: The package to onboard (as files MultiDict field from
        http://werkzeug.pocoo.org/docs/0.12/wrappers/#werkzeug.wrappers.BaseRequest).

        :return:  extracted package absolute file system path;
                  SHIELD manifest absolute file system path.
        """

        if package_file and package_file.filename == '':
            self.logger.info('No package file provided in POST')
            raise self._missing_package

        filename = secure_filename(package_file.filename)
        package_absolute_path = os.path.join(gettempdir(), filename)

        try:
            package_file.save(package_absolute_path)

            if not tar_package.is_tar_gz_file(package_absolute_path):
                self.logger.error(PKG_NOT_TARGZ)
                raise self._wrong_package_format

            self.logger.debug("Package stored at '%s'", package_absolute_path)

            extracted_package_path = mkdtemp()

            tar_package.extract_package(package_absolute_path, extracted_package_path)

            # Get the SHIELD manifest data.
            manifest_path = os.path.join(extracted_package_path, 'manifest.yaml')
            if not os.path.isfile(manifest_path):
                self.logger.error("Missing 'manifest.yaml' from %s", extracted_package_path)
                self.logger.error('Package contents: %s', os.listdir(extracted_package_path))
                raise self._package_compliance

        finally:
            os.remove(package_absolute_path)

        return extracted_package_path, manifest_path
