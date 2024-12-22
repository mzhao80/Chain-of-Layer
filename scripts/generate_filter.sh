#!/bin/bash

python rank_score.py \
  --taxo_name wiki \
  --model_path google-bert/bert-base-uncased \
  --save_path ./filter/
