S3 Data Folder Syncing Tool
=========

Enables `git` integration with `s3cmd` to keep a data folder in sync as changes are made in a repository.

# Prereqs

 1. Python 2.7
 2. [`s3cmd`](http://s3tools.org/) installed and configured

# Installation

 1. `git clone` the repo
 2. `cd` into the repo
 3. `pip install -e .`: this will install the package in editable mode so git pulling updates will be used next time you call the module.

 # Data Project Repository Structure

Repository must have a structure where the `.s3data` configuration file is in a sub-project directly below the root of the git working tree. I.e., `git_root/<sub_project>/.s3data`. You can have multiple sub-projects per single git repository. For example:

```
git_root/
    | ---- sub_project
        | ---- data_folder      # this folder should be in .gitignore
        | ---- .s3data          # config for data_folder
        ...
    | ---- sub_project2         # another project
        | ---- data_folder2     # this folder should be in .gitignore
        | ---- .s3data          # config for data_folder2
```

# Options for `.s3data` file

```
[s3data]

# should be relative to this configuration file
data_root=data

# must end with trailing slash; if spaces, enclose entire path in quotes
s3_data_root=s3://<FOLDER_TO_SYNC_WITH_DATA>/

# OPTIONAL (use .gitignore conventions)
#exclude_file=<PATH_TO_FILE_WITH_DATA_NOT_TO_SYNC>
```

# Using `data-sync-s3`

You can use `data-sync-s3` from the commandline anywhere where there is an `.s3data` file above your current directory in the working tree. Run this any time that you please.

However, the real goal is not to disrupt your current `git` workflow with additional commands. You can trigger `data-sync-s3` using `git` hooks.

On `git-push` or `git-pull`, we will look at the changes. For every unique sub-project folder in the commit, we will try to sync the data on S3.

To turn on the git hooks, simply:

 1. Navigate to the root of the repo
 2. run `data-sync-s3 install_hooks`
