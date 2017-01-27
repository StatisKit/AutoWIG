##################################################################################
#                                                                                #
# AutoWIG: Automatic Wrapper and Interface Generator                             #
#                                                                                #
# Homepage: http://autowig.readthedocs.io                                        #
#                                                                                #
# Copyright (c) 2016 Pierre Fernique                                             #
#                                                                                #
# This software is distributed under the CeCILL license. You should have       #
# received a copy of the legalcode along with this work. If not, see             #
# <http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html>.                 #
#                                                                                #
# File authors: Pierre Fernique <pfernique@gmail.com> (11)                       #
#                                                                                #
##################################################################################

from _feedback import parse_errors

def comment_feedback(err, directory, asg, **kwargs):
    wrappers = parse_errors(err, directory, asg, **kwargs)
    for wrapper, rows in wrappers.iteritems():
        with open(wrapper, 'r') as filehandler:
            content = filehandler.readlines()
        for row in rows:
            if row < len(content):
                content[row - 1] = '// TODO ' + content[row - 1]
            with open(wrapper, 'w') as filehandler:
                filehandler.writelines(content)
    return hash(frozenset(wrappers))
