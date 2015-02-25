# pdf-text

Extract text from a pdf into an array of text 'chunks'.  Useful for doing fuzzy parsing on structured pdf text.

Uses Mozilla's [pdf.js](http://mozilla.github.io/pdf.js/) via [pdf2json](https://github.com/modesty/pdf2json).

## install

```sh
$ npm install pdf-text
```

## use

```js
var pdfText = require('pdf-text')

var pathToPdf = __dirname + "/info.pdf"

pdfText(pathToPdf, function(err, chunks) {
  //chunks is an array of strings 
  //loosely corresponding to text objects within the pdf

  //for a more concrete example, view the test file in this repo
})

//or parse a buffer of pdf data
//this is handy when you already have the pdf in memory
//and don't want to write it to a temp file
var fs = require('fs')
var buffer = fs.readFileSync(pathToPdf)
pdfText(buffer, function(err, chunks) {

})

```

## api

#### pdfText(string pathToPdfFile, function callback(error, string[]))

Callback receives `string[]` of all the text objects within the pdf.  The array is ordered similarly to how the text appears on the page, making it possible to extract key pieces by finding them based on how they relate to other 'known' pieces of text in the page.

#### pdfText(Buffer bufferOfPdfContents, function callback(error, string[]))

Optionally pass a buffer of pdf data instead of a path to the file.

## license

The MIT License (MIT)

Copyright (c) 2013 Brian M. Carlson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

