# -*- coding: utf-8 -*-

from pyramid.config import Configurator
from ddbmock.router.pyramid import pyramid_router

def noop(*args, **kwargs): pass

# Pyramid entry point
def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    # Insert router as '/' route. This is because all DDB URL are '/' (!)
    config.add_route('pyramid_router', '')
    config.add_view(pyramid_router, route_name='pyramid_router')

    return config.make_wsgi_app()

# Regular "over the network" connection wrapper.
def connect_boto_network(host='localhost', port=6543):
    """Connect to ddbmock launched in *server* mode via boto"""
    import boto
    from boto.regioninfo import RegionInfo
    endpoint = '{}:{}'.format(host,port)
    region = RegionInfo(name='ddbmock', endpoint=endpoint)
    return boto.connect_dynamodb(region=region, port=port, is_secure=False)

# Monkey patch magic, required for the Boto entry point
# Request hijacking Yeah !
real_boto = {}

def connect_boto_patch():
    """Connect to ddbmock as a library via boto"""
    import boto

    if real_boto:
        return boto.connect_dynamodb()

    from boto.dynamodb.layer1 import Layer1
    from router.boto import boto_router

    # Backup real functions for potential cleanup
    real_boto['Layer1.make_request'] = Layer1.make_request
    real_boto['Layer1.__init__'] = Layer1.__init__

    # Bypass network *and* authentication
    Layer1.make_request = boto_router
    Layer1.__init__ = noop

    # Just one more shortcut
    return boto.connect_dynamodb()

def clean_boto_patch():
    """Restore real boto code"""
    if real_boto:
        from boto.dynamodb.layer1 import Layer1

        Layer1.make_request = real_boto['Layer1.make_request']
        Layer1.__init__ = real_boto['Layer1.__init__']

        real_boto.clear()
