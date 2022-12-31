# Configuration

In this document we will explain how `pygscholar` is working underneath and how to configure it.

## How is it working
When you add an author to the database, `pygscholar` will add the author to a file called `authors.json` in a cache directory. By default this is set to a directory called `.pygscholar` in your home directory. However, you can also specify a different directory by setting the environment variable `PYSCHOLAR_CACHE_DIR` to the desired directory. This is convenient if you want to work with different departments. Note also that you can pass the cache directory in as an argument to most commands.

For the `list-new-dep-publications` command, it will also keep track of all the publications for the department in a file called `publications.json` in the cache directory. Whenever, it recognizes a publication that is not listed in this file, it will report it as a new publication.

## Set up slack bot
It is also possible to make post updates about new publications to slack. To do this you can use the command
`post-slack-new-dep-publications`. In order for this to work you need to first make sure to install the `slack_sdk`
```
pip install slack_sdk
```
and then  set up a slack bot as described at <https://github.com/slackapi/python-slack-sdk/blob/main/tutorial/01-creating-the-slack-app.md>. You need to also pass the *Bot User OAuth Access Token* to `pygscholar`. You can do this in three ways
- Setting the environment variable `SLACK_BOT_TOKEN` to the token value, or
- Creating a file called `~/.pygscholarrc` or a file inside the cache directory called `config` with the following content
    ```toml
    [SLACK_BOT_TOKEN]
    token = xoxp-xxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```
    where you swap out `xoxp-xxxxxxxxxxxxxxxxxxxxxxxxxxx` with your token
