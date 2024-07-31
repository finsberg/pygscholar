# Configuration

In this document we will explain how `pygscholar` is working underneath and how to configure it.

## How is it working
When you add an author to the database, `pygscholar` will add the author to a file called `authors.json` in a cache directory. By default this is set to a directory called `.pygscholar` in your home directory. However, you can also specify a different directory by setting the environment variable `PYSCHOLAR_CACHE_DIR` to the desired directory. This is convenient if you want to work with different departments. Note also that you can pass the cache directory in as an argument to most commands.

Each author will have a corresponding Google Scholar ID and in `authors.json` we simply just save a mapping between the name of the author and the Google scholar ID. Now, there will also be one file for each author where the name of the file will be the Google scholar id for the author. This file will contain author information as well as the publications for that author.
