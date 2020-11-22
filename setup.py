# Copyright 2019 by Quopt IT Services BV
#
#  Licensed under the Artistic License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    https://raw.githubusercontent.com/Quopt/ITR-webclient/master/LICENSE
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("ITSCache.py")
)
setup (
    ext_modules = cythonize("ITSEncrypt.py")
)
setup (
    ext_modules = cythonize("ITSGit.py")
)
setup (
    ext_modules = cythonize("ITSHelpers.py")
)
setup (    ext_modules = cythonize("ITSJsonify.py")
)
setup (
    ext_modules = cythonize("ITSLogging.py")
)
setup (
    ext_modules = cythonize("ITSMailer.py")
)
setup (
    ext_modules = cythonize("ITSPrefixMiddleware.py")
)
setup (
    ext_modules = cythonize("ITSRestAPIDB.py")
)
setup (
    ext_modules = cythonize("ITSRestAPILogin.py")
)
setup (
    ext_modules = cythonize("ITSRestAPIORM.py")
)
setup (
    ext_modules = cythonize("ITSRestAPIORMExtendedFunctions.py")
)
setup (
    ext_modules = cythonize("ITSRestAPIORMExtensions.py")
)
setup (
    ext_modules = cythonize("ITSRestAPISettings.py")
)
setup (
    ext_modules = cythonize("ITSRestAPITest.py")
)
setup (
    ext_modules = cythonize("ITSTranslate.py")
)
setup (
    ext_modules = cythonize("ITSXMLConversionSupport.py")
)
setup (
    ext_modules = cythonize("application.py")
)
