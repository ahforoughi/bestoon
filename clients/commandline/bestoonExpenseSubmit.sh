#!/bin/bash

mytoken = 1234567
BASE_URL = http://localhost:8009

curl --data "token=$mytoken&amount=$1&text=$2" $BASE_URL/submit/expense/