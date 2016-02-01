import argparse
from path import path
import datetime
import subprocess
from tempfile import NamedTemporaryFile
import os
from time import mktime, strptime
from mako.template import Template
from ConfigParser import ConfigParser
from textwrap import TextWrapper
import itertools

def alea_headache():
    parser = argparse.ArgumentParser(description = 'Add license header to source files',
            epilog = 'Default values for arguments, if not precised, are read in the section \'metainfo\' of the \'metainfo.ini\' file present in the current working directory or the given meta-information file (\'metainfo\' parameter)')
    parser.add_argument('--srcdir', dest = 'srcdir', type = path,
            default = path('./src'),
            help = 'Source files directory (default set to \'./src\'')
    parser.add_argument('--scm', dest = 'scm',
            default = None,
            choices=['git'],
            help = 'Source Control Management (SCM) software')
    parser.add_argument('--name', dest = 'name',
            default = None,
            help = 'Name of the library')
    parser.add_argument('--description', dest = 'description',
            default = None,
            help = 'Short description of the library')
    parser.add_argument('--start', dest = 'start', type = int,
            default = None,
            help = 'Development starting year (default: None)')
    parser.add_argument('--end', dest = 'end', type = int,
            default = datetime.datetime.now().year,
            help = 'Development ending year (default: ' + str(datetime.datetime.now().year) + ')')
    parser.add_argument('--license', dest = 'license',
            default = None,
            choices = ['CeCill-C'],
            help = 'Library license')
    parser.add_argument('--institutes', dest = 'institutes', nargs = '*',
            default = None,
            help = 'Insitutes concerned by the library development')
    parser.add_argument('--patterns', dest = 'patterns', nargs = '*',
            default = ['*.h', '*.c', '*.hpp', '*.cpp', '*.py', '*.txt'],
            help = 'Patterns for detecting files within which a license header will be added (default: [\'*.h\', \'*.c\', \'*.hpp\', \'*.cpp\'])')
    parser.add_argument('--metainfo', dest = 'metainfo', type = path,
            default = path('./metainfo.ini'),
            help = 'Path to the meta-information file (default: \'./metainfo.ini\')')
    parser.add_argument('--config', dest = 'config', type = path,
            default = None,
            help = 'Path to the configuration file of headache (default: see headache)')
    parser.add_argument('--url', dest = 'url',
            default = None,
            help = 'Library\'s WebSite URL')
    args = parser.parse_args()
    args.srcdir = path(args.srcdir)
    metainfo = ConfigParser()
    metainfo.read(args.metainfo)
    if args.scm is None:
        try:
            args.scm = metainfo.get('metainfo', 'scm')
        except:
            args.scm = 'git'
    if args.name is None:
        args.name = metainfo.get('metainfo', 'name')
    if args.description is None:
        args.description = metainfo.get('metainfo', 'description')
    if args.license is None:
        args.license = 'CeCill-C'
    if args.institutes is None:
        try:
            args.institutes = [institute.strip() for institute in metainfo.get('metainfo', 'institutes').split(',')]
        except:
            pass
    if args.url is None:
        try:
            args.url = metainfo.get('metainfo', 'url')
        except:
            pass
    if args.config is None:
        with NamedTemporaryFile(delete=False) as filehandler:
            filehandler.write("""\
# C source
| \".*\\\\.[ch]\"    -> frame open:\"/*\" line:\"*\" close:\"*/\"
# C++ source
| \".*\\\\.[ch]pp\"    -> frame open:\"/*\" line:\"*\" close:\"*/\"
# Python source
| \".*\\\\.py\"    -> frame open:\"#\" line:\"#\" close:\"#\"
# Misc
| \".*\\\\.txt\"   -> frame open:\"*\"  line:\"*\" close:\"*\"
""")
            filehandler.close()
            args.config = filehandler.name
    if args.scm == 'git':
        headache = GitHeadache(name = args.name, description = args.description,
                institutes = args.institutes, license = args.license, url = args.url,
                wrapper = TextWrapper(break_long_words=False, break_on_hyphens=False, subsequent_indent='  '),
                config = args.config)
    else:
        raise ValueError('\'scm\' parameter')
    committed = True
    for pattern in args.patterns:
        for filepath in args.srcdir.walkfiles(pattern):
            if not len(subprocess.check_output(['git', 'diff', './' + str(filepath.relpath(filepath.parent))], cwd=str(filepath.parent.abspath()))) == 0:
                raise IOError('File changes not committed')
    for pattern in args.patterns:
        for filepath in args.srcdir.walkfiles(pattern):
            headache(filepath)
    if args.scm == 'git':
        subprocess.call(['git', 'commit', '--amend', '--no-edit'])
    else:
        raise ValueError('\'scm\' parameter')
    if not args.config is None:
        os.unlink(args.config)

class GitHeadache(object):

    header = Template(r"""\
% if name:
${name}\
% endif
% if description:
: ${description}
% endif

% if institutes:
Copyright \
    % if start:
${start} \
        % if end and not end == start:
 - \
        % endif
    % endif
    % if end and not start or end and not end == start:
${end} \
    % endif
${' - '.join(institutes)}
% endif

% if authors:
    % if len(authors) == 1:
File author: \
    % else:
File authors: \
    % endif
${"\n              ".join(author + " <" + mail + ">" if mail else author for author, mail in authors)}

% endif
% if license:
Distributed under the ${license} license.
See accompanying file LICENSE.txt
% endif

% if url:
WebSite: ${url}
% endif

% if dated or entitled or authored:
Last commit\
    % if entitled:
 entitled "${entitled}"\
    % endif
    % if authored:
 authored by ${authored}\
    % endif
    % if dated:
 ${dated}\
    % endif
.
% endif
""")

    def __init__(self, name=None, description=None, institutes=None, license=None, url=None, start=datetime.MAXYEAR, end=datetime.MINYEAR, override=True, wrapper=None, config=None):
        self.name = name
        self.description = description
        self.institutes = institutes
        self.license = license
        self.url = url
        self.start = start
        self.end = end
        self.override = override
        self.wrapper = wrapper
        self.config = config

    def __call__(self, filepath):
        if not isinstance(filepath, path):
            filepath = path(filepath)
        authors = dict()
        start = self.start
        end = self.end
        for commit in reversed(subprocess.check_output(['git', 'log', '--date=short', '--format=["%aN", "%aE", "%ad"]', './' + str(filepath.relpath(filepath.parent))], cwd=str(filepath.parent.abspath())).splitlines()):
            author, mail, date = eval(commit)
            if not author in authors:
                authors[author] = dict(mail = mail, commits = 1)
            else:
                authors[author]['commits'] += 1
            if self.override:
                date = datetime.datetime.fromtimestamp(mktime(strptime(date, '%Y-%M-%d')))
                if date.year < start:
                    start = date.year
                if date.year > end:
                    end = date.year
        authors = reversed(sorted(authors.iteritems(), key = lambda item: item[1]['commits']))
        authors = [(author, properties['mail']) for author, properties in authors]
        authored, dated, entitled = None, None, None
        try:
            authored, dated, entitled = eval(subprocess.check_output(['git', 'log', '-1', '--date=short', '--format=["%aN", "%ad", "%s"]', './' + str(filepath.relpath(filepath.parent))], cwd=str(filepath.parent.abspath())).splitlines()[-1])
        except:
            pass
        header = ""
        paragraph = ""
        if self.name:
            paragraph += str(self.name)
            if self.description:
                paragraph += ": "
        if self.description:
            paragraph += str(self.description)
        if paragraph:
            if self.wrapper:
                header += '\n'.join(self.wrapper.wrap(paragraph))
            else:
                header += paragraph
            header += '\n\n'
            paragraph = ""
        if self.institutes:
            paragraph += "Copyright"
            if not start == datetime.MAXYEAR:
                paragraph += " " + str(start)
            if not start == end and not end == datetime.MINYEAR:
                paragraph += " - " + str(end)
            paragraph += " " + ' - '.join(self.institutes)
        if paragraph:
            if self.wrapper:
                header += '\n'.join(self.wrapper.wrap(paragraph))
            else:
                header += paragraph
            header += '\n\n'
            paragraph = ""
        if not len(authors) == 0:
            if len(authors) == 1:
                paragraph += "File author: " + str(authors[0][0]) + ' <' + str(authors[0][1]) + '>'
                if self.wrapper:
                    header += '\n'.join(self.wrapper.wrap(paragraph))
                else:
                    header += paragraph
                header += '\n\n'
                paragraph = ""
            else:
                paragraph += "File authors: " + ("\n" + " "*14).join(author + " <" + mail + ">" if mail else author for author, mail in authors)
                if self.wrapper:
                    header += '\n'.join(itertools.chain(*[self.wrapper.wrap(line) for line in paragraph.splitlines()]))
                else:
                    header += paragraph
                header += '\n\n'
                paragraph = ""
        if self.license:
            paragraph = "Distributed under the " + self.license + " license. See accompanying file LICENSE.txt"
        if paragraph:
            if self.wrapper:
                header += '\n'.join(self.wrapper.wrap(paragraph))
            else:
                header += paragraph
            header += '\n\n'
            paragraph = ""
        if dated or entitled or authored:
            paragraph += "Last commit"
            if entitled:
                paragraph += ' "' + entitled + '"'
            if authored:
                paragraph += ' authored by ' + authored
            if dated:
                paragraph += ' the ' + dated
        if paragraph:
            if self.wrapper:
                header += '\n'.join(self.wrapper.wrap(paragraph))
            else:
                header += paragraph
            header += '\n\n'
            paragraph = ""
        with NamedTemporaryFile(delete=False) as filehandler:
            filehandler.write(header.strip())
            filehandler.close()
            subprocess.call(['headache', '-h', filehandler.name] + ['-c', self.config] * (self.config is not None) + ['./' + str(filepath.relpath())])
            subprocess.call(['git', 'add', './' + str(filepath.relpath(filepath.parent))], cwd=str(filepath.parent.abspath()))
            #subprocess.call(['git', 'commit', '-m', '"generate license headers"'])
            os.unlink(filehandler.name)
        return ('git', 'commit', '--amend', '--no-edit')
