#!/usr/bin/env python

# Copyright: (c) 2020, Atila Aloise de Almeida <atilaloise@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: splunk_app
short_description: Manipulate splunk apps easily
version_added: "1.0.0"
description: This module manages splunk apps
options:
    host:
        description: Splunk host where de index should be created.Defaults to localhost
        required: true
        type: str
    port:
        description: Splunk administration port. Defaults to 8089
        required: true
        type: str
    username:
        description: User with create index capabilitie. Defaults to admin
        required: true
        type: str
    password:
        description: User password.
        required: true
        type: str
    version:
        description: Splunk version.
        required: true
        type: str
    scheme:
        description: Scheme for connection. Can be http or https. Defaults to https
        required: true
        type: str
    name:
        description: The name of the index to be manipulated.
        required: true
        type: str
    template:
        description: The name of the index to be manipulated.
        required: true
        type: str
    version:
        description: The name of the index to be manipulated.
        required: true
        type: str
    visible:
        description: The name of the index to be manipulated.
        required: true
        type: str
    disabled:
        description: disable index. defaults to False
        required: false
        type: bool
    auth:
        description: Splunkbase session token for operations like install and update that require login. Use auth or session when installing or updating an app through Splunkbase.
        required: false
        type: str
    author:
        description: For apps posted to Splunkbase, use your Splunk account username. For internal apps, include your name and contact information.
        required: false
        type: str
    configured:	
        description: Custom setup complete indication: true = Custom app setup complete.false = Custom app setup not complete.
        required: false
        type: Bool
    description:
        description: Short app description also displayed below the app title in Splunk Web Launcher.
        required: false
        type: str
    explicit_appname:
        description: Custom app name. Overrides name when installing an app from a file where filename is set to true. See also filename.
        required: false
        type: str
    filename:
        description: Indicates whether to use the name value as the app source location.true indicates that name is a path to a file to install.false indicates that name is the literal app name and that the app is created from Splunkbase using a template.
        required: false
        type: bool
    label:
        description: App name displayed in Splunk Web, from five to eighty characters excluding the prefix "Splunk for".filename = false indicates that name is the literal app name and that the app is created from Splunkbase using a template.filename = true indicates that name is the URL or path to the local .tar, .tgz or .spl file. If name is the Splunkbase URL, set auth or session to authenticate the request.The app folder name cannot include spaces or special characters.
        required: false
        type: str 
    session:
        description: Login session token for installing or updating an app on Splunkbase. Alternatively, use auth.barebones - [Default] Basic app framework.sample_app - Example views and searches.Any custom app template.
        required: false
        type: str
    update:
        description: File-based update indication:true specifies that filename should be used to update an existing app. If not specified, update defaults tofalse, which indicates that filename should not be used to update an existing app.
        required: false
        type: bool
    state: 
        description: The desired state for the index. Defaults to Present
        required: true
        type: str


author:
    - Atila Aloise de Almeida (@atilaloise)
'''

EXAMPLES = r'''

    

'''

RETURN = '''
original_state:
    description: The original state of the param that was passed in
    type: str
changed_state:
    description: The output state that the module generates
    type: str
'''


import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from splunklib.client import connect
#from utils import *

def app_exists(service, name):
    return True if name in service.apps else False

def app_create(service, name, **kwargs):
    service.apps.create(name, **kwargs)

def app_update(service, name, **kwargs):
    app = service.apps[name]
    app.update(**kwargs)

def app_enable(service, name):
    app = service.apps[name]
    app.enable()

def app_disable(service, name):
    app = service.apps[name]
    app.disable()

def app_delete(service, name):
    app = service.apps[name]
    app.delete()

from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type="str", default="localhost"),
            port=dict(type="int", default="8089"),
            username=dict(type="str", default="admin"),
            password=dict(type="str", required=True, no_log=True),
            scheme=dict(type="str", choices=["http", "https"], default="https"),
            version=dict(type="str", required=True),
            name=dict(type="str", required=True),
            author=dict(type="str", required=True),
            description=dict(type="str", required=True),
            label=dict(type="str", required=True),
            app_version=dict(type="str", default="1.0.0"),
            disabled=dict(type="bool", default=False),
            template=dict(type="str",default="barebones"),
            visible=dict(type="bool", default=False),
            update=dict(type="bool", default=True),
            configured=dict(type="bool", default=True),
            auth=dict(type="str"),
            explicit_appname=dict(type="str"),
            filename=dict(type="str"),
            session=dict(type="str"),
            state=dict(type="str", choices=["present", "absent"], default="present"),
        ),
        required_if=([("state", "present", ["name", "password"])]),
        supports_check_mode=True,
    )

    result = dict(
        changed=False,
        changed_state={},
        facter={}
    )

    if module.check_mode:
        module.exit_json(**result)
    
    requested_state = module.params["state"]

    # Parameter assignments for splunk connection

    splunk_connection={}
    splunk_connection["host"] = module.params["host"]
    splunk_connection["port"] = module.params["port"]
    splunk_connection["username"] = module.params["username"]
    splunk_connection["password"] = module.params["password"]
    splunk_connection["version"] = module.params["version"]
    splunk_connection["scheme"] = module.params["scheme"]

    # Parameter assignments for app management

    app_config = {}
    app_new_config = {}
    
    # Required or default valued parameters

    name = module.params["name"]
    app_config['author'] = module.params["author"]
    app_config['visible'] = int(module.params["visible"])
    app_config['configured'] = int(module.params["configured"])
    app_config['description'] = module.params["description"]
    app_config['label'] = module.params["label"]
    app_config['update'] = module.params["update"]
    app_config['version'] = module.params["app_version"]
    app_config['template'] = module.params["template"]
    disable_app= module.params["disabled"]
    # Optional parameters

    if module.params["filename"] is not None:
        app_config['filename']  = module.params["filename"]
        
    if module.params["explicit_appname"] is not None:
        app_config['explicit_appname'] = module.params["explicit_appname"]

    if module.params["auth"] is not None:
        app_config['auth'] = module.params["auth"]

    if module.params["session"] is not None:
        app_config['session'] = module.params["session"]

    
    # Connecting to splunk
    
    service = connect(**splunk_connection)
    
    # Module Logic
    
    if requested_state == 'present':
        if not app_exists(service, name):
            app_create(service, name, **app_config)
            if disable_app:
                app_disable(service, name)
            result['changed']=True
        elif app_config:
            # remove unsuported values in update actions
            app_config.pop('update', None)
            app_config.pop('template', None)
    
            result['facter']=service.apps[name].content
            for key in app_config:
                if str(app_config[key]) != service.apps[name].content[key]:
                    app_new_config[key] = app_config[key]

            if app_new_config:
                app_update(service, name, **app_new_config)
                result['changed']=True
                result['changed_state']=app_new_config
        
        if disable_app and (disable_app != bool(int(service.apps[name].content["disabled"]))):
            app_disable(service, name)
            result['changed']=True
        elif (not disable_app) and (disable_app != bool(int(service.apps[name].content["disabled"]))):
            app_enable(service, name)
            result['changed']=True
    else:
        if app_exists(service, name):
            app_delete(service, name)
            result['changed']=True
        else:
            result['changed']=False



    module.exit_json(**result)


if __name__ == "__main__":
    main()
