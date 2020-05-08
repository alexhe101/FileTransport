# FileTransport

> Transfer files over TCP

## Feature

* Send file or folder
* resume from break-point
* update existing copy
* GUI

## How it works

## client sends header

A folder is treated as multiple files in it.  
To start, client sends the file header including structure as follows:  

| name_size | name              | md5      | compress | data_size |
|-----------|-------------------|----------|----------|-----------|
| 4 bytes   | [name_size] bytes | 16 bytes | 1 byte   | 8 byte    |

* `name_size` indicates the length of the name that follows.
* `name` is the UTF-8 encoded file name, with its relative path if sent in folder, it uses the same unix seperator in header and is connverted before sending and after receiving.
* `md5` is the calculated MD5 of the original file.
* `compress` indicates weather the following `data` is compressed or not.
* `data_size` is the size of `data`(compressed size if `compress`)

## server feedback

On server side, it first read `name_size`, if `0` then the transfer process is over, else it reads all the header then sends `shift` back to client, which tells client the starting position of file and determines the length of `data` that follows.  
Here's how `shift` is determined:

1. if `[name].download` exits and `md5`==`[name].md5`, then `shift`=`[name].download`  
2. if `[name]` exits and its md5 is identical, then `shift`=`0xffffffffffffffff`
3. else `shift`=`0`

## transfer

Once client receives `shift`, it will send `data` starting from `shift`.

## Development
  
Python 3 is required.  
Tested on both Linux and Windows.
