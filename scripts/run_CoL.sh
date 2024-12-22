#!/bin/bash

python infer.py \
  --openai_key $OPENAI_API_KEY \
  --taxo_name wiki \
  --model gpt-4o-mini \
  --numofExamples 5 \
  --run True \
  --save_path_model_response ./results/taxo_ChainofLayers_filter_init/ \
  --demo_path ./demos/demo_wordnet_train/ \
  --ChainofLayers True \
  --iteratively True \
  --filter_mode lm_score_ensemble \
  --filter_model google-bert/bert-base-uncased \
  --filter_topk 10