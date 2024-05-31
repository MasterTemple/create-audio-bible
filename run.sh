#! /usr/bin/bash

cab use "Ephesians - Tim Conway"
cab trim

cab use "Hebrews - Tim Conway"
cab db
cab find
cab trim

cab use "Romans - Tim Conway"
cab db
cab find
cab trim

cab use "1 Peter - Sam Renihan"
cab db
cab find
cab trim

cab use "1 Thessalonians - Sam Renihan"
cab db
cab find
cab trim

cab use "1 John - Sam Renihan"
cab db
cab find
cab trim

cab create "Galatians - Sam Renihan" "Galatians" "sources/gal.txt"
cab download
cab transcribe
cab db
cab find
cab trim

cab create "Esther - Sam Renihan" "Esther" "sources/esther.txt"
cab download
cab transcribe
cab db
cab find
cab trim

cab create "Malachi - Sam Renihan" "Malachi" "sources/malachi.txt"
cab download
cab transcribe
cab db
cab find
cab trim
