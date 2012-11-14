# -*- coding: utf-8 -*-
import sys

# Just, skip this unless "--no-skip"
if '--no-skip' in sys.argv:
    import os, imp, boto, unittest
    from ddbmock import connect_boto_patch, clean_boto_patch

    # Load boto dir
    boto_dir = os.path.realpath(boto.__file__+'/../../')

    # Plug patch
    connect_boto_patch()

    # Import boto test modules, pretending they are belonging to us. see hack in tests.unit.__init__
    layer1_file, _, desc1 = imp.find_module('test_layer1', [boto_dir+'/tests/integration/dynamodb'])
    layer2_file, _, desc2 = imp.find_module('test_layer2', [boto_dir+'/tests/integration/dynamodb'])
    layer1_module = imp.load_module('test_layer1', layer1_file, boto_dir, desc1)
    layer2_module = imp.load_module('test_layer2', layer2_file, boto_dir, desc2)

    # Finally, import the tests class, that's enough to let the magic happen !
    DynamoDBLayer1Test = layer1_module.DynamoDBLayer1Test
    DynamoDBLayer2Test = layer2_module.DynamoDBLayer2Test

    # clean up
    layer1_file.close()
    layer2_file.close()
    clean_boto_patch()
else:
    print "Boto Integration tests are slow hence disabled by default, enable them with '--no-skip'"

