# -*- Mode: Python; tab-width: 4 -*-

# Copyright (c) 2012 James McKernan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#     * Neither the name of the author nor the names of other
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""common/crypto.py

Utility module for encrypting and decrypting strings. 

Useful for encoding UUIDs for placement in browser cookies.

The underlying mechanism for key control is the keyczar crypto toolkit. Provides
an easy way to deploy sets of keys used for cryptographic functions. For more info
see http://www.keyczar.org/

A keyczar keyset is only ever read once, at module import time. This is to avoid
undue disk read operations when decrypting ciphertext. 
"""
import os
import conf
import keyczar.keyczar
CRYPTER = keyczar.keyczar.Crypter.Read(
    os.path.abspath(conf.get('keyczar_keyset_path')))

def encrypt(message):
    return CRYPTER.encrypt(message)

def decrypt(ciphertext):
    return CRYPTER.decrypt(ciphertext)
