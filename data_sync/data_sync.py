import ConfigParser
import os
import stat
from subprocess import check_output
import sys

class SyncEngineS3():
    def __init__(self, work_path=None):
        # find config file (if we need a subdirectory of where this is called, pass it in work_path)
        work_path = os.getcwd() if not work_path else os.path.join(os.getcwd(), work_path)
        self.config_path = self.find_s3data_config(work_path)

        # parse config file
        self.data_root, self.s3_data_root, self.exclude_file = self.parse_s3data()

    def find_s3data_config(self, path):
        # walk up from cwd we find a .s3data file
        while not os.path.exists(os.path.join(path, '.s3data')):
            path, removed = os.path.split(path)

            # if we don't remove anything (i.e., we reached the root) bail
            if not removed:
                raise Exception("Could not find .s3data file.")

        return os.path.join(path, '.s3data')

    def parse_s3data(self):
        config = ConfigParser.RawConfigParser()
        config.read(self.config_path)

        # required config vars
        data_root = config.get('s3data', 'data_root')
        config_directory = os.path.split(self.config_path)[0]
        data_path = os.path.join(config_directory, data_root)

        s3_data_root = config.get('s3data', 's3_data_root')

        # optional config vars
        exclude_file = None if not config.has_option('s3data', 'exclude_file') \
            else config.get('s3data', 'exclude_file')

        return data_path, s3_data_root, exclude_file
    
    def sync(self):
        print "Syncing data folder '{}' with {}".format(self.data_root, self.s3_data_root)

        # make the command
        s3_cmd = self.make_s3cmd()

        # run sync command in data folder
        return check_output(s3_cmd)

    def make_s3cmd(self):
        base = ["s3cmd", "sync"]

        # default options
        options = ["--exclude='.DS_Store'",
                   "--add-header=Expires:max-age=604800"]

        # if we need to exclude other files from syncing, this
        # should be defined
        if self.exclude_file:
            exclude_option = "--exclude-from='{}'".format(exclude_file)
            options.append(exclude_option)

        return base + options + [self.data_root, self.s3_data_root]

def main(work_path=None):
    if len(sys.argv) > 1:
        if sys.argv[1] == "install_hooks":
            install_hooks()
            return 0

    try:
        sync_engine_s3 = SyncEngineS3(work_path=work_path)
        result = sync_engine_s3.sync()

        if not result:
            result = "No files to sync."

        print result
    except Exception as e:
        print e.message

def git_hook():
    changed_files = check_output("git diff-tree -r --name-only --no-commit-id HEAD@{1} HEAD".split(" "))
    
    # get just the unique directories with changes
    changed_dirs = set()
    for c in changed_files.split("\n"):
        if "/" in c:
            changed_dirs.add(c.split("/")[0])

    # sync those directories!
    for c in changed_dirs:
        main(c)

def install_hooks():
    HOOK_FILE = """#!/usr/bin/env python
from data_sync import git_hook

if __name__ == "__main__":
    git_hook()
    """

    if not os.path.exists(".git"):
        raise Exception("install_hooks Must be called in root of git repository.")

    if os.path.exists(".git/hooks/post-merge") or os.path.exists(".git/hooks/pre-push"):
        raise Exception("post-merge or pre-push hooks already exist. Multiple hooks not supported at this time.")

    def _write_hook_file(path):
        with open(path, 'w') as f:
            f.write(HOOK_FILE)

        # make executable
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC)

    _write_hook_file(".git/hooks/post-merge")
    _write_hook_file(".git/hooks/pre-push")

    print "Successfully installed git hooks."

if __name__ == "__main__":
    main()


